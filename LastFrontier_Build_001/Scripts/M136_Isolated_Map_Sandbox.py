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
IGNORE = shutil.ignore_patterns(
    "Saved", "Intermediate", "Binaries", "DerivedDataCache", "__pycache__",
    ".git", "*.jks", "*.keystore", "*.aab", "*.apk", "*.pem", "*.p12",
)


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

    # Copy to a *new* workspace, never alter repo/Content/Maps or a Cloud VM.
    try:
        shutil.copytree(src, sandbox / PROJECT, ignore=IGNORE)
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
