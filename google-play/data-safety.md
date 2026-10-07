# Google Play Data safety — CROWNFALL: Stronghold 2.1.2

Production package: `com.crownfall.stronghold`
Version: 2.1.2
Version code: 214

## Recommended Play Console answers

- Does the app collect or share any of the required user data types? **No**
- Is all user data encrypted in transit? **Not applicable — the app does not transmit user data**
- Does the app provide a way for users to request deletion? **Not applicable — no account or remotely collected user data**
- Does the app contain ads? **No**
- Does the app require account creation? **No**
- Does the app use analytics? **No**
- Does the app use third-party advertising or tracking SDKs? **No**
- Does the app transmit gameplay progress to a server? **No**
- Is gameplay progress stored locally on the device? **Yes**
- Can the user remove locally stored progress? **Yes — by clearing app data or uninstalling the app**

## Technical basis checked in production source

- No INTERNET permission is declared in the Android manifest.
- The WebView loads local content from `file:///android_asset/www/index.html`.
- Production validation rejects network URLs, Firebase, analytics, ads, and WebSocket markers in the game asset.
- Local progress uses on-device browser storage.
- No login or account system is present.

Re-check these answers if networking, analytics, ads, accounts, cloud saves, crash reporting, or third-party SDKs are added later.