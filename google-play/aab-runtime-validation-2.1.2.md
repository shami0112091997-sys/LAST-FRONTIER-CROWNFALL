# CROWNFALL: Stronghold — Google Play AAB validation

Release: 2.1.2
Version code: 212
Package: com.crownfall.stronghold
Target SDK: 36

Final Google Play-style validation completed successfully.

Validated path:
1. Built the production Android App Bundle from the production source.
2. Verified production identity: com.crownfall.stronghold / 2.1.2 / 212.
3. Confirmed targetSdk 36.
4. Confirmed no INTERNET permission in the production manifest.
5. Used Google's bundletool to generate an installable universal APK from the production AAB.
6. Verified the generated APK signature and package metadata.
7. Installed that AAB-derived APK on an Android emulator.
8. Launched com.crownfall.stronghold/.MainActivity successfully.
9. Confirmed the app process remained running and no CROWNFALL fatal exception or app ANR was detected during the smoke window.

Successful GitHub Actions run:
37517204620

Evidence artifact:
CROWNFALL-2.1.2-Play-AAB-Smoke-Evidence
Artifact ID: 11437079745
Artifact digest:
sha256:a6070635722b3d4d76bbcc3ce47f4d51cf2bd9616ca3ef6f0fa728cf7f47a7aa

This report validates the production AAB path, not PhoneTest/DebugPhone/PhonePreview diagnostic builds.
