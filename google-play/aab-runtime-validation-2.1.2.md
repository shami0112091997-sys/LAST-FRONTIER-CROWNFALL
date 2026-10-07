# CROWNFALL: Stronghold — Google Play AAB validation

Release: 2.1.2
Version code: 214
Package: com.crownfall.stronghold
Compile SDK: 36
Target SDK: 36
Minimum SDK: 23

Final Google Play-style validation completed successfully on the current production source.

Validated path:
1. Static production assertions passed.
2. Android Lint for the release build passed.
3. Built the production Android App Bundle from the current main branch.
4. Verified production identity: com.crownfall.stronghold / 2.1.2 / 214.
5. Confirmed targetSdk 36 and minSdk 23.
6. Confirmed no INTERNET permission in the generated app.
7. Validated the AAB with Google's bundletool 1.18.2.
8. Generated a universal APK from the AAB and verified its package metadata.
9. Installed the AAB-derived APK on an Android API 35 emulator.
10. Cold-launched com.crownfall.stronghold/.MainActivity successfully.
11. Confirmed the app was the top resumed activity and its process remained running.
12. Visual smoke test passed before and after pressing the Start button.
13. No CROWNFALL fatal exception, app ANR, JavaScript syntax error, or WebView console error was detected during the QA window.

Successful GitHub Actions run:
37581748639

Evidence artifact:
CROWNFALL-2.1.2-Production-QA-Evidence
Artifact ID: 11464908414
Artifact digest:
sha256:16348b3c6d0e43f9310e05d491f2995b3d262d0ae63b0c71ea2f7f37c001cb9f

This report validates the production AAB path for versionCode 214, not PhoneTest/DebugPhone/PhonePreview diagnostic builds.
