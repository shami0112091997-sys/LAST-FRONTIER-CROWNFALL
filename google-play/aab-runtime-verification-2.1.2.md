# CROWNFALL: Stronghold 2.1.2 — Google Play AAB runtime verification

Production package: `com.crownfall.stronghold`  
Version name: `2.1.2`  
Version code: `212`  
Target SDK: `36`

Verification run: GitHub Actions run `37517204620`

## What was verified

- Production identity validation passed.
- Release AAB build passed.
- The AAB was processed through Google's bundletool 1.18.2.
- A universal APK derived from the AAB was generated successfully.
- The derived APK reported:
  - package: `com.crownfall.stronghold`
  - versionCode: `212`
  - versionName: `2.1.2`
  - compileSdkVersion: `36`
- The derived APK installed successfully on an Android emulator.
- Android launched `com.crownfall.stronghold/.MainActivity` with `Status: ok`.
- The app process remained running after launch.
- Runtime log validation found no `FATAL EXCEPTION` and no `ANR in com.crownfall.stronghold`.
- Final smoke result: `CROWNFALL_PLAY_AAB_SMOKE_PASS`.

## Scope

This verifies the production Android bundle path and runtime startup behavior from an APK generated from the AAB. Store policy declarations, privacy-policy hosting, and Play Console account verification remain separate publishing requirements.
