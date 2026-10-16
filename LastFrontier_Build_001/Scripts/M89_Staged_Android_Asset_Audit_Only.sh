#!/usr/bin/env bash
# M89 read-only stage gate: do not build/cook/package/sign/upload.
set -u
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
W="$HOME/crownfall/M84_EDITOR_SANDBOX_v218"
S="$W/Saved/StagedBuilds/Android_ASTC/LastFrontier/Content/Paks"
L="$HOME/crownfall/M88_STAGE_ANDROID_ASTC.log"
echo '=== M89 STAGE VALIDATION ==='
PASS=YES
for N in 'global.ucas' 'global.utoc' 'LastFrontier-Android_ASTC.pak' 'LastFrontier-Android_ASTC.ucas' 'LastFrontier-Android_ASTC.utoc'; do
  if [ -s "$S/$N" ]; then
    echo "M89_FOUND=$N ($(stat -c %s "$S/$N") bytes)"
  else
    echo "M89_MISSING=$N"
    PASS=NO
  fi
done
if [ -s "$L" ] && grep -Fq 'AutomationTool exiting with ExitCode=0 (Success)' "$L"; then echo 'M89_UAT_LOG=PASS'; else echo 'M89_UAT_LOG=NOT_VERIFIED'; PASS=NO; fi
if [ -s "$W/Saved/Cooked/Android_ASTC/LastFrontier/Content/Maps/TestMap.umap" ]; then echo 'M89_COOKED_MAP=PASS'; else echo 'M89_COOKED_MAP=MISSING'; PASS=NO; fi
if cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" && cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap"; then echo 'M89_MAP_INTEGRITY=PASS'; else echo 'M89_MAP_INTEGRITY=FAIL'; PASS=NO; fi
for X in 'StoreVersion=218' 'PackageName=com.crownfall.stronghold' 'TargetSDKVersion=36' 'bEnableBundle=True'; do grep -Fqx "$X" "$W/Config/DefaultEngine.ini" || { echo "M89_CONFIG_MISMATCH=$X"; PASS=NO; }; done
if [ -d "$S" ]; then
  echo "M89_ARCHIVE_COUNT=$(find "$S" -maxdepth 1 -type f \( -name '*.pak' -o -name '*.ucas' -o -name '*.utoc' \) | wc -l)"
  du -sh "$W/Saved/StagedBuilds/Android_ASTC" | sed 's/^/M89_STAGE_SIZE=/'
fi
if [ -d "$W/Saved/StagedBuilds" ]; then
  N=$(find "$W/Saved/StagedBuilds" -type f \( -iname '*.jks' -o -iname '*.keystore' -o -iname '*.pem' -o -iname '*.p12' \) | wc -l)
  echo "M89_PRIVATE_SIGNING_FILES=$N"
  [ "$N" -eq 0 ] || PASS=NO
fi
echo "M89_STAGE_GATE=$PASS"
echo "M89_NO_PACKAGE_OR_SIGN=TRUE"
