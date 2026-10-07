# CROWNFALL: Stronghold — Internal testing release 214

## Upload artifact

- App: CROWNFALL: Stronghold
- Package: `com.crownfall.stronghold`
- Version name: `2.1.2`
- Version code: `214`
- Track: Google Play Internal testing
- Format: signed Android App Bundle (AAB)
- Upload certificate SHA-1: `60:15:C8:63:D5:84:BF:FB:71:1B:4F:B1:65:A6:31:C7:43:70:93:5C`

## QA gate completed

Current versionCode 214 passed:
- Static production assertions
- JavaScript syntax
- Android release lint
- AAB build
- bundletool validation
- Package/version/SDK checks
- No INTERNET permission
- AAB-derived APK installation
- Cold launch
- Top resumed activity
- Visual launch-screen render
- Start-button visual transition into the kingdom
- Crash/ANR/WebView console error scan

QA run: `37581748639`

## Internal-test release notes

Arabic:
`اختبار داخلي للإصدار 2.1.2 (214): مراجعة البناء والقتال والحملة والصوت والحفظ والأداء على أجهزة Android الحقيقية.`

English:
`Internal test for 2.1.2 (214): validate building, combat, campaign, audio, save persistence, and performance on real Android devices.`

## Tester checklist

Each tester should check:
1. Install from the Google Play opt-in link.
2. Launch and press “دخول المملكة”.
3. Complete the first-session tutorial.
4. Place at least one building and confirm its position.
5. Train at least one guard.
6. Start and finish at least two battles.
7. Open Campaign and enter a campaign battle.
8. Toggle sound off/on.
9. Close and reopen the app; confirm progress is preserved.
10. Report device model, Android version, crashes, freezes, layout problems, touch problems, and perceived performance.

## Play Console path

Test and release > Testing > Internal testing > Create new release.

Upload only the signed versionCode 214 AAB. Add tester emails, review the release, then roll out to internal testing.

Internal testing supports up to 100 testers and can be started before the full app setup is complete.
