# M44 Recovery Deep Audit — 2026-10-03

## Provenance
This recovery starts from the exact Library artifact `LastFrontier_Build_001_M44_Validated.zip` dated 2026-09-22. The original artifact is preserved unchanged separately.

## Baseline truth
The last verified execution state remains:
- STATIC_PREFLIGHT: PASS
- UE_COMPILE: NOT_RUN
- BUILD: NOT_RUN
- COOK: NOT_RUN
- PACKAGE: NOT_RUN
- RUNTIME/BOOT: NOT_RUN
- AUTOMATION/GAUNTLET: NOT_RUN
- PERFORMANCE: NOT_RUN

This recovery package does **not** promote the project beyond M44.

## Deep audit corrections applied
1. Moved `LastFrontier.Target.cs` and `LastFrontierEditor.Target.cs` to the canonical `Source/` target location while leaving `LastFrontier.Build.cs` in the runtime module directory.
2. Removed the source-level assignment `GameInstanceClass = ULFGameInstance::StaticClass()` from `ALFGameMode`. UE 5.8 exposes `GameInstanceClass` through `UGameMapsSettings`, not as GameMode wiring.
3. Added `GameInstanceClass=/Script/LastFrontier.LFGameInstance` under `[/Script/EngineSettings.GameMapsSettings]`.
4. Added `DefaultPawnClass = ALFCharacter::StaticClass()` so the documented GameMode→Character wiring actually exists in source.
5. Moved `UGeneralProjectSettings` metadata to `Config/DefaultGame.ini` because that settings class uses `Config=Game`.
6. Replaced the log-only BuildGraph scaffold with real `Compile`, `Cook`, and `Stage` tasks.
7. Split Compile from Cook/Package. The missing map no longer prevents the first real UBT compile attempt.
8. Kept the map gate fail-closed: Cook/Package will not claim success until a genuine `Content/Maps/TestMap.umap` exists.

## Remaining external blockers
- Unreal Engine 5.8 / UnrealBuildTool / RunUAT are not installed in the current analysis environment.
- `Content/Maps/TestMap.umap` is still absent. It must be created/saved by Unreal Engine; a fake text `.umap` was deliberately not generated.

## Execution order on a real UE 5.8 machine
1. Set `UE_ROOT` to the Unreal Engine 5.8 installation root.
2. Run `Scripts/M44_Recovery_Static_Audit.py`.
3. Run `Scripts/Run_M44_Compile_UE58.*` and keep the complete log.
4. Only if Compile passes, create/save `/Game/Maps/TestMap` in UE 5.8.
5. Run `Scripts/Run_M44_BuildCookPackage_UE58.*`.
6. After a packaged artifact exists, perform boot/smoke evidence, then Automation/Gauntlet, then performance measurements.

## Evidence rule
A script being present is not a successful build. Only actual UE/UBT/UAT process output plus produced artifacts can promote Compile/Build/Cook/Package/Runtime gates to PASS.
