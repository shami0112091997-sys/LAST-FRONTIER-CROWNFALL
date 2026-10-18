#!/usr/bin/env bash
# CROWNFALL M116 revision 2: READ ONLY release readiness audit.
# Never builds, signs, asks for credentials, edits files, or prints secret values.
set -Eeuo pipefail
export LC_ALL=C
ROOT="${M116_ROOT:-$HOME/crownfall/M106_RELEASE_SANDBOX_v218}"
UE="${M116_UE_ROOT:-$HOME/UE_5.8.3}"
INI="$ROOT/Config/DefaultEngine.ini"
GAME="$ROOT/Config/DefaultGame.ini"
KEY="$ROOT/Build/Android/CROWNFALL_v0.8_upload_key.jks"
EXPECTED_JKS_SHA256='b4822980977b29f6106187f5f5e1c6480075fdfe08c210897a202ccf2da11b8b'

block() {
    printf 'M116_GATE=BLOCKED:%s\n' "$1"
    printf 'M116_ACTION_BUILD_STARTED=NO\n'
    exit 2
}
require_nonempty() { [[ -f "$1" && -s "$1" ]] || block "$2"; }
require_line() { grep -Fqx -- "$2" "$1" || block "$3"; }

printf 'M116_AUDIT_MODE=READ_ONLY\n'
require_nonempty "$ROOT/LastFrontier.uproject" PROJECT_MISSING
require_nonempty "$INI" ENGINE_CONFIG_MISSING
require_nonempty "$GAME" GAME_CONFIG_MISSING
require_nonempty "$ROOT/Content/Maps/TestMap.umap" ORIGINAL_MAP_MISSING
require_nonempty "$ROOT/Saved/Cooked/Android_ASTC/LastFrontier/Content/Maps/TestMap.umap" COOKED_MAP_MISSING
require_nonempty "$ROOT/Binaries/Android/LastFrontier-Android-Shipping-arm64.so" SHIPPING_BINARY_MISSING
[[ -f "$UE/Engine/Build/BatchFiles/RunUAT.sh" && -x "$UE/Engine/Build/BatchFiles/RunUAT.sh" ]] || block UAT_MISSING
printf 'M116_PROJECT_CONTENT_AND_TOOLS=PASS\n'

require_line "$GAME" 'ForDistribution=True' FOR_DISTRIBUTION_NOT_SET
require_line "$GAME" 'BuildConfiguration=PPBC_Shipping' SHIPPING_NOT_SET
require_line "$INI" 'PackageName=com.crownfall.stronghold' PACKAGE_NAME_MISMATCH
require_line "$INI" 'StoreVersion=218' VERSION_CODE_MISMATCH
require_line "$INI" 'TargetSDKVersion=36' TARGET_SDK_MISMATCH
require_line "$INI" 'bEnableBundle=True' BUNDLE_NOT_ENABLED
printf 'M116_ANDROID_DISTRIBUTION_METADATA=PASS\n'

# Existence, provenance and file permissions only; never keytool and never private-key output.
[[ ! -L "$KEY" ]] || block KEYSTORE_SYMLINK_NOT_ALLOWED
require_nonempty "$KEY" KEYSTORE_NOT_FOUND
[[ "$(stat -c '%u' -- "$KEY")" == "$(id -u)" ]] || block KEYSTORE_WRONG_OWNER
mode="$(stat -c '%a' -- "$KEY")"
[[ "$mode" =~ ^[0-7]{3,4}$ ]] || block KEYSTORE_MODE_UNRECOGNIZED
(( (8#$mode & 077) == 0 )) || block KEYSTORE_PERMISSIONS_TOO_BROAD
actual="$(sha256sum -- "$KEY")" || block KEYSTORE_UNREADABLE
actual="${actual%% *}"
[[ "$actual" == "$EXPECTED_JKS_SHA256" ]] || block KEYSTORE_SHA256_MISMATCH
printf 'M116_ORIGINAL_KEY_FILE=PASS\n'

[[ ! -e "$ROOT/Intermediate/Android" && ! -L "$ROOT/Intermediate/Android" ]] || block ANDROID_INTERMEDIATE_REVIEW_NEEDED
printf 'M116_ANDROID_INTERMEDIATE=CLEAN\n'

# Metadata-only evaluation: do not source, echo or hash the INI when it may hold secrets.
if grep -Eq '^[[:space:]]*KeyStore[[:space:]]*=' "$INI"; then
    grep -Eq '^[[:space:]]*KeyStore[[:space:]]*=[[:space:]]*CROWNFALL_v0[.]8_upload_key[.]jks[[:space:]]*$' "$INI" || block KEYSTORE_CONFIG_MISMATCH
    printf 'M116_KEYSTORE_CONFIG=SET\n'
else
    printf 'M116_KEYSTORE_CONFIG=MISSING\n'
fi
if grep -Eq '^[[:space:]]*KeyAlias[[:space:]]*=' "$INI"; then
    grep -Eq '^[[:space:]]*KeyAlias[[:space:]]*=[[:space:]]*crownfall-upload[[:space:]]*$' "$INI" || block KEY_ALIAS_MISMATCH
    printf 'M116_KEY_ALIAS=SET\n'
else
    printf 'M116_KEY_ALIAS=MISSING\n'
fi
if grep -Eq '^[[:space:]]*KeyStorePassword[[:space:]]*=[[:space:]]*[^[:space:]#;]+' "$INI"; then
    ini_mode="$(stat -c '%a' -- "$INI")"
    [[ "$ini_mode" =~ ^[0-7]{3,4}$ ]] || block SECRET_CONFIG_MODE_UNKNOWN
    (( (8#$ini_mode & 077) == 0 )) || block SIGNING_PASSWORD_IN_ACCESSIBLE_CONFIG
    printf 'M116_SIGNING_PASSWORD=SET_PRIVATE_CONFIG_REVIEW_REQUIRED\n'
else
    printf 'M116_SIGNING_PASSWORD=NOT_CONFIGURED\n'
fi
# A missing KeyPassword is allowed by Epic if it equals the store password.
printf 'M116_KEY_PASSWORD=OPTIONAL_IF_SAME_AS_STORE\n'
printf 'M116_ACTION_BUILD_STARTED=NO\n'
printf 'M116_AUDIT_COMPLETE=PASS\n'
printf 'M116_RELEASE_BUILD_AUTHORIZED=NO\n'
printf 'M116_GATE=HOLD_FOR_PRIVATE_SIGNING_SETUP\n'
exit 3
