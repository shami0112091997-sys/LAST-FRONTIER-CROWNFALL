#!/usr/bin/env python3
"""Source-marker checks only. Unreal compilation and Android runtime are not exercised."""
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parent.parent / "Source/LastFrontier"


class BootObservabilitySourceTests(unittest.TestCase):
    def test_world_and_enemy_spawns_are_reported(self):
        code = (SOURCE / "Private/World/LFWorldDirector.cpp").read_text(encoding="utf-8")
        self.assertIn("CROWNFALL_BOOT_WORLD_DIRECTOR_BEGINPLAY=M135", code)
        self.assertIn("CROWNFALL_BOOT_BASIC_SHAPES_MISSING", code)
        self.assertIn("CROWNFALL_ENEMIES_SPAWNED=%d", code)
        self.assertIn("CROWNFALL_ENEMY_SPAWN_INCOMPLETE=%d_OF_%d", code)
        self.assertIn("CROWNFALL_M60_WORLD=READY", code)
        self.assertIn("SetTimerForNextTick", code)

    def test_player_spawning_failure_is_reported(self):
        code = (SOURCE / "Private/Core/LFGameMode.cpp").read_text(encoding="utf-8")
        self.assertIn("CROWNFALL_BOOT_PLAYER_SPAWN_FAILED", code)
        self.assertIn("CROWNFALL_M60_PLAYER=READY", code)


if __name__ == "__main__":
    unittest.main()
