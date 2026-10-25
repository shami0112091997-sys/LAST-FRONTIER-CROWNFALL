#!/usr/bin/env python3
"""M131: source-only, read-only Unreal/Android integrity gate.

Examines tracked repository files. NEVER reads JKS, runs tools, downloads
dependencies, signs, builds, contacts a device, or accesses Google Play.
A source PASS is NOT proof that versionCode 218 launched successfully.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

PACKAGE_TAG = bytes.fromhex("c1832a9e")
ANDROID_SECTION = "[/script/androidruntimesettings.androidruntimesettings]"
PAD_SECTION = "[/script/googlepadeditor.googlepadruntimesettings]"


def text_file(path: Path) -> str | None:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        return None
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return None


def unique_ini_value(content: str, section: str, name: str) -> str | None:
    active = False
    values = []
    for line in content.splitlines():
        value = line.strip()
        if value.startswith("[") and value.endswith("]"):
            active = value.casefold() == section
        elif active and re.match(r"^" + re.escape(name) + r"\s*=", value, re.I):
            values.append(value.split("=", 1)[1].strip())
    return values[0] if len(values) == 1 else None


def audit(repo: Path, play_version: int = 218) -> tuple[dict[str, str], list[str], list[str]]:
    """Return safe-to-print statuses, hard structural defects, review-only issues."""
    root = repo / "LastFrontier_Build_001"
    checks: dict[str, str] = {}
    errors: list[str] = []
    reviews: list[str] = []

    def status(name: str, condition: bool, on_fail: str = "error") -> None:
        checks[name] = "PASS" if condition else "REVIEW" if on_fail == "review" else "FAIL"
        if not condition:
            (reviews if on_fail == "review" else errors).append(name)

    proj_raw = text_file(root / "LastFrontier.uproject")
    engine = text_file(root / "Config/DefaultEngine.ini")
    build = text_file(root / "Source/LastFrontier/LastFrontier.Build.cs")
    enemy = text_file(root / "Source/LastFrontier/Private/Enemy/LFEnemy.cpp")
    world = text_file(root / "Source/LastFrontier/Private/World/LFWorldDirector.cpp")
    hud = text_file(root / "Source/LastFrontier/Private/UI/LFHUD.cpp")
    hud_header = text_file(root / "Source/LastFrontier/Public/UI/LFHUD.h")
    legacy = text_file(repo / "CROWNFALL_Stronghold_Android/app/build.gradle.kts")
    legacy_workflow = text_file(repo / ".github/workflows/crownfall-android-build.yml")
    release_gate = text_file(root / "Scripts/M68_Staged_Android_Build.sh")

    project = None
    if proj_raw:
        try:
            project = json.loads(proj_raw)
        except (TypeError, ValueError):
            pass
    status("UPROJECT_VALID", isinstance(project, dict))
    status("UNREAL_ENGINE_58", bool(project and str(project.get("EngineAssociation")) == "5.8"))
    plugins = project.get("Plugins", []) if isinstance(project, dict) else []
    enabled_pad = (isinstance(plugins, list)
                   and len([p for p in plugins if isinstance(p, dict)
                            and p.get("Name") == "GooglePAD" and p.get("Enabled") is True]) == 1)
    status("GOOGLEPAD_DESCRIPTOR", enabled_pad)
    status("ANDROID_CONFIG_PRESENT", engine is not None)
    if engine is not None:
        status("ANDROID_PACKAGE", unique_ini_value(engine, ANDROID_SECTION, "PackageName")
               == "com.crownfall.stronghold")
        status("GOOGLEPAD_RUNTIME_ENABLED", (unique_ini_value(engine, PAD_SECTION, "bEnablePlugin") or "").lower() == "true")
        status("PACKAGE_DATA_OUTSIDE_APK", (unique_ini_value(engine, ANDROID_SECTION, "bPackageDataInsideApk") or "").lower() == "false")
        status("ANDROID_AAB", (unique_ini_value(engine, ANDROID_SECTION, "bEnableBundle") or "").lower() == "true")
        version = unique_ini_value(engine, ANDROID_SECTION, "StoreVersion")
        status("SOURCE_VERSION_NUMERIC", bool(version and version.isdecimal()))
        status("SOURCE_VERSION_EQUALS_PLAY",
               bool(version and version.isdecimal() and int(version) == play_version), "review")
        target = unique_ini_value(engine, ANDROID_SECTION, "TargetSDKVersion")
        status("API36_OUTSIDE_UE58_RECOMMENDED35", target != "36", "review")

    map_file = root / "Content/Maps/TestMap.umap"
    try:
        ok_map = False
        if not map_file.is_symlink() and map_file.is_file() and map_file.stat().st_size >= 32:
            with map_file.open("rb") as stream:
                ok_map = stream.read(4) == PACKAGE_TAG
    except OSError:
        ok_map = False
    status("UNREAL_MAP_HEADER_PRESENT", ok_map)  # Not a load/cook validation.

    status("AI_CONTROLLER_FOR_SPAWNED_ENEMIES", bool(enemy
           and "AIControllerClass = AAIController::StaticClass();" in enemy
           and "AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;" in enemy
           and build and '"AIModule"' in build))
    status("HUD_QUERY_THROTTLED", bool(hud and hud_header
           and "LastEnemyCountRefreshSeconds" in hud
           and "CachedEnemyCount" in hud_header
           and ">= 0.25f" in hud))
    status("ANDROID_STARTUP_STAGED", bool(world
           and "SetTimerForNextTick" in world and "#if PLATFORM_ANDROID" in world
           and "BuildNextStage()" in world))
    status("RELEASE_GATE_EXCLUDES_218", bool(release_gate
           and "NEXT > 218" in release_gate))

    same_id = bool(legacy and '"com.crownfall.stronghold"' in legacy)
    status("LEGACY_SAME_PACKAGE_ID", not same_id, "review")
    wrong_workflow = bool(legacy_workflow and "working-directory: CROWNFALL_Stronghold_Android" in legacy_workflow)
    status("LEGACY_WEBVIEW_WORKFLOW", not wrong_workflow, "review")
    if legacy_workflow:
        status("LEGACY_SIGNING_SECRETS_NOT_IN_GITHUB_ENV",
               "CROWNFALL_KEYSTORE_PASSWORD=$STORE_PASSWORD" not in legacy_workflow
               and "CROWNFALL_KEY_PASSWORD=$KEY_PASSWORD" not in legacy_workflow)

    return checks, errors, reviews


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--play-version-code", type=int, default=218)
    args = parser.parse_args()
    if args.play_version_code < 1:
        print("M131_INPUT=INVALID"); return 2
    checks, errors, reviews = audit(args.repo, args.play_version_code)
    print("M131_MODE=REPOSITORY_SOURCE_READ_ONLY")
    for name, result in sorted(checks.items()):
        print(f"M131_{name}={result}")
    print(f"M131_STRUCTURAL_ERRORS={len(errors)}")
    print(f"M131_REVIEW_ONLY={len(reviews)}")
    print("M131_AAB_218_RUNTIME=NOT_INSPECTED")
    print("M131_BUILD_COOK_SIGN_PUBLISH=NOT_PERFORMED")
    print("M131_CRASH_CAUSE=UNCONFIRMED")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
