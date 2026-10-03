from __future__ import annotations
import json, pathlib, re, sys, xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parents[1]
passes=[]; warnings=[]; errors=[]
def ok(cond, name, err): (passes if cond else errors).append(name if cond else err)

def text(rel):
    p=root/rel
    if not p.is_file():
        errors.append(f"missing file: {rel}")
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

# Descriptor / engine pin
try:
    u=json.loads(text("LastFrontier.uproject"))
    ok(u.get("EngineAssociation")=="5.8", "ENGINE_ASSOCIATION_5_8", "EngineAssociation must be 5.8")
    mods={m.get("Name") for m in u.get("Modules",[])}
    ok("LastFrontier" in mods, "RUNTIME_MODULE_DECLARED", "LastFrontier runtime module missing")
except Exception as e: errors.append(f"uproject parse failed: {e}")

# Canonical target/module layout
for rel,name in [
    ("Source/LastFrontier.Target.cs","GAME_TARGET_CANONICAL"),
    ("Source/LastFrontierEditor.Target.cs","EDITOR_TARGET_CANONICAL"),
    ("Source/LastFrontier/LastFrontier.Build.cs","MODULE_RULES_CANONICAL")]:
    ok((root/rel).is_file(),name,f"missing {rel}")
legacy=[root/"Source/LastFrontier/LastFrontier.Target.cs", root/"Source/LastFrontier/LastFrontierEditor.Target.cs"]
ok(not any(p.exists() for p in legacy), "NO_LEGACY_NESTED_TARGET_FILES", "duplicate/nested Target.cs files remain inside module directory")

# Target rules compile-risk checks
game_target=text("Source/LastFrontier.Target.cs")
editor_target=text("Source/LastFrontierEditor.Target.cs")
for t,label in [(game_target,"GAME"),(editor_target,"EDITOR")]:
    ok("EngineIncludeOrderVersion.Unreal5_8" in t, f"{label}_INCLUDE_ORDER_5_8", f"{label} target not pinned to Unreal5_8 include order")
    ok("BuildSettingsVersion.V5" in t, f"{label}_BUILD_SETTINGS_V5", f"{label} target missing BuildSettingsVersion.V5")

# Module dependencies
build=text("Source/LastFrontier/LastFrontier.Build.cs")
for dep in ("Core","CoreUObject","Engine","InputCore","NetCore"):
    ok(f'"{dep}"' in build, f"DEPENDENCY_{dep}", f"module dependency missing: {dep}")

# UHT header invariants
for h in sorted((root/"Source/LastFrontier/Public").rglob("*.h")):
    s=h.read_text(encoding="utf-8",errors="replace")
    rel=h.relative_to(root).as_posix()
    generated=re.findall(r'#include\s+"([^"]+\.generated\.h)"',s)
    ok(bool(generated), f"GENERATED_HEADER_{h.stem}", f"{rel}: generated.h include missing")
    if generated:
        include_lines=[line.strip() for line in s.splitlines() if line.strip().startswith("#include")]
        ok(include_lines[-1].endswith(f'"{h.stem}.generated.h"'), f"GENERATED_HEADER_LAST_{h.stem}", f"{rel}: generated.h must be the last include")
    ok("GENERATED_BODY()" in s, f"GENERATED_BODY_{h.stem}", f"{rel}: GENERATED_BODY missing")

# GameMode / GameInstance / pawn wiring
gm=text("Source/LastFrontier/Private/Core/LFGameMode.cpp")
engine_ini=text("Config/DefaultEngine.ini")
oki="GameInstanceClass=/Script/LastFrontier.LFGameInstance" in engine_ini
ok("GameInstanceClass =" not in gm, "NO_INVALID_GAMEMODE_GAMEINSTANCE_MEMBER", "LFGameMode still assigns nonexistent/incorrect GameInstanceClass member")
ok(oki,"GAMEINSTANCE_IN_GAMEMAPSSETTINGS","GameInstanceClass missing from GameMapsSettings")
ok("GameStateClass = ALFGameState::StaticClass()" in gm,"GAMESTATE_WIRED","GameStateClass not wired")
ok("DefaultPawnClass = ALFCharacter::StaticClass()" in gm,"DEFAULT_PAWN_WIRED","DefaultPawnClass not wired")

# Replication
gsh=text("Source/LastFrontier/Public/Core/LFGameState.h")
gsc=text("Source/LastFrontier/Private/Core/LFGameState.cpp")
ok("UPROPERTY(Replicated" in gsh and "AlivePlayers" in gsh,"ALIVEPLAYERS_REPLICATED","AlivePlayers replicated declaration missing")
ok("DOREPLIFETIME(ALFGameState, AlivePlayers)" in gsc,"ALIVEPLAYERS_REGISTERED","AlivePlayers DOREPLIFETIME missing")

# BuildGraph parse and compile task
try:
    graph=root/"Build/Graph/LastFrontierBuild.xml"; ET.parse(graph); passes.append("BUILDGRAPH_XML_VALID")
    gt=graph.read_text(encoding="utf-8")
    ok("<Compile " in gt,"BUILDGRAPH_COMPILE_TASK","BuildGraph Compile task missing")
except Exception as e: errors.append(f"BuildGraph parse failed: {e}")

# Compile runner must not gate on map
runner=text("Scripts/Run_M47_Compile_UE58.sh")
ok("TestMap.umap" not in runner,"COMPILE_INDEPENDENT_OF_MAP","M47 compile runner incorrectly gates on TestMap.umap")
ok("LastFrontierEditor" in runner and "LastFrontier" in runner,"COMPILE_BOTH_TARGETS","runner does not compile both Editor and Game targets")

# Map/cook remains separate and honestly unresolved
map_path=root/"Content/Maps/TestMap.umap"
if map_path.is_file() and map_path.stat().st_size>0:
    passes.append("TESTMAP_PRESENT")
else:
    warnings.append("TESTMAP_MISSING: does not block Compile; it still blocks the original TestMap Cook/Package path")

# Environment probe only; absence is warning, not static failure
ue_root=None
import os
if os.environ.get("UE_ROOT") and pathlib.Path(os.environ["UE_ROOT"]).is_dir(): ue_root=pathlib.Path(os.environ["UE_ROOT"])
if ue_root: passes.append(f"UE_ROOT_PRESENT={ue_root}")
else: warnings.append("UE_ROOT_NOT_AVAILABLE_IN_CURRENT_CONTAINER: real UBT compile cannot be executed here")

status="FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS")
print("M47_STATIC_STATUS="+status)
for x in passes: print("PASS="+x)
for x in warnings: print("WARNING="+x)
for x in errors: print("ERROR="+x)
sys.exit(1 if errors else 0)
