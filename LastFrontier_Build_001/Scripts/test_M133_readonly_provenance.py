#!/usr/bin/env python3
"""M133 synthetic unit tests; NEVER require the user's Google Cloud VM or JKS."""
from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
from pathlib import Path
import tempfile
from unittest import TestCase, main, mock
import zipfile

import M133_VM_Map_AAB_Provenance_ReadOnly as tool


class M133ReadOnlyTests(TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="m133_fake_")
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.maps = {}
        for label in ("M63", "M84", "M106"):
            path = self.tmp / label / "Content/Maps/TestMap.umap"
            path.parent.mkdir(parents=True)
            path.write_bytes(tool.UNREAL_PACKAGE_TAG + label.encode() + b"_fixture")
            self.maps[label] = path
        self.aab = self.tmp / "original_test.aab"
        self.build_aab()

    def build_aab(self, *, with_arm64=True, with_obb=True, with_dex=True, with_pack=True):
        with zipfile.ZipFile(self.aab, mode="w") as archive:
            archive.writestr("BundleConfig.pb", b"\x00")
            archive.writestr("base/manifest/AndroidManifest.xml", b"\x01")
            if with_pack:
                archive.writestr("obbassets/manifest/AndroidManifest.xml", b"\x01")
            if with_dex:
                archive.writestr("base/dex/classes.dex", b"dex\n038\x00")
            if with_arm64:
                archive.writestr("base/lib/arm64-v8a/libUnreal.so", b"\x7fELF")
            if with_obb and with_pack:
                archive.writestr("obbassets/assets/main.obb.png", b"SIMULATED_TEST_DATA_NOT_A_REAL_OBB")

    def test_maps_distinct_and_aab_metadata_pass(self):
        maps, valid_maps = tool.inspect_maps(self.maps)
        self.assertTrue(valid_maps)
        self.assertEqual(maps["M63_VS_M84_MAP"], "DIFFERENT")
        self.assertEqual(maps["M84_VS_M106_MAP"], "DIFFERENT")
        self.assertEqual(maps["GITHUB_BAD_BLOB_MATCHED_BY_VM"], "NO_OR_UNAVAILABLE")
        aab, valid_aab = tool.inspect_aab(self.aab)
        self.assertTrue(valid_aab)
        self.assertEqual(aab["AAB_STRUCTURE"], "PASS_METADATA_ONLY")
        self.assertEqual(aab["AAB_OBBASSETS_MODULE"], "YES")
        self.assertEqual(aab["AAB_INSTALL_PACK_OBB_COUNT"], "1")
        self.assertEqual(aab["AAB_DELIVERY_MODE"], "NOT_DERIVED_NEEDS_BUNDLETOOL_OR_PLAY")

    def test_identical_map_copies_are_detected(self):
        contents = self.maps["M63"].read_bytes()
        for p in self.maps.values():
            p.write_bytes(contents)
        checks, ok = tool.inspect_maps(self.maps)
        self.assertTrue(ok)
        self.assertEqual(checks["M63_VS_M84_MAP"], "EQUAL")
        self.assertEqual(checks["M63_VS_M106_MAP"], "EQUAL")
        self.assertEqual(checks["M84_VS_M106_MAP"], "EQUAL")

    def test_historically_failed_map_identity_is_detected(self):
        bad_content = tool.UNREAL_PACKAGE_TAG + b"historical_simulated_bad_map"
        self.maps["M84"].write_bytes(bad_content)
        oid = hashlib.sha1(b"blob " + str(len(bad_content)).encode()
                           + b"\0" + bad_content).hexdigest()
        with mock.patch.object(tool, "HISTORIC_BAD_GITHUB_MAP_GIT_OID", oid):
            facts, ok = tool.inspect_maps(self.maps)
        self.assertFalse(ok)  # genuine prior UE cook failure blocks green status
        self.assertEqual(facts["MAP_PROVENANCE_STATUS"], "REVIEW_KNOWN_COOK_FAILED_BLOB")
        self.assertEqual(facts["M84_HISTORIC_BAD_GITHUB_BLOB"], "YES")
        self.assertEqual(facts["GITHUB_BAD_BLOB_MATCHED_BY_VM"], "YES")

    def test_corrupt_map_header_blocks_complete_result(self):
        self.maps["M106"].write_bytes(b"XXXX_corrupt_map")
        facts, ok = tool.inspect_maps(self.maps)
        self.assertFalse(ok)
        self.assertEqual(facts["M106_MAP_HEADER"], "INVALID")

    def test_missing_map_is_explicit(self):
        self.maps["M63"].unlink()
        facts, ok = tool.inspect_maps(self.maps)
        self.assertFalse(ok)
        self.assertEqual(facts["M63_MAP"], "MISSING_OR_UNSAFE")
        self.assertEqual(facts["M63_VS_M84_MAP"], "UNAVAILABLE")

    def test_unreal_native_library_is_required(self):
        self.build_aab(with_arm64=False)
        aab, valid = tool.inspect_aab(self.aab)
        self.assertFalse(valid)
        self.assertEqual(aab["AAB_ARM64_SO_COUNT"], "0")
        self.assertEqual(aab["AAB_STRUCTURE"], "REVIEW")

    def test_install_pack_requires_obb_payload(self):
        self.build_aab(with_obb=False)
        aab, valid = tool.inspect_aab(self.aab)
        self.assertFalse(valid)
        self.assertEqual(aab["AAB_INSTALL_PACK_OBB_COUNT"], "0")

    def test_missing_obassets_module_blocks_218_claim(self):
        self.build_aab(with_pack=False)
        report, valid = tool.inspect_aab(self.aab)
        self.assertFalse(valid)
        self.assertEqual(report["AAB_OBBASSETS_MODULE"], "NO")
        self.assertEqual(report["AAB_STRUCTURE"], "REVIEW")

    def test_dex_required(self):
        self.build_aab(with_dex=False)
        aab, valid = tool.inspect_aab(self.aab)
        self.assertFalse(valid)
        self.assertEqual(aab["AAB_DEX_COUNT"], "0")

    def test_symlink_aab_blocked(self):
        alias = self.tmp / "unsafe_link.aab"
        alias.symlink_to(self.aab)
        facts, valid = tool.inspect_aab(alias)
        self.assertFalse(valid)
        self.assertEqual(facts["AAB_FILE"], "MISSING_OR_UNSAFE")

    def test_fake_nonzip_file_rejected(self):
        self.aab.write_text("this is not a zip file", encoding="utf-8")
        facts, valid = tool.inspect_aab(self.aab)
        self.assertFalse(valid)
        self.assertEqual(facts["AAB_FILE"], "BAD_ZIP_OR_READ_FAILED")

    def test_one_command_summary_does_not_reveal_absolute_paths(self):
        output = io.StringIO()
        args = [
            "--m63-map", str(self.maps["M63"]),
            "--m84-map", str(self.maps["M84"]),
            "--m106-map", str(self.maps["M106"]),
            "--aab", str(self.aab),
        ]
        with mock.patch.object(tool, "M118_RECORDED_218_AAB_BYTES", self.aab.stat().st_size):
            with redirect_stdout(output):
                status = tool.main(args)
        self.assertEqual(status, 0)
        report = output.getvalue()
        self.assertIn("M133_RESULT=STRUCTURAL_AUDIT_COMPLETE", report)
        self.assertIn("M133_218_CRASH_CAUSE=UNCONFIRMED", report)
        self.assertNotIn(str(self.tmp), report)

    def test_original_218_gate_rejects_same_layout_wrong_size(self):
        facts, valid = tool.inspect_aab(self.aab, expected_bytes=tool.M118_RECORDED_218_AAB_BYTES)
        self.assertFalse(valid)
        self.assertEqual(facts["AAB_M118_EXPECTED_SIZE_GATE"],
                         "BLOCKED_DIFFERENT_ARTIFACT_SIZE")
        self.assertEqual(facts["AAB_STRUCTURE"], "REVIEW")

    def test_missing_aab_has_nonzero_exit(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = tool.main([
                "--m63-map", str(self.maps["M63"]),
                "--m84-map", str(self.maps["M84"]),
                "--m106-map", str(self.maps["M106"]),
                "--aab", str(self.tmp / "doesnotexist.aab"),
            ])
        self.assertEqual(code, 2)
        self.assertIn("M133_RESULT=INCOMPLETE_MISSING_OR_UNVERIFIED_INPUTS",
                      output.getvalue())


if __name__ == "__main__":
    main()
