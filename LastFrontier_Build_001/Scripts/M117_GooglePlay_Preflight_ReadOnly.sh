#!/usr/bin/env bash
# CROWNFALL M117: Google Play Release preflight; STRICTLY READ ONLY.
# Checks known M106 sandbox, never starts UAT, never prints credentials.
set -uo pipefail
export LC_ALL=C
W="${M117_ROOT:-$HOME/crownfall/M106_RELEASE_SANDBOX_v218}"
UE="${M117_UNREAL_ROOT:-$HOME/UE_5.8.3}"
INI="$W/Config/DefaultEngine.ini"
GAME="$W/Config/DefaultGame.ini"
KEY="$W/Build/Android/CROWNFALL_v0.8_upload_key.jks"
MAP="$W/Content/Maps/TestMap.umap"
COOKED="$W/Saved/Cooked/Android_ASTC/LastFrontier/Content/Maps/TestMap.umap"
BIN="$W/Binaries/Android/LastFrontier-Android-Shipping-arm64.so"
REFERENCE_SHA256='b4822980977b29f6106187f5f5e1c6480075fdfe08c210897a202ccf2da11b8b'
errors=0
warns=0
pass(){ printf 'M117_%s=PASS\n' "$1"; }
fail(){ printf 'M117_%s=BLOCKED\n' "$1"; errors=$((errors+1)); }
warn(){ printf 'M117_%s=REVIEW\n' "$1"; warns=$((warns+1)); }
require_file(){ if [[ -f "$2" && -s "$2" && ! -L "$2" ]]; then pass "$1"; else fail "$1"; fi; }
require_exact(){ if [[ -f "$2" ]] && grep -Fqx -- "$3" "$2"; then pass "$1"; else fail "$1"; fi; }

printf 'M117_MODE=READ_ONLY\n'
require_file PROJECT "$W/LastFrontier.uproject"
require_file MAP "$MAP"
require_file COOKED_MAP "$COOKED"
require_file ARM64_SHIPPING_BINARY "$BIN"
require_file ENGINE_INI "$INI"
require_file GAME_INI "$GAME"
if [[ -x "$UE/Engine/Build/BatchFiles/RunUAT.sh" ]]; then pass UAT; else fail UAT; fi
require_exact PACKAGE_ID "$INI" 'PackageName=com.crownfall.stronghold'
require_exact VERSION_218 "$INI" 'StoreVersion=218'
require_exact TARGET_API_36 "$INI" 'TargetSDKVersion=36'
require_exact ARM64_ENABLED "$INI" 'bBuildForArm64=True'
require_exact APP_BUNDLE "$INI" 'bEnableBundle=True'
require_exact DISTRIBUTION "$GAME" 'ForDistribution=True'
require_exact SHIPPING "$GAME" 'BuildConfiguration=PPBC_Shipping'
if [[ -f "$INI" && ! -L "$INI" && "$(stat -c '%u' -- "$INI" 2>/dev/null)" == "$(id -u)" ]]; then
    perms="$(stat -c '%a' -- "$INI" 2>/dev/null)"
    if [[ "$perms" =~ ^[0-7]{3,4}$ ]] && (( (8#$perms & 077) == 0 )); then pass PRIVATE_CONFIG_FILE; else fail PRIVATE_CONFIG_FILE; fi
else fail PRIVATE_CONFIG_FILE; fi
if [[ -f "$KEY" && ! -L "$KEY" && -s "$KEY" && "$(stat -c '%u' -- "$KEY" 2>/dev/null)" == "$(id -u)" ]]; then
    perms="$(stat -c '%a' -- "$KEY" 2>/dev/null)"
    if [[ "$perms" =~ ^[0-7]{3,4}$ ]] && (( (8#$perms & 077) == 0 )) && [[ "$(sha256sum -- "$KEY" 2>/dev/null | cut -d ' ' -f1)" == "$REFERENCE_SHA256" ]]; then pass ORIGINAL_UPLOAD_KEY; else fail ORIGINAL_UPLOAD_KEY; fi
else fail ORIGINAL_UPLOAD_KEY; fi
if [[ -e "$W/Intermediate/Android" || -L "$W/Intermediate/Android" ]]; then warn ANDROID_INTERMEDIATE_EXISTS; else pass ANDROID_INTERMEDIATE_CLEAN; fi
if [[ -d "$W/Binaries/Android" ]] && find "$W/Binaries/Android" -maxdepth 1 -type f \( -iname '*.aab' -o -iname '*.apk' \) -print -quit 2>/dev/null | grep -q .; then fail AAB_ALREADY_IN_RELEASE_SANDBOX; else pass NO_OLD_RELEASE_BUNDLE; fi
if [[ -f "$INI" ]] && grep -Eq '^[[:space:]]*KeyStorePassword[[:space:]]*=[[:space:]]*[^[:space:]#;]+' "$INI"; then warn SIGNING_PASSWORD_IN_INI_PRIVATE_REVIEW_REQUIRED; else warn SIGNING_PASSWORD_NOT_CONFIGURED; fi
if [[ -f "$INI" ]] && grep -Eq '^[[:space:]]*KeyStore[[:space:]]*=[[:space:]]*CROWNFALL_v0[.]8_upload_key[.]jks[[:space:]]*$' "$INI" && grep -Eq '^[[:space:]]*KeyAlias[[:space:]]*=[[:space:]]*crownfall-upload[[:space:]]*$' "$INI"; then pass SIGNING_KEY_METADATA; else fail SIGNING_KEY_METADATA; fi
avail_kb="$(df -Pk "$W" 2>/dev/null | awk 'END{print $4}')"
if [[ "$avail_kb" =~ ^[0-9]+$ ]] && (( avail_kb >= 30*1024*1024 )); then pass DISK_30_GIB; else fail DISK_30_GIB; fi
if command -v readelf >/dev/null 2>&1 && [[ -s "$BIN" ]]; then
    alignments="$(readelf -W -l -- "$BIN" 2>/dev/null | awk '$1=="LOAD" {print $NF}')"
    if [[ -n "$alignments" ]]; then
        if printf '%s\n' "$alignments" | grep -Eiq '^0x(1000|2000)$'; then warn NATIVE_SO_16K_ALIGNMENT; else pass NATIVE_SO_LOAD_ALIGNMENT_REVIEWED; fi
    else warn NATIVE_SO_ALIGNMENT_UNKNOWN; fi
else warn NATIVE_SO_ALIGNMENT_NOT_TESTED; fi
printf 'M117_PLAY_CONSOLE_VERSION_218_AVAILABILITY=UNVERIFIED\n'
printf 'M117_KEY_EXPOSURE=UPLOAD_KEY_RESET_RECOMMENDED\n'
printf 'M117_ERRORS=%s\nM117_WARNINGS=%s\n' "$errors" "$warns"
printf 'M117_BUILD_STARTED=NO\nM117_PLAY_UPLOAD=NO\n'
if (( errors > 0 )); then printf 'M117_STATUS=BLOCKED\n'; exit 2; fi
printf 'M117_STATUS=PRELIMINARY_READY_REQUIRES_PRIVATE_SIGNING_AND_PLAY_VERSION_CHECK\n'
exit 0