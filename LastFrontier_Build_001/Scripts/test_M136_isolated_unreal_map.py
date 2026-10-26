#!/usr/bin/env python3
"""Offline synthetic tests for M136 sandbox, no Unreal binaries or real VM."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import M136_Isolated_Map_Sandbox as m

GAME_INI = (
    "[/Script/EngineSettings.GameMapsSettings]\n"
    "GameDefaultMap=/Game/Maps/TestMap\n"
    "EditorStartupMap=/Game/Maps/TestMap\n"
    "[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]\n"
    "PackageName=com.crownfall.stronghold\nStoreVersion=215\n"
)
DESCRIPTOR = {
    "FileVersion": 3,
    "EngineAssociation": "5.8",
    "DisableEnginePluginsByDefault": True,
    "Plugins": [{"Name": "GooglePAD", "Enabled": True}],
}


class M136IsolatedMapTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="m136_offline_")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.repo = self.root / "repo"
        self.sandbox = self.root / "sandbox"
        self.project = self.repo / m.PROJECT
        (self.project / m.MAP.parent).mkdir(parents=True)
        (self.project / m.DESCRIPTOR).write_text(json.dumps(DESCRIPTOR))
        (self.project / m.CONFIG).parent.mkdir(parents=True)
        (self.project / m.CONFIG).write_text(GAME_INI)
        (self.project / "Source/LastFrontier").mkdir(parents=True)
        (self.project / "Source/LastFrontier/LastFrontier.Build.cs").write_text(
            "using UnrealBuildTool; // synthetic fixture only"
        )
        (self.project / "Scripts").mkdir(parents=True)
        (self.project / "Scripts/M136_Create_TestMap_In_Unreal.py").write_text(
            Path(__file__).with_name("M136_Create_TestMap_In_Unreal.py").read_text()
        )
        self.fake_map = m.MAGIC + b"intentionally_corrupt_fixture" + b"0" * 64
        (self.project / m.MAP).write_bytes(self.fake_map)
        self.oid = hashlib.sha1(
            b"blob " + str(len(self.fake_map)).encode("ascii")
            + b"\0" + self.fake_map
        ).hexdigest()

    def prepare(self):
        with patch.object(m, "BAD_OID", self.oid):
            return m.prepare(self.repo, self.sandbox)

    def test_known_bad_map_is_quarantined_only_in_new_sandbox(self):
        self.assertEqual(self.prepare(),
                         ("SANDBOX_PREPARED_EDITOR_MAP_NOT_YET_CREATED", 0))
        self.assertEqual((self.project / m.MAP).read_bytes(), self.fake_map)
        self.assertFalse((self.sandbox / m.PROJECT / m.MAP).exists())
        self.assertEqual(
            (self.sandbox / "M136_Quarantine/TestMap_M60_KNOWN_BAD_DO_NOT_USE.umap").read_bytes(),
            self.fake_map,
        )

    def test_isolated_copy_enables_editor_plugins_temporarily(self):
        self.prepare()
        dst = self.sandbox / m.PROJECT
        descriptor = json.loads((dst / m.DESCRIPTOR).read_text())
        enabled = [x["Name"] for x in descriptor["Plugins"] if x.get("Enabled")]
        self.assertIn("PythonScriptPlugin", enabled)
        self.assertIn("EditorScriptingUtilities", enabled)
        self.assertIn("GooglePAD", enabled)
        config = (dst / m.CONFIG).read_text()
        self.assertIn("EditorStartupMap=/Engine/Maps/Entry", config)
        self.assertIn("GameDefaultMap=/Engine/Maps/Entry", config)
        self.assertIn("EditorStartupMap=/Game/Maps/TestMap", (self.project / m.CONFIG).read_text())

    def test_unknown_original_map_is_never_replaced(self):
        self.assertEqual(m.prepare(self.repo, self.sandbox)[1], 2)
        self.assertFalse(self.sandbox.exists())

    def test_missing_original_map_fails_without_creating_sandbox(self):
        (self.project / m.MAP).unlink()
        self.assertEqual(self.prepare()[1], 2)
        self.assertFalse(self.sandbox.exists())

    def test_existing_sandbox_refused(self):
        self.sandbox.mkdir()
        self.assertEqual(self.prepare()[0], "BLOCKED_SANDBOX_NOT_NEW_OR_NOT_ISOLATED")

    def test_cannot_copy_sandbox_inside_source_repo(self):
        with patch.object(m, "BAD_OID", self.oid):
            status, rc = m.prepare(self.repo, self.repo / "subdir")
        self.assertEqual(rc, 2)
        self.assertEqual(status, "BLOCKED_SANDBOX_NOT_NEW_OR_NOT_ISOLATED")

    def test_finalize_requires_real_unreal_log_and_new_map(self):
        self.prepare()
        log = self.root / "editor.log"
        log.write_text("NO UE INVOCATION HERE " * 5)
        self.assertEqual(m.finalize(self.sandbox, log)[1], 2)
        self.assertFalse((self.sandbox / m.PROJECT / m.MAP).exists())

    def test_synthetic_success_restores_original_configuration(self):
        self.prepare()
        new_map = m.MAGIC + b"synthetic_new_map_not_from_editor" + b"1" * 96
        (self.sandbox / m.PROJECT / m.MAP).write_bytes(new_map)
        # This only tests the finalize logic: marker is a synthetic fixture,
        # NOT proof that UE actually generated a playable .umap.
        log = self.root / "editor.log"
        log.write_text("Fake CI fixture only\nCROWNFALL_M136_UE_LEVEL_GENERATED=PASS\n")
        with patch.object(m, "BAD_OID", self.oid):
            status, rc = m.finalize(self.sandbox, log)
        self.assertEqual(rc, 0)
        self.assertIn("REQUIRES_UE_LOAD_COOK", status)
        self.assertEqual((self.sandbox / m.PROJECT / m.DESCRIPTOR).read_text(),
                         (self.project / m.DESCRIPTOR).read_text())
        self.assertEqual((self.sandbox / m.PROJECT / m.CONFIG).read_text(),
                         (self.project / m.CONFIG).read_text())
        self.assertEqual((self.project / m.MAP).read_bytes(), self.fake_map)

    def test_private_binary_files_not_copied_into_sandbox(self):
        (self.project / "private.jks").write_bytes(b"fake_secret")
        (self.project / "sample.aab").write_bytes(b"fake_bundle")
        self.prepare()
        self.assertFalse((self.sandbox / m.PROJECT / "private.jks").exists())
        self.assertFalse((self.sandbox / m.PROJECT / "sample.aab").exists())

    def test_unrelated_asset_and_jks_with_unusual_extension_not_copied(self):
        (self.project / "Content/Maps").mkdir(parents=True, exist_ok=True)
        (self.project / "Content/Maps/PrivateArchive.bin").write_bytes(b"not-for-sandbox")
        (self.project / "Config/SigningProperties.txt").write_text("fake_password")
        self.prepare()
        dest = self.sandbox / m.PROJECT
        self.assertFalse((dest / "Content/Maps/PrivateArchive.bin").exists())
        self.assertFalse((dest / "Config/SigningProperties.txt").exists())

    def test_symlink_to_external_credentials_blocks_before_copy(self):
        external = self.root / "outside_backup"
        external.mkdir()
        (external / "key.properties").write_text("synthetic_private_secret")
        (self.project / "Content/ExternalKeys").symlink_to(external, target_is_directory=True)
        with patch.object(m, "BAD_OID", self.oid):
            status, code = m.prepare(self.repo, self.sandbox)
        self.assertEqual((status, code), ("BLOCKED_SYMLINK_IN_SOURCE_PROJECT", 2))
        self.assertFalse(self.sandbox.exists())

    def test_signing_key_in_default_engine_ini_blocks_before_copy(self):
        p = self.project / m.CONFIG
        p.write_text(p.read_text() + "  KeyStorePassword = FAKE_VALUE_NOT_A_SECRET\n")
        with patch.object(m, "BAD_OID", self.oid):
            status, code = m.prepare(self.repo, self.sandbox)
        self.assertEqual((status, code), ("BLOCKED_SIGNING_OR_SECRET_CONFIG_KEY", 2))
        self.assertFalse(self.sandbox.exists())

    def test_secret_key_in_default_game_ini_also_blocks_copy(self):
        p = self.project / "Config/DefaultGame.ini"
        p.write_text("[Section]\nMyClientSecret=SYNTHETIC_ONLY\n")
        with patch.object(m, "BAD_OID", self.oid):
            status, code = m.prepare(self.repo, self.sandbox)
        self.assertEqual((status, code), ("BLOCKED_SIGNING_OR_SECRET_CONFIG_KEY", 2))
        self.assertFalse(self.sandbox.exists())

    def test_unexpected_source_binary_blocks_before_copy(self):
        p = self.project / "Source/LastFrontier/native_keystore.bin"
        p.write_bytes(b"fixture")
        with patch.object(m, "BAD_OID", self.oid):
            status, code = m.prepare(self.repo, self.sandbox)
        self.assertEqual((status, code), ("BLOCKED_NON_CODE_SOURCE_ARTIFACT", 2))
        self.assertFalse(self.sandbox.exists())

    def test_map_generation_python_script_parses_without_engine(self):
        import ast
        script = self.project.parent.parent / "none.py"
        # Files live beside this test, not in synthetic project.
        script = Path(__file__).with_name("M136_Create_TestMap_In_Unreal.py")
        src = script.read_text()
        ast.parse(src)
        self.assertIn("LevelEditorSubsystem", src)
        self.assertIn("new_level", src)
        self.assertIn("CROWNFALL_M136_UE_LEVEL_GENERATED=PASS", src)


if __name__ == "__main__":
    unittest.main()
