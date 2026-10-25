#!/usr/bin/env python3
"""Synthetic regression tests for the read-only M131 repository gate.

Tests use ONLY tempfile fixtures, never the Play release, VM, or private keys.
Run locally: python3 -m unittest discover -s LastFrontier_Build_001/Scripts -p 'test_M131_*.py' -v
"""
import tempfile
import unittest
from pathlib import Path

from M131_Unreal_Repo_Integrity_ReadOnly import audit


class RepoGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="m131-fixture-")
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)

        def write(path, content):
            p = self.repo / path
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                p.write_bytes(content)
            else:
                p.write_text(content, encoding="utf-8")
        self.write = write
        self.write("LastFrontier_Build_001/LastFrontier.uproject",
                   '{"EngineAssociation":"5.8","Plugins":[{"Name":"GooglePAD","Enabled":true}]}')
        self.config = ("[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]\n"
                       "PackageName=com.crownfall.stronghold\nStoreVersion=215\n"
                       "TargetSDKVersion=36\nbPackageDataInsideApk=False\n"
                       "bEnableBundle=True\n"
                       "[/Script/GooglePADEditor.GooglePADRuntimeSettings]\n"
                       "bEnablePlugin=True\n")
        self.write("LastFrontier_Build_001/Config/DefaultEngine.ini", self.config)
        self.write("LastFrontier_Build_001/Content/Maps/TestMap.umap",
                   bytes.fromhex("c1832a9e") + b"\0" * 60)
        self.write("LastFrontier_Build_001/Source/LastFrontier/LastFrontier.Build.cs", '"AIModule"')
        self.write("LastFrontier_Build_001/Source/LastFrontier/Private/Enemy/LFEnemy.cpp",
                   "AIControllerClass = AAIController::StaticClass();\n"
                   "AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;\n")
        self.write("LastFrontier_Build_001/Source/LastFrontier/Private/UI/LFHUD.cpp",
                   "LastEnemyCountRefreshSeconds\nNow - LastEnemyCountRefreshSeconds >= 0.25f")
        self.write("LastFrontier_Build_001/Source/LastFrontier/Public/UI/LFHUD.h",
                   "CachedEnemyCount")
        self.write("LastFrontier_Build_001/Source/LastFrontier/Private/World/LFWorldDirector.cpp",
                   "#if PLATFORM_ANDROID\nSetTimerForNextTick\nBuildNextStage()")
        self.write("LastFrontier_Build_001/Scripts/M68_Staged_Android_Build.sh",
                   "(( NEXT > MAX && NEXT > 218 ))")
        self.write("LastFrontier_Build_001/Source/LastFrontier/Private/Core/LFGameInstance.cpp",
                   "CROWNFALL_BOOT_GAMEINSTANCE_INIT=M131")
        self.write("LastFrontier_Build_001/Source/LastFrontier/Private/Core/LFGameMode.cpp",
                   "CROWNFALL_BOOT_GAMEMODE_BEGINPLAY=M131")
        self.write("CROWNFALL_Stronghold_Android/app/build.gradle.kts",
                   'applicationId = "com.crownfall.stronghold"')
        self.write(".github/workflows/crownfall-android-build.yml",
                   "name: LEGACY WebView\nworking-directory: CROWNFALL_Stronghold_Android\n")

    def test_structural_fixture_passes_but_flags_provenance(self):
        checks, errors, reviews = audit(self.repo)
        self.assertFalse(errors)
        self.assertEqual(checks["AI_CONTROLLER_FOR_SPAWNED_ENEMIES"], "PASS")
        self.assertEqual(checks["SOURCE_VERSION_EQUALS_PLAY"], "REVIEW")
        self.assertIn("LEGACY_WEBVIEW_WORKFLOW", reviews)
        self.assertIn("API36_OUTSIDE_UE58_RECOMMENDED35", reviews)

    def test_a_matching_version_removes_version_mismatch_warning(self):
        self.write("LastFrontier_Build_001/Config/DefaultEngine.ini",
                   self.config.replace("StoreVersion=215", "StoreVersion=218"))
        checks, errors, reviews = audit(self.repo)
        self.assertFalse(errors)
        self.assertEqual(checks["SOURCE_VERSION_EQUALS_PLAY"], "PASS")
        self.assertNotIn("SOURCE_VERSION_EQUALS_PLAY", reviews)

    def test_missing_ai_controller_blocks_source_gate(self):
        self.write("LastFrontier_Build_001/Source/LastFrontier/Private/Enemy/LFEnemy.cpp",
                   "void ALFEnemy::Tick(float DeltaSeconds) {}")
        checks, errors, _ = audit(self.repo)
        self.assertIn("AI_CONTROLLER_FOR_SPAWNED_ENEMIES", errors)
        self.assertEqual(checks["AI_CONTROLLER_FOR_SPAWNED_ENEMIES"], "FAIL")

    def test_corrupt_map_header_is_rejected(self):
        self.write("LastFrontier_Build_001/Content/Maps/TestMap.umap", b"bad!" + b"\0" * 60)
        _, errors, _ = audit(self.repo)
        self.assertIn("UNREAL_MAP_HEADER_PRESENT", errors)

    def test_duplicate_ini_setting_is_not_silently_accepted(self):
        self.write("LastFrontier_Build_001/Config/DefaultEngine.ini",
                   self.config.replace("bPackageDataInsideApk=False",
                                       "bPackageDataInsideApk=False\nbPackageDataInsideApk=False"))
        _, errors, _ = audit(self.repo)
        self.assertIn("PACKAGE_DATA_OUTSIDE_APK", errors)


if __name__ == "__main__":
    unittest.main()
