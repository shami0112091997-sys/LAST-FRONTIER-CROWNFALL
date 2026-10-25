# M130 — CROWNFALL Stronghold: deep source audit (read-only evidence, 25 October 2026)

**Branch:** `m130-source-audit-report-only`, isolated successor of M129/M128.  
**Scope:** actual tracked Unreal C++, map asset metadata, Unreal/Android configs, M106/M118/M121–M128 scripts and reports, competing Android WebView build workflows.  
**NO BUILD / COOK / EXECUTION / GITHUB ACTIONS / PLAY UPLOAD / SIGNING / PHONE / VM.** Findings distinguish source facts from runtime hypotheses. No claims that these are the established cause of the version 218 Android exit.

## Executive judgement

**Known observation:** Google Play app reaches Unreal splash then returns to home within ~1s according to the owner. Exact `versionCode` installed on the tested phone is **not independently read**, even though the Play Console bundle inspector displayed AAB 218.

**New information from Play Console screenshots:** the bundle inspector shows `obbassets` delivery **Install-time**. That makes "fast-follow assets haven't finished downloading" a weak explanation, but does **NOT** verify that UE successfully mounted/opened the OBB and archives. In the inspected 28-day Android vitals Crashes/ANRs view, no matching reports were listed; Pre-launch report had no inspected crash evidence. Zero reports != zero crashes.

**Root cause:** UNDETERMINED without the actual first-failure native/Java trace or equivalent trusted runtime evidence. Static mistakes below are genuine engineering issues but must NOT be mistaken for proved causes of the 218 crash.

## Finding register

### F01 — AI enemies have no explicit controller/movement activation (high priority gameplay defect)

**Evidence:** `LastFrontier_Build_001/Source/LastFrontier/Private/Enemy/LFEnemy.cpp:11–18,39–63` creates a Character and only uses `AddMovementInput(...)` at line 57; no explicit `AutoPossessAI`, `AIControllerClass`, `SpawnDefaultController`, or `bRunPhysicsWithNoController`. `.../Private/World/LFWorldDirector.cpp:205–225` calls `SpawnActor<ALFEnemy>` six times at runtime without attaching a controller. The associated header likewise has no controller policy.

**Conclusion:** this path does not *ensure* the spawned enemies can move. Epic documents that spawned pawns are not generally auto-possessed, and CharacterMovement normally aborts walking if it has no controller unless explicitly configured otherwise. Verify actual engine defaults/blueprint overrides before declaring every enemy immobile. **Not a cause of splash exit.**

**Safe eventual patch idea, NOT APPLIED:** select a deliberate AI possession policy (e.g. `AutoPossessAI=EAutoPossessAI::PlacedInWorldOrSpawned` with an appropriate AIController), or deliberately choose controllerless movement with `bRunPhysicsWithNoController=true`; test chase on target build. Do not change both without a reason.
Docs: https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/EAutoPossessAI and https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UCharacterMovementComponent

### F02 — Synchronous world construction at startup (verified pattern; runtime impact unmeasured)

**Evidence:** `.../Private/Core/LFGameMode.cpp:18–27` spawns `ALFWorldDirector`. Its `BeginPlay` at `.../Private/World/LFWorldDirector.cpp:31–41` calls all world-build methods synchronously.

From the counted static loop extents in `LFWorldDirector.cpp`: **80** `AStaticMeshActor` spawn attempts (13 ground/roads, 43 stronghold/city, 24 industrial/crates), **18** `APointLight`, **1** directional light, **1** skylight, **1** height fog, **6** enemies = **107** spawn attempts from the director, before counting the director itself/player. Each attempted spawn's runtime success is not verified. The lights are created during gameplay without any Android device profiling.

**Conclusion:** potential main-thread startup latency, mobile shader/light cost, memory pressure and failure to complete first frame. No proof of OOM, ANR, or native crash. The size of `Content/Maps/TestMap.umap` in the GitHub tree is **6,295 bytes**; serialized strings include WorldSettings/TestMap and no explicit PlayerStart/WorldDirector string found in a bounded ASCII scan, **not** a full Unreal package semantic parse or proof of an empty world.

**Safe eventual check:** instrument durations of each of the five startup blocks, number of successful spawns, and light count on a **separate** verified development build; use Unreal Insights/Android profiling. Defer mobile-light/shader changes until a real benchmark.
Docs: https://dev.epicgames.com/documentation/unreal-engine/performance-guidelines-for-mobile-devices-in-unreal-engine

### F03 — Game UI performs all-enemy actor lookup each DrawHUD (verified inefficiency)

**Evidence:** `.../Private/UI/LFHUD.cpp:10–36`, `UGameplayStatics::GetAllActorsOfClass(...ALFEnemy...)` is called on every HUD draw, and status string rebuilt. Cost scales with world size/draw frequency. **Likely performance issue**, not demonstrable immediate exit. Eventually cache tracked enemies using spawn/death events or an authoritative counter; require tests.

### F04 — Two different Android applications share package ID (high risk of wrong build)

**Evidence:** Unreal `.../Config/DefaultEngine.ini:19–30` defines `PackageName=com.crownfall.stronghold`. Independent `CROWNFALL_Stronghold_Android/app/build.gradle.kts:15–24` defines the **same** `applicationId`, but `versionCode=214`, `versionName=2.1.2`, and WebView `MainActivity.java` loads `file:///android_asset/www/index.html`. `.github/workflows/crownfall-android-build.yml:1,80–82` named `CROWNFALL Google Play Release` builds **this WebView module**, not Unreal. `.github/workflows/crownfall-production-qa.yml` likewise tests the WebView app.

**Conclusion:** confirmed release-path ambiguity. Operators can upload/test or mistake the WebView build for Unreal if they choose the wrong workflow. The fact that the observed app displayed an Unreal splash suggests the particular tested app came from the Unreal pipeline, NOT proof of a WebView crash. **DO NOT RUN** these workflows as a fix for 218.

**Safeguard:** future release gates should explicitly assert the Unreal bundle's UE libraries/assets, application ID, versionCode and signing identity. Rename/retire wrong-path workflows only after owner approval and separate review.

### F05 — GitHub source != build 218's actual settings (verified provenance mismatch)

**Evidence:** `LastFrontier_Build_001/Config/DefaultEngine.ini:21` says `StoreVersion=215`; `.../Scripts/M106_Prepare_Distribution_Sandbox.sh:23–25` requires `StoreVersion=218` in VM source. `M128` report confirms GitHub descriptor/settings aren't verbatim M106.

**Conclusion:** the GitHub tree is not an exact snapshot of the original Google Play 218 release. Any GitHub PAD/SDK/config observation **cannot be promoted to actual-bundle evidence**. Proposed safe action: compare **non-secret** relevant fields and actual SHA-256 digest or generated manifest from authentic M106, without distributing signed files/secrets.

### F06 — Build/cook reuse creates an important provenance question (historical verified; not a defect proven)

**Evidence:** `M106_Prepare_Distribution_Sandbox.sh:39–75` copies existing `Saved/Cooked` and `Binaries/Android` from its source, only excluding selected staged/derived artifacts. M124/M125 historical reports say M119 uses UAT `-skipbuild -skipcook` to stage/package previously produced Shipping outputs. The exact original output hashes/engine plugin Java code aren't accessible in this audit.

**Conclusion:** old cook/binaries are *intentionally* reused. This does **not automatically make the 218 AAB invalid**, but is precisely why enabling GooglePAD later requires proper rebuild/cook/package in a new isolated worktree; do **not** transplant GitHub's `DefaultEngine.ini` over M106 (also carries signing configuration). No build authorized or performed.

### F07 — M128 PAD source candidate is consistent in principle, not tested or proven

**Evidence:** `LastFrontier.uproject:13–18` contains `DisableEnginePluginsByDefault=true` with an explicit `GooglePAD` enablement; `Config/DefaultEngine.ini:29–33` says `bPackageDataInsideApk=False` and runtime `bEnablePlugin=True`; `Docs/M128_...md` identifies this as a candidate. Epic Unreal 5.8 documents these choices for GooglePAD install-time OBB/AAB.

**Conclusion:** static candidate plausibility yes; actual Java/UPL/JNI integration, success of build, installation, OBB mount and on-device runtime **UNKNOWN**. The Play screenshot shows `obbassets=Install-time` for 218, so no assumption of delayed download should be used to motivate change.
Docs: https://dev.epicgames.com/documentation/unreal-engine/using-google-play-asset-delivery-in-unreal-engine and https://developer.android.com/guide/playcore/asset-delivery

### F08 — Unreal 5.8 Android toolchain vs project API should be checked, not blamed

**Evidence:** `Config/DefaultEngine.ini:22–28` chooses `MinSDKVersion=26`, `TargetSDKVersion=36`, ARM64 and Vulkan. Unreal's 5.8 recommended tested Android SDK is 35, NDK r27c, JDK 21.0.3; `M106` actual SDK/NDK/JDK environment not inspected. A target SDK of 36 by itself **does not prove a crash**. Play bundle inspector showed ARM64 and 16KB support; those are packaging/compatibility observations, not a launch test.
Docs: https://dev.epicgames.com/documentation/en-us/unreal-engine/android-development-requirements-for-unreal-engine

### F09 — Limited first-frame Android rendering exposure (plausible, unproved)

**Evidence:** source `bSupportsVulkan=True`; startup initializes many game Actors including point lights/fog. The exact GPU driver/backend selected on the user's Android device and crash events are not accessible. Even a successful ARM64, install-time asset pack, or Play validation does not confirm native initialization.

**Decision tests:** log evidence containing `VK_ERROR`, `RHIInit`, `ShaderCodeLibrary`, `PakFile`, `dlopen failed`, `UnsatisfiedLinkError`, `SIGSEGV`/`SIGABRT`, JNI `NoSuchMethodError`. Do not disable Vulkan blindly or change multiple confounders together.

### F10 — Static analyzers are limited evidence, not successful app tests

**Evidence:** `Scripts/M121_`, `M122_`, `M124_`, `M125_`, `M126_` read the AAB or sample logs, compute statuses, and explicitly flag absence of runtime proof. M127 did fix test-discovered false confidence in the DEX parser regarding wrong method owner and `Available()Z` signature; prior 14+6 checks used **synthetic DEX fixtures**. The real 218 AAB and Android process trace were **not provided to this audit**.

**Limits:** `M126` checks method names/class ownership and one known `Available()Z` signature, not every JNI signature or actual call graph. Seeing raw method strings, method IDs or compatible runtime signatures still does not establish a crash cause.

### F11 — Separate Android/WebView CI propagates signing env to later steps (security review, not crash)

**Evidence:** `.github/workflows/crownfall-android-build.yml:59–82` writes `CROWNFALL_KEYSTORE_PASSWORD` and `CROWNFALL_KEY_PASSWORD` through `$GITHUB_ENV` to future steps. No secret values were read. This is a separate WebView release workflow and is not responsible for AAB 218 per available evidence; avoid enabling it for the Unreal diagnosis. If maintained, review step/job isolation, least privilege, secret masking, artifact retention and signing strategy before any production use.

## Most valuable no-phone sequence

1. **Confirm track provenance:** from Google Play Console's Internal Testing release detail, determine which exact versionCode was actively rolled out and available to the tester on the failure date. The bundle inspector alone displaying 218, especially if marked Draft, doesn't establish what version was installed.
2. **Inspect already-stored Play artifacts:** App Bundle Explorer can show delivery configuration (confirmed `obbassets/install-time`) and, if available, generated APKs/manifest; do not imply AAB bytes were actually downloaded from Console here. Avoid treating Google Play's validation as runtime validation.
3. **If original 218 AAB still exists in user's authorized VM**, inspect it with the corrected **read-only** M125/M126 tools after reviewing them and confirming the AAB hash and input paths. Relevant targets: module delivery manifest, classes.dex method owner/signatures, native GooglePAD JNI names, UE pak/ucas/utoc payload. Tool status remains forensic only, not a runtime crash explanation.
4. **Prefer remote testing from appropriately provisioned isolated Google/Android test environment** once user separately approves cost/privacy and a valid Play-delivered installation path is available. A raw universal APK test that omits install-time splits is *not* equivalent to Play delivery. No such environment was used in this audit.
5. Before fixes, obtain a trustworthy first-failure stack or equivalent crash diagnostic **without requiring access to the user's personal phone** (e.g. controlled independent test device/cloud test). No such trace exists yet. Then address exactly one proven fault per test.
6. Only after separate approval: create a new isolated sandbox from verified M106, apply the minimal change set required, run full Build/Cook/Package (not stale `-skipbuild -skipcook` blindly), validate new versionCode **greater than 218 and unused**, signature, UE payload, ARM64/16KB, and successful Android scene entry. Internal Testing only.

## Read-only execution status and conclusions

- GitHub source and histories: **reviewed**. Binary `TestMap.umap`: GitHub blob size 6,295 bytes and its limited ASCII name-table strings inspected, not loaded with Unreal or cooked.
- Actual 218 AAB bytes, its Play generated APKs, Google Console session, VM, Kimi agent execution, signed files, first crash stack: **NOT ACCESSED**.
- Android runtime, compile, cook, BuildCookRun, Google Play, GitHub Actions: **NOT EXECUTED**.
- Files changed outside this M130 report: **NONE**; `main`, `m66`, `m128`, JKS, Play unchanged.
- One-sentence conclusion: **Fixable gameplay/performance/release-provenance issues exist in repository source, but the root cause of the 218 splash exit remains unknown.** Next highest-value evidence is the exact installed track version and first runtime failure from an authorized independent test.
