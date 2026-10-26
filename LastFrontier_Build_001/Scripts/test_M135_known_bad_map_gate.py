#!/usr/bin/env python3
"""M135 synthetic tests: gate warns about historically failed map but does not modify assets."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import M135_KnownBadMap_ReleaseBlock_ReadOnly as gate

MAGIC = gate.UNREAL_PACKAGE_MAGIC


class KnownBadMapTests(unittest.TestCase):
    def setUp(self):
        obj = tempfile.TemporaryDirectory(prefix="m135_map_")
        self.addCleanup(obj.cleanup)
        self.map = Path(obj.name) / "TestMap.umap"
        self.valid_bytes = MAGIC + b"safe-but-unvalidated-unreal-fixture" + b"0" * 64
        self.map.write_bytes(self.valid_bytes)

    def test_regular_map_is_only_not_known_bad(self):
        status, rc = gate.inspect_map(self.map)
        self.assertEqual(rc, 0)
        self.assertEqual(status, "NOT_KNOWN_BAD_STILL_REQUIRES_UE_LOAD_AND_COOK")

    def test_known_cook_failure_blocks_even_with_correct_magic(self):
        digest = hashlib.sha1(
            b"blob " + str(len(self.valid_bytes)).encode("ascii") + b"\0" + self.valid_bytes
        ).hexdigest()
        with patch.object(gate, "KNOWN_FAILED_UE_COOK_MAP_OID", digest):
            status, rc = gate.inspect_map(self.map)
        self.assertEqual(rc, 2)
        self.assertEqual(status, "BLOCKED_HISTORIC_UE_COOK_FAILURE")

    def test_wrong_header_blocks(self):
        self.map.write_bytes(b"BAD!" + b"x" * 80)
        self.assertEqual(gate.inspect_map(self.map), ("BLOCKED_BAD_UNREAL_PACKAGE_HEADER", 2))

    def test_missing_map_blocks(self):
        self.map.unlink()
        self.assertEqual(gate.inspect_map(self.map), ("BLOCKED_MISSING_OR_UNSAFE_MAP", 2))

    def test_symlink_map_blocks(self):
        alias = self.map.with_suffix(".alias")
        alias.symlink_to(self.map)
        self.assertEqual(gate.inspect_map(alias), ("BLOCKED_MISSING_OR_UNSAFE_MAP", 2))

    def test_gate_does_not_change_bytes(self):
        before = self.map.read_bytes()
        gate.inspect_map(self.map)
        self.assertEqual(self.map.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
