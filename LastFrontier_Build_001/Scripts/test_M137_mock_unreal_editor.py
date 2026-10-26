#!/usr/bin/env python3
"""Exercise UE map-generator control flow with a FAKE Unreal API.

This is a deterministic offline simulation, NOT Unreal Editor validation.
The real binary TestMap is generated only by an installed UE5.8.
"""
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("M136_Create_TestMap_In_Unreal.py")
MAP = "/Game/Maps/TestMap"


class FakeAssetLibrary:
    def __init__(self, data):
        self.data = data

    def does_asset_exist(self, path):
        self.data["calls"].append(("asset_exists", path))
        return bool(self.data.get("exists", False))


class FakeLevelSubsystem:
    def __init__(self, data):
        self.data = data

    def new_level(self, path, partitioned):
        self.data["calls"].append(("new_level", path, partitioned))
        if self.data.get("new_level_ok", True):
            self.data["exists"] = True
            return True
        return False

    def save_current_level(self):
        self.data["calls"].append(("save",))
        return self.data.get("save_ok", True)

    def load_level(self, path):
        self.data["calls"].append(("load", path))
        return self.data.get("load_ok", True)


class FakeActor:
    def __init__(self, data):
        self.data = data

    def set_actor_label(self, label):
        self.data["calls"].append(("set_label", label))


class FakeActorSubsystem:
    def __init__(self, data):
        self.data = data

    def spawn_actor_from_class(self, actor_class, location, rotation):
        self.data["calls"].append(("spawn", actor_class, location, rotation))
        return FakeActor(self.data) if self.data.get("spawn_ok", True) else None


def fake_unreal(**override):
    data = {"calls": [], "logs": [], **override}
    fake = types.ModuleType("unreal")
    fake.PlayerStart = object()
    fake.Vector = lambda *values: ("vector", *values)
    fake.Rotator = lambda *values: ("rotator", *values)
    fake.LevelEditorSubsystem = type("LevelEditorSubsystem", (), {})
    fake.EditorActorSubsystem = type("EditorActorSubsystem", (), {})
    fake.EditorAssetLibrary = FakeAssetLibrary(data)

    def get_subsystem(cls):
        if cls is fake.LevelEditorSubsystem:
            return FakeLevelSubsystem(data) if data.get("level_subsystem_ok", True) else None
        if cls is fake.EditorActorSubsystem:
            return FakeActorSubsystem(data) if data.get("actor_subsystem_ok", True) else None
        raise AssertionError("unexpected subsystem")
    fake.get_editor_subsystem = get_subsystem
    fake.log = lambda text: data["logs"].append(("info", text))
    fake.log_error = lambda text: data["logs"].append(("error", text))
    return fake, data


class EditorPythonFlowTests(unittest.TestCase):
    def execute(self, **settings):
        fake, data = fake_unreal(**settings)
        with patch.dict(sys.modules, {"unreal": fake}):
            runpy.run_path(str(SCRIPT), run_name="__main__")
        return data

    def test_editor_flow_generates_saves_then_reloads(self):
        data = self.execute()
        tags = [item[0] for item in data["calls"]]
        self.assertLess(tags.index("new_level"), tags.index("spawn"))
        self.assertLess(tags.index("spawn"), tags.index("save"))
        self.assertLess(tags.index("save"), tags.index("load"))
        self.assertIn(("load", MAP), data["calls"])
        self.assertIn(("info", "CROWNFALL_M137_UE_TESTMAP_EDITOR_RELOAD=PASS"), data["logs"])
        self.assertIn(("info", "CROWNFALL_M136_UE_LEVEL_GENERATED=PASS"), data["logs"])

    def test_existing_map_is_never_overwritten(self):
        with self.assertRaisesRegex(RuntimeError, "PREEXISTING_TESTMAP_BLOCKED"):
            self.execute(exists=True)

    def test_failed_new_level_never_reports_success(self):
        with self.assertRaisesRegex(RuntimeError, "NEW_LEVEL_FAILED"):
            self.execute(new_level_ok=False)

    def test_missing_editor_actor_subsystem_fails(self):
        with self.assertRaisesRegex(RuntimeError, "EDITOR_ACTOR_SUBSYSTEM_UNAVAILABLE"):
            self.execute(actor_subsystem_ok=False)

    def test_failed_spawn_fails_before_save(self):
        fake, data = fake_unreal(spawn_ok=False)
        with patch.dict(sys.modules, {"unreal": fake}):
            with self.assertRaisesRegex(RuntimeError, "PLAYER_START_SPAWN_FAILED"):
                runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertNotIn(("save",), data["calls"])

    def test_failed_level_save_blocks_reload(self):
        fake, data = fake_unreal(save_ok=False)
        with patch.dict(sys.modules, {"unreal": fake}):
            with self.assertRaisesRegex(RuntimeError, "NEW_LEVEL_SAVE_FAILED"):
                runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertNotIn(("load", MAP), data["calls"])

    def test_failed_real_editor_reload_never_logs_success(self):
        fake, data = fake_unreal(load_ok=False)
        with patch.dict(sys.modules, {"unreal": fake}):
            with self.assertRaisesRegex(RuntimeError, "SAVED_LEVEL_RELOAD_FAILED"):
                runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertNotIn(("info", "CROWNFALL_M136_UE_LEVEL_GENERATED=PASS"), data["logs"])


if __name__ == "__main__":
    unittest.main()
