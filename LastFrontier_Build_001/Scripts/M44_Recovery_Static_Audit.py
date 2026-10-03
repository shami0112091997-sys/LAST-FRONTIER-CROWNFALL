from __future__ import annotations
import configparser
import hashlib
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []
passes: list[str] = []

def check(cond: bool, ok: str, bad: str):
    if cond:
        passes.append(ok)
    else:
        errors.append(bad)

# Descriptor
try:
    p = json.loads((root / "LastFrontier.uproject").read_text(encoding="utf-8"))
    check(p.get("EngineAssociation") == "5.8", "UPROJECT_ENGINE_5_8", "EngineAssociation is not 5.8")
    mods = {m.get("Name") for m in p.get("Modules", [])}
    check("LastFrontier" in mods, "UPROJECT_RUNTIME_MODULE", "LastFrontier runtime module missing from .uproject")
except Exception as e:
    errors.append(f"uproject parse: {e}")

# XML + real tasks
try:
    graph = root / "Build" / "Graph" / "LastFrontierBuild.xml"
    ET.parse(graph)
    passes.append("BUILDGRAPH_XML_WELL_FORMED")
    text = graph.read_text(encoding="utf-8")
    for tag in ("Compile", "Cook", "Stage"):
        check(f"<{tag} " in text, f"BUILDGRAPH_{tag.upper()}_TASK", f"BuildGraph missing {tag} task")
except Exception as e:
    errors.append(f"BuildGraph parse: {e}")

# Canonical module/target placement
check((root / "Source" / "LastFrontier.Target.cs").is_file(), "GAME_TARGET_AT_SOURCE_ROOT", "Source/LastFrontier.Target.cs missing")
check((root / "Source" / "LastFrontierEditor.Target.cs").is_file(), "EDITOR_TARGET_AT_SOURCE_ROOT", "Source/LastFrontierEditor.Target.cs missing")
check((root / "Source" / "LastFrontier" / "LastFrontier.Build.cs").is_file(), "MODULE_BUILD_CS_PRESENT", "Module Build.cs missing")

# Core classes and duplicate-name scan
headers = list((root / "Source").rglob("*.h"))
classes: dict[str, list[pathlib.Path]] = {}
for h in headers:
    t = h.read_text(encoding="utf-8", errors="ignore")
    for name in re.findall(r"\bclass\s+LASTFRONTIER_API\s+(\w+)", t):
        classes.setdefault(name, []).append(h)
for name, paths in classes.items():
    if len(paths) > 1:
        errors.append(f"duplicate reflected class {name}: " + ", ".join(str(p.relative_to(root)) for p in paths))
check(all(len(v) == 1 for v in classes.values()), "NO_DUPLICATE_REFLECTED_CLASSES", "Duplicate reflected classes detected")

# GameMode compile-risk checks
gm = (root / "Source" / "LastFrontier" / "Private" / "Core" / "LFGameMode.cpp").read_text(encoding="utf-8")
check("GameInstanceClass =" not in gm, "NO_INVALID_GAMEMODE_GAMEINSTANCE_ASSIGNMENT", "LFGameMode assigns GameInstanceClass directly")
check("GameStateClass = ALFGameState::StaticClass()" in gm, "GAMEMODE_GAMESTATE_WIRING", "GameStateClass wiring missing")
check("DefaultPawnClass = ALFCharacter::StaticClass()" in gm, "GAMEMODE_CHARACTER_WIRING", "DefaultPawnClass wiring missing")

# Config checks
engine_ini = (root / "Config" / "DefaultEngine.ini").read_text(encoding="utf-8")
game_ini = (root / "Config" / "DefaultGame.ini").read_text(encoding="utf-8")
check("GameInstanceClass=/Script/LastFrontier.LFGameInstance" in engine_ini, "GAMEINSTANCE_CONFIGURED_IN_GAMEMAPSSETTINGS", "GameInstanceClass config missing")
check("GlobalDefaultGameMode=/Script/LastFrontier.LFGameMode" in engine_ini, "DEFAULT_GAMEMODE_CONFIGURED", "GlobalDefaultGameMode missing")
check("ProjectName=LAST FRONTIER: CROWNFALL" in game_ini, "PROJECT_METADATA_IN_DEFAULTGAME", "Project metadata missing from DefaultGame.ini")

# Replication checks
gs_h = (root / "Source" / "LastFrontier" / "Public" / "Core" / "LFGameState.h").read_text(encoding="utf-8")
gs_cpp = (root / "Source" / "LastFrontier" / "Private" / "Core" / "LFGameState.cpp").read_text(encoding="utf-8")
check("UPROPERTY(Replicated" in gs_h and "AlivePlayers" in gs_h, "ALIVEPLAYERS_REPLICATED_PROPERTY", "AlivePlayers replicated UPROPERTY missing")
check("DOREPLIFETIME(ALFGameState, AlivePlayers)" in gs_cpp, "ALIVEPLAYERS_DOREPLIFETIME", "AlivePlayers DOREPLIFETIME missing")

# Map is not required for Compile, but it is required before Cook/Package for this config.
map_path = root / "Content" / "Maps" / "TestMap.umap"
if map_path.is_file() and map_path.stat().st_size > 0:
    passes.append("TESTMAP_ASSET_PRESENT")
else:
    warnings.append("TESTMAP_ASSET_MISSING: Compile can proceed; Cook/Package remains blocked until a genuine UE 5.8 map is saved at Content/Maps/TestMap.umap")

# Archive integrity manifest input count
files = [p for p in root.rglob("*") if p.is_file()]
passes.append(f"FILE_COUNT_{len(files)}")

print("STATIC_AUDIT_STATUS=" + ("PASS_WITH_WARNINGS" if not errors and warnings else "PASS" if not errors else "FAIL"))
for p in passes:
    print("PASS=" + p)
for w in warnings:
    print("WARNING=" + w)
for e in errors:
    print("ERROR=" + e)
sys.exit(1 if errors else 0)
