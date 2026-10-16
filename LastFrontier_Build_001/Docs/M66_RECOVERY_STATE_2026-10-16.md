# CROWNFALL M66 Smart Recovery State

Date: 2026-10-16

This branch was created from `m60-unreal-first-playable` as a safe recovery/integration branch. It does not replace main or the M60 branch.

## Authoritative live workspace

- VM: `crownfall-m62-build`
- GCP project: `project-f1aa4101-551b-4dbe-981`
- Zone: `us-central1-a`
- Unreal Engine: `$HOME/UE_5.8.3`
- Current live project: `$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001`

The VM copy is currently the authoritative source for the newest binary Unreal assets (`.uasset`, `.umap`) and the M63 editor-commandlet work. Those newest binaries are not assumed to exist on GitHub until explicitly synced.

## Recovered stable checkpoints

### Android / Play
- Package: `com.crownfall.stronghold`
- Current verified Play upload line reached versionCode 217.
- Billing permission issue was removed by disabling IAP for the current non-IAP build.
- v217 bundle verification previously passed with versionCode 217 and debuggable=false.
- A separate Google Play device-compatibility warning remained to diagnose later.

### M63 real-content pipeline
Verified on the VM:
- UE editor compile path works.
- Python commandlet clean-exit gate passed.
- TestMap load-only gate passed without modifying the map.
- C++ editor-only commandlet module compiled and executed cleanly.
- C++ package/world load-only gate passed.
- Atomic test map creation passed:
  - `/Game/Maps/TestMap_M63_Atomic`
  - one actor tagged `CROWNFALL_ATOMIC`
  - mesh `SM_WoodenCrate01_wooden_crate_01`
  - location `(0,0,100)`
- Independent reopen/persistence verification passed.
- Original `TestMap` stayed unchanged through the atomic tests.

### Imported real content
Latest audit:
- 11 Static Mesh assets
- 60,646 LOD0 triangles total
- 43,251 LOD0 vertices total
- All audited meshes currently had one LOD.
- Real Environment content size was about 6.9 MB.
- Street lamp was the heaviest mesh at about 30,610 triangles.
- Wine barrel was about 10,204 triangles.
- Wooden crate was about 5,508 triangles.

### Texture / collision / BodySetup
Latest verified audits:
- Texture/collision audit process exited 0.
- Texture count: 6.
- Static mesh count: 11.
- Content hash unchanged.
- No crash markers.
- BodySetup audit process exited 0.
- BodySetup mesh count: 11.
- No asset modification requested.
- Real content remained unchanged.

### StreetLamp LOD experiment
A controlled LOD-generation test was attempted on:
`/Game/Environment/Real/Models/street_lamp_01/SM_StreetLamp01.SM_StreetLamp01`

Observed result:
- `LOD0_TRIANGLES=30610`
- `SET_LODS_RESULT=-1`
- test declared failure
- backup restoration completed
- `ROLLBACK=PASS`

Therefore: no StreetLamp LOD change should be considered committed. The asset should be treated as restored to its pre-test state.

Epic UE 5.8 docs define a negative `SetLodsWithNotification/SetLods` result as reduction failure and instruct checking the log for the explanation. The next task is diagnosis, not another blind LOD attempt.

## GitHub recovery sources
- Safe real first-playable base: `m60-unreal-first-playable`
- Recovery/integration branch: `m66-smart-recovery`
- Genuine `LastFrontier_Build_001/Content/Maps/TestMap.umap` exists on the M60 branch.
- M60 contains gameplay source such as `LFCharacter`, `LFGameMode`, `LFWorldDirector`, and `LFHUD`.

## Library recovery sources
Persistent Library also contains M65 recovery material including:
- `CROWNFALL_M65_UNREAL_SOURCE_RELEASE_CANDIDATE.zip`
- `CROWNFALL_M65_PROJECT_CHECKPOINT_2026-10-08_AR.txt`
- `CROWNFALL_M65_AUDIT_REPORT_AR.txt`
- `CROWNFALL_M65_RESUME_REPORT_2026-10-14_AR.md`

## Safety policy for M66
1. Never overwrite `TestMap.umap` while testing automation.
2. Use copy/atomic-map validation before promotion.
3. Back up a target asset before any editor mutation.
4. Require post-run reopen verification for any saved Unreal asset.
5. If an API returns a negative/failure result, restore the backup and diagnose the exact log before retrying.
6. Do not modify UE engine source for a project workaround.
7. Do not add fake padding to make the Android package larger; package growth must come from real game content.
8. Keep Editor-only tooling out of Android/Shipping runtime modules.

## Immediate next task
Diagnose why StreetLamp LOD generation returned `-1` by inspecting:
- `$HOME/crownfall/M63_STREETLAMP_LOD.log`
- local UE 5.8.3 `StaticMeshEditorSubsystem::SetLodsWithNotification` source
- installed mesh-reduction module availability

Do not retry the LOD mutation until the failure reason is identified.
