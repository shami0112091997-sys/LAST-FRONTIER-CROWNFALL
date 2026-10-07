# CROWNFALL: Stronghold 2.1.2 — Google Play AAB runtime verification

Production package: `com.crownfall.stronghold`  
Version name: `2.1.2`  
Version code: `214`  
Compile SDK: `36`  
Target SDK: `36`  
Minimum SDK: `23`

Verification run: GitHub Actions run `37581748639`

## What was verified

- Static production assertions passed.
- Android release lint passed.
- Release AAB build passed.
- The AAB was validated with Google's bundletool 1.18.2.
- A universal APK derived from the AAB was generated successfully.
- The derived APK reported:
  - package: `com.crownfall.stronghold`
  - versionCode: `214`
  - versionName: `2.1.2`
  - compileSdkVersion: `36`
  - targetSdkVersion: `36`
  - minSdkVersion: `23`
- The derived APK declared no `android.permission.INTERNET`.
- The derived APK installed successfully on an Android API 35 emulator.
- Android cold-launched `com.crownfall.stronghold/.MainActivity` with `Status: ok`.
- MainActivity became the top resumed activity.
- The app process remained running.
- The launch screen rendered correctly.
- The Start-button interaction changed the rendered screen and displayed the live kingdom UI.
- Runtime checks found no `FATAL EXCEPTION`, no app ANR, and no captured JavaScript/WebView console error.

## Evidence

- GitHub Actions run: `37581748639`
- Evidence artifact: `CROWNFALL-2.1.2-Production-QA-Evidence`
- Artifact ID: `11464908414`
- Artifact digest: `sha256:16348b3c6d0e43f9310e05d491f2995b3d262d0ae63b0c71ea2f7f37c001cb9f`

## Scope

This verifies the actual production Android bundle path and the first visible game transition from the splash screen into the kingdom. Store policy declarations, privacy-policy hosting, account verification, and human gameplay feedback remain separate Play Console tasks.
