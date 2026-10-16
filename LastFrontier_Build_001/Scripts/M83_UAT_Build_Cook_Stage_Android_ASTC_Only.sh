#!/usr/bin/env bash
# M83: isolated Android Shipping UAT BUILD+COOK+STAGE+PAK. NO PACKAGE/SIGN/DISTRIBUTION/UPLOAD.
set -u
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
E="$HOME/UE_5.8.3"
L="$HOME/crownfall/M83_ANDROID_ASTC_UAT_STAGE.log"
BLOCKED=""
if [ -e "$L" ]; then BLOCKED="LOG_ALREADY_EXISTS"; fi
if [ -z "$BLOCKED" ] && { [ ! -s "$D/LastFrontier.uproject" ] || [ ! -s "$D/Content/Maps/TestMap.umap" ] || [ ! -s "$P/Content/Maps/TestMap.umap" ] || [ ! -x "$E/Engine/Build/BatchFiles/RunUAT.sh" ]; }; then BLOCKED="REQUIRED_FILE_MISSING"; fi
if [ -z "$BLOCKED" ] && ! cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap"; then BLOCKED="ORIGINAL_MAP_DIFFERS"; fi
if [ -z "$BLOCKED" ]; then
  for LINE in 'PackageName=com.crownfall.stronghold' 'StoreVersion=218' 'TargetSDKVersion=36' 'bBuildForArm64=True' 'bEnableBundle=True'; do
    grep -Fqx "$LINE" "$D/Config/DefaultEngine.ini" || BLOCKED="INVALID_CONFIG:$LINE"
  done
fi
if [ -z "$BLOCKED" ] && [ -n "$(find "$D/Content" -type l -print -quit)" ]; then BLOCKED="SYMLINKED_CONTENT"; fi
K=$(df -Pk "$D" 2>/dev/null | awk 'END{print $4}')
if [ -z "$BLOCKED" ] && { ! [[ "$K" =~ ^[0-9]+$ ]] || [ "$K" -lt 52428800 ]; }; then BLOCKED="DISK_SPACE_BELOW_50_GIB"; fi
if [ -n "$BLOCKED" ]; then echo "M83_PREFLIGHT=BLOCKED:$BLOCKED"; exit 2; fi
BEFORE=$(sha256sum "$P/Content/Maps/TestMap.umap" | cut -d' ' -f1)
echo 'M83_PREFLIGHT=PASS'
echo 'M83_ACTION=BUILD_COOK_STAGE_PAK_ONLY'
echo 'M83_NO_PACKAGE=YES'
echo 'M83_NO_SIGNING=YES'
timeout 3600 "$E/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun \
  -project="$D/LastFrontier.uproject" -noP4 \
  -platform=Android -cookflavor=ASTC -clientconfig=Shipping \
  -build -cook -stage -pak -unattended -utf8output > "$L" 2>&1
R=$?
echo "M83_UAT_EXIT=$R"
if [ "$BEFORE" = "$(sha256sum "$P/Content/Maps/TestMap.umap" | cut -d' ' -f1)" ] && \
  [ "$BEFORE" = "$(sha256sum "$D/Content/Maps/TestMap.umap" | cut -d' ' -f1)" ]; then
  echo 'M83_MAP_INTEGRITY=PASS'
else
  echo 'M83_MAP_INTEGRITY=FAIL'
fi
echo '=== COOKED MAPS ==='
find "$D/Saved" -type f -iname '*TestMap*' -print 2>/dev/null | head -n 6 || true
echo '=== STAGED GAME ARCHIVES ==='
find "$D/Saved" -type f \( -name '*.pak' -o -name '*.ucas' -o -name '*.utoc' \) -printf '%p | %s bytes\n' 2>/dev/null | head -n 12 || true
echo '=== ENGINE SUMMARY ==='
grep -Ei 'AutomationTool exiting|BUILD FAILED|LogCook: Error|LogLinker: Error|Fatal error|Exception:' "$L" | tail -n 15 || true
echo "M83_LOG=$L"
