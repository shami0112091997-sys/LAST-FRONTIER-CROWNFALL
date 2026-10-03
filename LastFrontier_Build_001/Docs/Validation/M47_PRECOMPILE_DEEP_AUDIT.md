# M47 Pre-Compile Deep Audit

## Goal
Advance the recovered M44 project to the strongest honest state possible before a real Unreal Engine 5.8 invocation.

## Historical defects corrected in the recovery line
1. The original M44 placed `LastFrontier.Target.cs` and `LastFrontierEditor.Target.cs` inside the module directory. The recovery line places them at `Source/`, the canonical project target location.
2. The original M44 assigned `GameInstanceClass` from `ALFGameMode`. The recovery line configures `GameInstanceClass=/Script/LastFrontier.LFGameInstance` under `GameMapsSettings` instead.
3. The recovered GameMode explicitly wires `ALFCharacter` as `DefaultPawnClass` and `ALFGameState` as `GameStateClass`.
4. Compile and Cook gates are separated. Missing `TestMap.umap` is no longer allowed to prevent the first real UBT compile.

## M47 additions
- Cross-platform compile-only runners that compile both Editor and Game targets.
- Linux runner can use UE `Build.sh`, native UBT, or `UnrealBuildTool.dll` through `dotnet`.
- Compile runner verifies that project binary artifacts were actually produced before writing `M47_COMPILE_STATUS=PASS`.
- Static pre-compile audit checks UHT header invariants, module dependencies, replication wiring, target placement, config wiring, BuildGraph validity, and the map/compile separation.
- Evidence auditor refuses to promote the checkpoint without both a PASS log marker and actual binary artifacts.

## Evidence rule
M47 is **not** a Compile PASS until `Scripts/M47_Compile_Evidence_Audit.py` reports `M47_EVIDENCE_STATUS=REAL_COMPILE_PASS` after execution on an Unreal Engine 5.8 machine.

## Current blocker in this container
Unreal Engine 5.8 / UnrealBuildTool is not installed here. Therefore this package may reach static pre-compile readiness only; no UE Compile/Build/Cook/Package/Runtime success is claimed.
