# CROWNFALL: Stronghold 2.1.2 — Final Google Play readiness

Production identity:
- Package: `com.crownfall.stronghold`
- Version name: `2.1.2`
- Version code: `214`
- Compile SDK: `36`
- Target SDK: `36`
- Minimum SDK: `23`
- App label: `CROWNFALL: Stronghold`
- Launch activity: `com.crownfall.stronghold.MainActivity`

## Current QA status

PASS:
- Production source assertions
- JavaScript syntax
- Android release lint
- Release AAB build
- ZIP integrity
- bundletool validation
- AAB-derived APK generation
- Package/version metadata
- No INTERNET permission
- Android installation
- Cold launch
- MainActivity top-resumed state
- Process-alive check
- Visual render of the launch screen
- Start-button visual transition into the kingdom
- Runtime crash/ANR/console-error scan

Latest successful QA:
- GitHub Actions run: `37581748639`
- Evidence artifact: `CROWNFALL-2.1.2-Production-QA-Evidence`
- Artifact ID: `11464908414`
- Artifact digest: `sha256:16348b3c6d0e43f9310e05d491f2995b3d262d0ae63b0c71ea2f7f37c001cb9f`

## Signed internal-test bundle

Use the AAB signed with the existing CROWNFALL Google Play upload key.
Expected upload-certificate SHA-1:
`60:15:C8:63:D5:84:BF:FB:71:1B:4F:B1:65:A6:31:C7:43:70:93:5C`

Never upload PhoneTest, DebugPhone, PhonePreview, or diagnostic APKs to the Play testing track.

## Remaining external tasks

- Upload the signed versionCode 214 AAB to Play Console > Internal testing.
- Add tester email addresses and publish the internal-testing release.
- Collect real-device feedback on touch, sound, building placement, campaign, combat, performance, and save persistence.
- A public HTTPS privacy-policy URL and developer privacy contact remain required before the store/policy setup is finalized.
- If the developer account is a new personal account created after November 13, 2023, production access later requires a qualifying closed test; internal testing itself is the recommended first QA track.
