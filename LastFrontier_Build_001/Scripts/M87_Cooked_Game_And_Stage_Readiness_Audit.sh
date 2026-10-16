#!/usr/bin/env bash
# M87: no writes: validate output of M86 before Stage/PAK. No cloud operations.
set -u
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
W="$HOME/crownfall/M84_EDITOR_SANDBOX_v218"
C="$W/Saved/Cooked/Android_ASTC/LastFrontier/Content"
L="$HOME/crownfall/M86_ANDROID_ASTC_COOK.log"
echo '=== M87 READ ONLY COOK/STAGE PREFLIGHT ==='
if [ ! -s "$L" ] || [ ! -s "$C/Maps/TestMap.umap" ]; then
 echo 'M87_COOK=BLOCKED_NO_MAP_OR_LOG'
 exit 2
fi
if cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap"; then echo 'M87_SOURCE_MAP=PASS'; else echo 'M87_SOURCE_MAP=FAIL'; exit 2; fi
if grep -Eq 'Success - 0 error\(s\)' "$L"; then echo 'M87_LOG_NO_ERRORS=PASS'; else echo 'M87_LOG_NO_ERRORS=NOT_CONFIRMED'; fi
echo '=== TARGET / EXECUTABLE ==='
grep -E '^(GameDefaultMap|PackageName|StoreVersion|TargetSDKVersion|bBuildForArm64|bEnableBundle|bPackageDataInsideApk)=' "$W/Config/DefaultEngine.ini" || true
if [ -s "$W/Binaries/Android/LastFrontier-Android-Shipping-arm64.so" ]; then echo 'M87_ANDROID_SHIPPING_SO=EXISTS'; else echo 'M87_ANDROID_SHIPPING_SO=MISSING'; fi
echo '=== COOKED GAME CONTENT ==='
printf 'M87_COOKED_GAME_FILES='
find "$C" -type f | wc -l
printf 'M87_COOKED_GAME_BYTES='
du -sb "$C" | awk '{print $1}'
find "$C" -type f -printf '%P | %s bytes\n' | head -n 18
echo '=== COOK OUTPUT SUMMARY ==='
du -sh "$W/Saved/Cooked/Android_ASTC" 2>/dev/null || true
grep -E 'Packages Cooked:|Packages Skipped by Platform:|Success - 0 error' "$L" | tail -n 5 || true
echo '=== AVAILABLE SPACE ==='
df -h "$W" | tail -n 1
echo 'M87_READONLY_COMPLETE=YES'
