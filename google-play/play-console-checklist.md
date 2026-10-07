# CROWNFALL: Stronghold — Google Play publishing checklist

## Production identity
- App name: CROWNFALL: Stronghold
- Package: com.crownfall.stronghold
- Version name: 2.1.2
- Version code: 214
- Target SDK: 36
- Minimum SDK: 23
- Orientation: Landscape
- Distribution artifact: Android App Bundle (AAB)

## Store listing
- Arabic short/full description: prepared in store-listing-ar.txt
- English short/full description: prepared in store-listing-en.txt
- Release notes: prepared in release-notes-2.1.2.txt
- Category recommendation: Games > Strategy
- Ads declaration: No ads

## App content
- Privacy policy: prepared in privacy-policy.html; it still needs a public HTTPS URL for the Play Console field.
- In-app privacy text: included in the production game information panel.
- Data safety draft: prepared in data-safety.md
- Account deletion: not applicable because there is no account system.
- Content rating questionnaire: answer based on fantasy/strategy combat shown in the game; do not claim no violence if battle content is presented.
- Target audience: select the actual intended audience in Play Console; do not mark the app as primarily child-directed unless that is truly intended.

## Technical
- No INTERNET permission.
- No analytics/ad/tracking markers in production asset.
- Startup crash fix retained in MainActivity.
- Release package remains com.crownfall.stronghold.
- Upload only the production AAB. Never upload PhoneTest, DebugPhone, PhonePreview, or APK diagnostic builds.

## Before review
1. Complete developer identity verification in Play Console.
2. Host privacy-policy.html at a public HTTPS URL and enter that URL in Play Console.
3. Upload production AAB.
4. Complete App access, Ads, Content rating, Target audience, Data safety, and privacy-policy fields.
5. Add required store graphics/screenshots from the real game.
6. Use Internal testing first, then promote the same approved build to production when ready.