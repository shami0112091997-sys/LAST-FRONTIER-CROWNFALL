#!/usr/bin/env python3
"""M136: Stage an isolated UE5.8 project for rebuilding the broken TestMap.

Only 'prepare' changes files, exclusively inside --sandbox; source checkout,
signed bundles, Cloud VM and Play are never changed. 'finalize' verifies that
the real UE Editor generated a *different* map and restores project settings.
NO Unreal Engine is included or executed by this Python script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat
import sys

PROJECT = "LastFrontier_Build_001"
MAP = Path("Content/Maps/TestMap.umap")
DESCRIPTOR = Path("LastFrontier.uproject")
CONFIG = Path("Config/DefaultEngine.ini")
BAD_OID = "965b78fc071c21412f966b70712eb30724799c20"
MAGIC = bytes.fromhex("c1832a9e")
# M137: only compile-time C++ files and known non-secret configs are
# necessary for the minimal M60 recovery. Never recursively copy a VM project:
# doing so can follow symlinks into credentials or leak JKS under other names.
SAFE_SOURCE_SUFFIXES = {".cpp", ".h", ".cs", ".inl", ".ush", ".usf"}
SAFE_CONFIG_NAMES = {
    "DefaultEngine.ini", "DefaultGame.ini", "DefaultInput.ini",
    "DefaultScalability.ini", "DefaultDeviceProfiles.ini",
}
SENSITIVE_INI_KEY = re.compile(
    r"(?im)^\\s*[^;#\\s=]*"
    r"(?:password|keystore|keyalias|privatekey|clientsecret|accesskey|auth[_-]?token)"
    r"[^=\\n]*=",
)


def validate_minimal_source(project: Path) -> str | None:
    if not project.is_dir() or project.is_symlink():
        return "BLOCKED_UNSAFE_PROJECT_DIRECTORY"
    source = project / "Source"
    if not source.is_dir() or source.is_symlink():
        return "BLOCKED_MISSING_SOURCE_DIRECTORY"
    for p in project.rglob("*"):
        if p.is_symlink():
            return "BLOCKED_SYMLINK_IN_SOURCE_PROJECT"
    source_files = [p for p in source.rglob("*") if p.is_file()]
    if not source_files or any(p.suffix.lower() not in SAFE_SOURCE_SUFFIXES for p in source_files):
        return "BLOCKED_NON_CODE_SOURCE_ARTIFACT"
    cfg = project / CONFIG
    try:
        ini = cfg.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return "BLOCKED_DEFAULTENGINE_UNREADABLE"
    if SENSITIVE_INI_KEY.search(ini):
        return "BLOCKED_SIGNING_OR_SECRET_CONFIG_KEY"
    return None


def copy_minimal_source(project: Path, dest: Path) -> None:
    """Only copy explicit project inputs needed for the first-playable map."""
    dest.mkdir(parents=True, exist_ok=False)
    shutil.copy2(project / DESCRIPTOR, dest / DESCRIPTOR)
    shutil.copytree(project / "Source", dest / "Source", symlinks=True)
    (dest / "Config").mkdir()
    for name in SAFE_CONFIG_NAMES:
        cfg = project / "Config" / name
        if cfg.is_file():
            shutil.copy2(cfg, dest / "Config" / name)
    source_map = project / MAP
    (dest / MAP.parent).mkdir(parents=True)
    shutil.copy2(source_map, dest / MAP)
    script = project / "Scripts/M136_Create_TestMap_In_Unreal.py"
    if not script.is_file():
        raise ValueError("EDITOR_SCRIPT_MISSING")
    (dest / "Scripts").mkdir()
    shutil.copy2(script, dest / "Scripts" / script.name)


def safe_file(path: Path, max_size: int = 256_000_000) -> bool:
    try:
        f = path.lstat()
        return stat.S_ISREG(f.st_mode) and 32 <= f.st_size <= max_size
    except OSError:
        return False


def git_oid(path: Path) -> tuple[str, bytes]:
    if not safe_file(path):
        raise ValueError("MAP_FILE_NOT_REGULAR_OR_NOT_PRESENT")
    n = path.stat().st_size
    digest = hashlib.sha1(b"blob " + str(n).encode("ascii") + b"\0")
    with path.open("rb") as reader:
        magic = reader.read(4)
        digest.update(magic)
        for data in iter(lambda: reader.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest(), magic


def map_for(root: Path) -> Path:
    return root / PROJECT / MAP


def prepare(repo: Path, sandbox: Path) -> tuple[str, int]:
    repo = repo.resolve(strict=True)
    sandbox = sandbox.resolve(strict=False)
    if sandbox.exists() or sandbox == repo or sandbox.is_relative_to(repo) or repo.is_relative_to(sandbox):
        return "BLOCKED_SANDBOX_NOT_NEW_OR_NOT_ISOLATED", 2
    original = map_for(repo)
    try:
        oid, magic = git_oid(original)
    except ValueError:
        return "BLOCKED_SOURCE_MAP_NOT_READABLE", 2
    if oid != BAD_OID or magic != MAGIC:
        return "BLOCKED_SOURCE_MAP_NOT_THE_KNOWN_BAD_M60_BLOB", 2
    src = repo / PROJECT
    if not (src / DESCRIPTOR).is_file() or not (src / CONFIG).is_file():
        return "BLOCKED_INCOMPLETE_UNREAL_PROJECT", 2
    issue = validate_minimal_source(src)
    if issue:
        return issue, 2

    # Copy ONLY explicitly permitted inputs to a new workspace.
    # No unrelated Content, secrets, binaries, generated assets or symlinks.
    try:
        sandbox.mkdir(parents=True, exist_ok=False)
        copy_minimal_source(src, sandbox / PROJECT)
        dst = sandbox / PROJECT
        quarantine = sandbox / "M136_Quarantine"
        quarantine.mkdir(parents=True, exist_ok=True)
        copied_bad = dst / MAP
        qmap = quarantine / "TestMap_M60_KNOWN_BAD_DO_NOT_USE.umap"
        shutil.move(str(copied_bad), str(qmap))
        if git_oid(qmap)[0] != BAD_OID:
            return "BLOCKED_QUARANTINED_BLOB_MISMATCH", 2

        project_file = dst / DESCRIPTOR
        config_file = dst / CONFIG
        descriptor_bytes = project_file.read_bytes()
        config_bytes = config_file.read_bytes()
        (quarantine / "OriginalLastFrontier.uproject").write_bytes(descriptor_bytes)
        (quarantine / "OriginalDefaultEngine.ini").write_bytes(config_bytes)

        proj = json.loads(descriptor_bytes.decode("utf-8-sig"))
        if not isinstance(proj, dict) or proj.get("EngineAssociation") != "5.8":
            return "BLOCKED_PROJECT_ENGINE_NOT_58", 2
        plugins = proj.setdefault("Plugins", [])
        if not isinstance(plugins, list):
            return "BLOCKED_BAD_PLUGIN_STRUCTURE", 2
        for name in ("PythonScriptPlugin", "EditorScriptingUtilities"):
            matches = [p for p in plugins if isinstance(p, dict) and p.get("Name") == name]
            if len(matches) > 1:
                return "BLOCKED_DUPLICATE_EDITOR_PLUGIN", 2
            if matches:
                matches[0]["Enabled"] = True
            else:
                plugins.append({"Name": name, "Enabled": True})
        project_file.write_text(json.dumps(proj, indent=2) + "\n", encoding="utf-8")

        ini = config_bytes.decode("utf-8-sig")
        expected = [
            "GameDefaultMap=/Game/Maps/TestMap",
            "EditorStartupMap=/Game/Maps/TestMap",
        ]
        if any(ini.count(x) != 1 for x in expected):
            return "BLOCKED_UNEXPECTED_MAP_CONFIG", 2
        for field in ("GameDefaultMap", "EditorStartupMap"):
            ini = ini.replace(field + "=/Game/Maps/TestMap",
                              field + "=/Engine/Maps/Entry")
        config_file.write_text(ini, encoding="utf-8")
        # Avoid any appearance that Python AST checks equal an Editor cook.
        return "SANDBOX_PREPARED_EDITOR_MAP_NOT_YET_CREATED", 0
    except (OSError, ValueError, json.JSONDecodeError, UnicodeError, shutil.Error):
        return "BLOCKED_SANDBOX_PREPARATION_FAILED", 2


def finalize(sandbox: Path, editor_log: Path) -> tuple[str, int]:
    root = sandbox.resolve(strict=True)
    src = root / PROJECT
    q = root / "M136_Quarantine"
    try:
        if not safe_file(editor_log, 20_000_000):
            return "BLOCKED_NO_REAL_UNREAL_EDITOR_LOG", 2
        if "CROWNFALL_M136_UE_LEVEL_GENERATED=PASS" not in editor_log.read_text(errors="replace"):
            return "BLOCKED_NO_UNREAL_MAP_GENERATION_MARKER", 2
        oid, magic = git_oid(src / MAP)
        if oid == BAD_OID or magic != MAGIC:
            return "BLOCKED_MAP_NOT_NEW_UNREAL_PACKAGE", 2
        project_original = (q / "OriginalLastFrontier.uproject").read_bytes()
        config_original = (q / "OriginalDefaultEngine.ini").read_bytes()
        (src / DESCRIPTOR).write_bytes(project_original)
        (src / CONFIG).write_bytes(config_original)
        if (src / DESCRIPTOR).read_bytes() != project_original:
            return "BLOCKED_DESCRIPTOR_RESTORE_FAILED", 2
        if (src / CONFIG).read_bytes() != config_original:
            return "BLOCKED_CONFIG_RESTORE_FAILED", 2
        return "NEW_MAP_PRESENT_SETTINGS_RESTORED_REQUIRES_UE_LOAD_COOK", 0
    except (OSError, ValueError, UnicodeError):
        return "BLOCKED_FINALIZE_MISSING_INPUTS", 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    cmd = parser.add_subparsers(dest="cmd", required=True)
    prep = cmd.add_parser("prepare")
    prep.add_argument("--repo", required=True, type=Path)
    prep.add_argument("--sandbox", required=True, type=Path)
    finish = cmd.add_parser("finalize")
    finish.add_argument("--sandbox", required=True, type=Path)
    finish.add_argument("--editor-log", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.cmd == "prepare":
        status, rc = prepare(args.repo, args.sandbox)
    else:
        status, rc = finalize(args.sandbox, args.editor_log)
    print(f"M136_MAP_RECOVERY={status}")
    print("M136_UNREAL_ENGINE_EXECUTED_BY_THIS_SCRIPT=NO")
    print("M136_ORIGINAL_PROJECT_MODIFIED=NO")
    print("M136_ANDROID_BUILD_OR_PLAY_UPLOAD=NO")
    return rc


if __name__ == "__main__":
    sys.exit(main())
