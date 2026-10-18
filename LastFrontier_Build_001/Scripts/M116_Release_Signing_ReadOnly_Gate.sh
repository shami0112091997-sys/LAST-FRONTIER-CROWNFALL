#!/usr/bin/env bash
# M116 / READ ONLY: no build, no key extraction, no upload, no writes.
set -Eeuo pipefail
ROOT="$HOME/crownfall/M106_RELEASE_SANDBOX_v218"
UE="$HOME/UE_5.8.3"
INI="$ROOT/Config/DefaultEngine.ini"
GAME="$ROOT/Config/DefaultGame.ini"
KEY="$ROOT/Build/Android/CROWNFALL_v0.8_upload_key.jks"
EXPECTED_JKS_SHA256='b4822980977b29f6106187f5f5e1c6480075fdfe08c210897a202ccf2da11b8b'
fail() { printf 'M116_GATE=BLOCKED:%s\nM116_BUILD_NOT_STARTED=CONFIRMED\n' "$1"; exit 2; }
need() { [[ -s "$1" ]] || fail "$2"; }
need "$ROOT/LastFrontier.uproject" PROJECT_MISSING
need "$INI" ANDROID_CONFIG_MISSING
need "$GAME" DISTRIBUTION_CONFIG_MISSING
need "$ROOT/Binaries/Android/LastFrontier-Android-Shipping-arm64.so" SHIPPING_BINARY_MISSING
need "$ROOT/Saved/Cooked/Android_ASTC/LastFrontier/Content/Maps/TestMap.umap" COOKED_MAP_MISSING
[[ -x "$UE/Engine/Build/BatchFiles/RunUAT.sh" ]] || fail UAT_MISSING
printf 'M116_PROJECT_AND_CONTENT=PASS\n'

# Check the known original key by digest only. Never show its bytes or ask for passwords.
[[ ! -L "$KEY" ]] || fail KEYSTORE_SYMLINK_NOT_ALLOWED
need "$KEY" KEYSTORE_MISSING
key_sha="$(sha256sum -- "$KEY" | cut -d ' ' -f1)"
[[ "$key_sha" == "$EXPECTED_JKS_SHA256" ]] || fail KEYSTORE_DIGEST_MISMATCH
key_mode="$(stat -c '%a' -- "$KEY")"
[[ "$key_mode" =~ ^[0-7]{3,4}$ ]] || fail KEYSTORE_MODE_UNKNOWN
(( (8#$key_mode & 077) == 0 )) || fail KEYSTORE_FILE_TOO_PERMISSIVE
printf 'M116_ORIGINAL_KEY_AND_PERMISSIONS=PASS\n'

for entry in \
  'ForDistribution=True' \
  'BuildConfiguration=PPBC_Shipping'; do
  grep -Fqx -- "$entry" "$GAME" || fail DISTRIBUTION_MODE_MISSING
done
for entry in \
  'PackageName=com.crownfall.stronghold' \
  'StoreVersion=218' \
  'TargetSDKVersion=36' \
  'bEnableBundle=True'; do
  grep -Fqx -- "$entry" "$INI" || fail ANDROID_CONFIG_MISMATCH
done
printf 'M116_DISTRIBUTION_SETTINGS=PASS\n'

# Official Unreal Android distribution signing settings; report names only, never values.
grep -Eq '^[[:space:]]*KeyStore[[:space:]]*=[[:space:]]*CROWNFALL_v0[.]8_upload_key[.]jks[[:space:]]*$' "$INI" || fail KEYSTORE_SETTING_NOT_CONFIGURED
grep -Eq '^[[:space:]]*KeyAlias[[:space:]]*=[[:space:]]*crownfall-upload[[:space:]]*$' "$INI" || fail KEY_ALIAS_NOT_CONFIGURED
grep -Eq '^[[:space:]]*KeyStorePassword[[:space:]]*=[[:space:]]*[^[:space:]#;]+' "$INI" || fail KEYSTORE_PASSWORD_NOT_CONFIGURED
ini_mode="$(stat -c '%a' -- "$INI")"
[[ "$ini_mode" =~ ^[0-7]{3,4}$ ]] || fail SIGNING_CONFIG_MODE_UNKNOWN
(( (8#$ini_mode & 077) == 0 )) || fail SIGNING_CONFIG_TOO_PERMISSIVE
printf 'M116_SIGNING_CONFIG_PRESENT=PASS\n'

if [[ -e "$ROOT/Intermediate/Android" ]]; then
  printf 'M116_GRADLE_STATE=REVIEW_REQUIRED\n'
  fail OLD_OR_NEW_GRADLE_ARTIFACTS_REQUIRE_REVIEW
fi
printf 'M116_GRADLE_STATE=CLEAN\n'
printf 'M116_BUILD_NOT_STARTED=CONFIRMED\nM116_READONLY_GATE=PASS\n'
