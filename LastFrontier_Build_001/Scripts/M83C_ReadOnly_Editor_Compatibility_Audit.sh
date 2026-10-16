#!/usr/bin/env bash
# M83C: comparison only. Never copies modules, runs Unreal, or edits any file.
set -u
O="$HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
E="$HOME/UE_5.8.3"
echo '=== M83C SOURCE AND ASSET MATCH ==='
for F in Source Content; do
  if [ ! -d "$O/$F" ] || [ ! -d "$D/$F" ]; then echo "M83C_${F}=MISSING"
  elif diff -qr "$O/$F" "$D/$F" >/dev/null 2>&1; then echo "M83C_${F}=MATCH"
  else echo "M83C_${F}=DIFFERENT"; diff -qr "$O/$F" "$D/$F" 2>/dev/null | head -n 8; fi
done
echo '=== EDITOR MODULE BUILD IDS ==='
for F in "$E/Engine/Binaries/Linux/UnrealEditor.modules" "$O/Binaries/Linux/UnrealEditor.modules" "$P/Binaries/Linux/UnrealEditor.modules"; do
  if [ -s "$F" ]; then
    echo "MODULE_FILE=$F"
    grep -m1 -o '"BuildId"[[:space:]]*:[[:space:]]*"[^"]*"' "$F" || true
    grep -m2 'LastFrontier' "$F" || true
  else echo "MISSING_MODULE_FILE=$F"; fi
done
echo '=== ACTUAL M70 EDITOR DLLS ==='
find "$O/Binaries/Linux" -maxdepth 1 -type f -name 'libUnrealEditor-LastFrontier*.so' -printf '%f | %s bytes\n' 2>/dev/null | head -n 10
echo '=== RELEASE CONFIG ==='
grep -E '^(GameDefaultMap|PackageName|StoreVersion|TargetSDKVersion)=' "$D/Config/DefaultEngine.ini" || true
grep -E '^ProjectVersion=' "$D/Config/DefaultGame.ini" || true
if cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap"; then echo 'M83C_ORIGINAL_MAP=PASS'; else echo 'M83C_ORIGINAL_MAP=FAIL'; fi
echo 'M83C_READONLY_COMPLETE'
