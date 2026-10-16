#!/usr/bin/env bash
# M90: QA-only packaging from validated M84 stage. NEVER upload output to Google Play.
set -u
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
W="$HOME/crownfall/M84_EDITOR_SANDBOX_v218"
E="$HOME/UE_5.8.3"
S="$W/Saved/StagedBuilds/Android_ASTC/LastFrontier/Content/Paks"
L="$HOME/crownfall/M90_ANDROID_QA_PACKAGE.log"
stop(){ echo "M90_BLOCKED=$1"; exit 2; }
[ ! -e "$L" ] || stop EXISTING_LOG
[ -x "$E/Engine/Build/BatchFiles/RunUAT.sh" ] || stop MISSING_UAT
[ -s "$W/LastFrontier.uproject" ] || stop MISSING_PROJECT
[ -s "$W/Saved/Cooked/Android_ASTC/LastFrontier/Content/Maps/TestMap.umap" ] || stop MISSING_COOKED_MAP
[ -s "$W/Binaries/Android/LastFrontier-Android-Shipping-arm64.so" ] || stop MISSING_ANDROID_BINARY
for F in global.ucas global.utoc LastFrontier-Android_ASTC.pak LastFrontier-Android_ASTC.ucas LastFrontier-Android_ASTC.utoc; do
  [ -s "$S/$F" ] || stop "MISSING_STAGE_ARCHIVE:$F"
done
for X in 'StoreVersion=218' 'PackageName=com.crownfall.stronghold' 'TargetSDKVersion=36' 'bEnableBundle=True'; do grep -Fqx "$X" "$W/Config/DefaultEngine.ini" || stop "INVALID_CONFIG:$X"; done
cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap" || stop M84_MAP_CHANGED
cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" || stop M77_MAP_CHANGED
if find "$W/Binaries/Android" -maxdepth 1 -type f \( -iname '*.aab' -o -iname '*.apk' \) -print -quit | grep -q .; then stop PACKAGE_ALREADY_EXISTS; fi
K=$(df -Pk "$W" | awk 'END{print $4}')
[[ "$K" =~ ^[0-9]+$ ]] || stop DISK_UNKNOWN
((K >= 30*1024*1024)) || stop NEED_30GIB_FREE
echo "M90_PREFLIGHT=PASS"
echo "M90_MODE=QA_ONLY_NOT_FOR_PLAY"
timeout --kill-after=20s 2700 "$E/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun \
  -project="$W/LastFrontier.uproject" -noP4 \
  -platform=Android -cookflavor=ASTC -clientconfig=Shipping \
  -skipbuild -skipcook -skipstage -skippak -package -unattended -utf8output > "$L" 2>&1
R=$?
echo "M90_UAT_EXIT=$R"
echo "=== OUTPUT ==="
find "$W/Binaries/Android" -maxdepth 2 -type f \( -iname '*.aab' -o -iname '*.apk' \) -printf '%p | %s bytes\n' 2>/dev/null | head -n 15 || true
echo "=== ERRORS ==="
grep -Ei 'AutomationTool exiting|Error:|Fatal error|Exception:' "$L" | tail -n 14 || true
if cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap" && cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap"; then echo "M90_MAP_INTEGRITY=PASS"; else echo "M90_MAP_INTEGRITY=FAIL"; fi
echo "M90_LOG=$L"
echo "M90_UPLOAD=NOT_PERFORMED"
