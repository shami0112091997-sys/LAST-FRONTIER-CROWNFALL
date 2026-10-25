# M132 — CROWNFALL source audit: verified CI and historical TestMap cook failure

**Date:** 2026-10-25
**Branch:** `m132-ci-source-audit-only` — isolated from `m131-isolated-source-repairs-20261025`
**Scope:** read-only source validation, no UE build/cook, no AAB, Google Play, M106 VM, personal phone, or signing credentials accessed.

## Live CI result — actual GitHub Actions logs, not presumed

- Initial source-only action run: **40173743911** — success, 6 synthetic unit tests passed; 0 hard structural failures, 4 source-only reviews.
- Most recent after historical-map guard + test: **40174070157** — **success**, **7 of 7 actual Python unittest tests passed**, Bash syntax checks passed, no Unreal/Gradle/build or signing.
- Final source audit output:
  - `M131_STRUCTURAL_ERRORS=0`
  - `M131_REVIEW_ONLY=5`
  - `M131_UNREAL_MAP_HEADER_PRESENT=PASS`
  - `M131_TESTMAP_HISTORIC_COOK_FAILURE=REVIEW`
  - `M131_AAB_218_RUNTIME=NOT_INSPECTED`
  - `M131_CRASH_CAUSE=UNCONFIRMED`
- URL: https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/40174070157
- New CI file `.github/workflows/m132-source-only-ci.yml` triggers only on this branch, checks Python tests and source and Bash syntax, permissions `contents: read`, no secrets.

## Confirmed historical Unreal failure: exact map blob preserved

**Important verified cross-reference**, not a hypothesis:

1. Genuine GitHub Actions Unreal run **37645589203**, **2026-10-07**, head commit `d77f736e50e0746a69f5ea434cfdea28c6da88c2`, failed during cook.
2. Its job `build-cook-package` (ID `112875375372`) emitted:
   `LogLinker: Error: .../Content/Maps/TestMap.umap: Serialization error - FName are serialized as an index recorded in the package header, the current deserialized index has value 64, outside of the valid range [0, 44).`
3. Later `Cook failed.` and `AutomationTool exiting with ExitCode=25 (Error_UnknownCookFailure)`.
4. Via `fetch_file` at exact *run head commit*, and at `m132-ci-source-audit-only`, the Git blob ID for `LastFrontier_Build_001/Content/Maps/TestMap.umap` is **the same** `965b78fc071c21412f966b70712eb30724799c20`; this is independent of branch-head movement.
5. M131's earlier magic-header check is insufficient: the four bytes match Unreal package tag while the **full** file failed that original UE cook.
6. M132 source checker now emits a review flag on the exact known Git blob OID and has a synthetic regression test for the flag.

**Limit:** The owner has separate *VM source* `M63_REAL_MOBILE`, M84/M106 workspaces. Historical recovery record `CROWNFALL_Recovery_Audit_2026-10-19_AR.md` recounts M85 Editor map load PASS, M86 ASTC Cook ~220 packages 0 errors, M88 stage PASS and successful Release M118/119 packaging in later VM context. **Those records refer to VM workspace, not proof the GitHub TestMap blob was fixed.** We did not obtain the M84/M106 map hashes in this turn, therefore do NOT imply that build 218 used the bad GitHub map or that it crashed because of this specific serialization failure. **Never replace the successfully validated VM map with this GitHub blob** without matching hashes and valid UE load/cook.

Reference: https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/37645589203

## Other tracked source warnings (not runtime-crash diagnoses)

- `Config/DefaultEngine.ini` source `StoreVersion=215` vs Play AAB 218; original M106 sandbox uses independent settings. Do not overwrite signed VM settings with GitHub.
- UE 5.8 documentation: recommended Android target SDK 35, NDK r27c, JDK OpenJDK 21.0.3. GitHub targets 36; investigate compatibility, don't blindly lower Target SDK.
- Separate legacy Android WebView project uses identical `com.crownfall.stronghold` application ID (version 214); its workflows must not be confused with Unreal builds.
- M128 GooglePAD candidate source has explicit `GooglePAD`, `bPackageDataInsideApk=False`, `bEnablePlugin=True`; no new Android UE compile/cook/run of M128/M131/M132 has occurred.
- Play screenshot for 218 confirms `obbassets` delivered **Install-time**. This is not proof of pack mounting/runtime read success.
- Android vitals filtered view had no reports, but no Java/native trace of crash.

## Safe next gate

1. On the original **trusted** VM workspaces, first compare only **hashes** of M63 and M84/M106 `Content/Maps/TestMap.umap` to GitHub known blob and to each other; NEVER upload/reveal JKS or private config. File hash output is not sufficient to assert runtime, but can distinguish divergent map sources.
2. If authentic original map is UE loadable (documented M85), use **that** as the source of a future *isolated* new test build, not the failed GitHub blob. No changes to canonical map in place.
3. Verify actively delivered Play Internal Testing versionCode (the bundle inspector's existence of 218 is not equivalent to tester-installed code).
4. Obtain first failure evidence via an authorized independent/cloud test environment (no personal phone access), with a Play-faithful install-time asset-pack setup. Choose one hypothesis based on the first fatal stack.
5. Only when explicitly commissioning a build (and determining VM access and budget), use isolated copy, full Unreal Build/Cook/Stage/Package from verified VM source and an unused versionCode >218. Never merge or publish without runtime test.

## Actions / boundaries

- No project/source/map artifact changed by M132 except additions to read-only guard script, its synthetic test, this documentation, and source-only CI workflow.
- `main`, `m66`, `m128`, `m131` untouched.
- No credentials/keystore inspected or leaked. No VM, Play upload, UE compile, cook, APK/AAB, personal device, or cloud testing performed.
- Critical unresolved point: **Android version 218 launch failure** remains unproven in cause. M132 demonstrates correct and falsifiable source-level test instrumentation and a legitimate historical binary-source blocker.
