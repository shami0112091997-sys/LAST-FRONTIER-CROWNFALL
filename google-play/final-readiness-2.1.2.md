# CROWNFALL: Stronghold 2.1.2 — Google Play AAB verification

Production identity:
- Package: `com.crownfall.stronghold`
- Version name: `2.1.2`
- Version code: `212`
- Compile SDK: `36`
- Target SDK: `36`
- Minimum SDK: `23`
- App label: `CROWNFALL: Stronghold`
- Launch activity: `com.crownfall.stronghold.MainActivity`

Google Play style bundle verification:
- Production AAB built successfully from the current main branch.
- `bundletool 1.18.2` successfully generated a universal APK from that AAB.
- Universal APK signature verification passed using a temporary smoke-test key. The production AAB upload key remains unchanged.
- AAB-derived APK installed successfully on an Android API 35 emulator.
- Cold launch returned `Status: ok`.
- MainActivity launched successfully.
- App process remained alive after launch.
- WebView 124 initialized and launched its sandboxed process.
- No `FATAL EXCEPTION`, `AndroidRuntime FATAL`, or `ANR in com.crownfall.stronghold` was found in the captured runtime log.
- The generated APK did not declare `android.permission.INTERNET`.

Evidence:
- GitHub Actions run: `37517204620`
- Workflow conclusion: `success`
- Evidence artifact: `CROWNFALL-2.1.2-Play-AAB-Smoke-Evidence`
- Artifact ID: `11437079745`
- Artifact digest: `sha256:a6070635722b3d4d76bbcc3ce47f4d51cf2bd9616ca3ef6f0fa728cf7f47a7aa`

Note:
The headless emulator screenshot is not used as a visual-quality assertion because GPU/WebView rendering in the headless emulator can produce a black capture. Visual store screenshots are kept separately from actual game captures. Runtime and WebView initialization are verified through Android process/activity state and log evidence.
