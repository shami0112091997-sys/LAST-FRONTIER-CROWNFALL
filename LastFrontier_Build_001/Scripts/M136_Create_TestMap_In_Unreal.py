"""M136: execute via Unreal Engine 5.8's Python Editor Script Plugin ONLY.

Run on an isolated M136 sandbox prepared from the historically corrupt GitHub
TestMap; NOT on the trusted M84/M106 VM. Unreal creates a real new binary .umap.
This is NOT a reconstruction of M84's original level or a full Android test.
"""
import unreal

LEVEL_PATH = "/Game/Maps/TestMap"


def require(condition, code):
    if not condition:
        unreal.log_error("CROWNFALL_M136_FAILURE=" + code)
        raise RuntimeError(code)


assets = unreal.EditorAssetLibrary
require(not assets.does_asset_exist(LEVEL_PATH), "PREEXISTING_TESTMAP_BLOCKED")

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
require(level is not None, "LEVEL_EDITOR_SUBSYSTEM_UNAVAILABLE")
require(level.new_level(LEVEL_PATH, False), "NEW_LEVEL_FAILED")

# C++ ALFWorldDirector creates terrain, lighting and enemies at runtime.
# Do not duplicate its lights here; create one PlayerStart only.
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
require(actors is not None, "EDITOR_ACTOR_SUBSYSTEM_UNAVAILABLE")
start = actors.spawn_actor_from_class(
    unreal.PlayerStart,
    unreal.Vector(0.0, -3200.0, 180.0),
    unreal.Rotator(0.0, 0.0, 0.0),
)
require(start is not None, "PLAYER_START_SPAWN_FAILED")
start.set_actor_label("Crownfall_M136_PlayerStart")
require(level.save_current_level(), "NEW_LEVEL_SAVE_FAILED")
require(assets.does_asset_exist(LEVEL_PATH), "ASSET_REGISTRY_MISSING_LEVEL")
unreal.log("CROWNFALL_M136_UE_LEVEL_GENERATED=PASS")
