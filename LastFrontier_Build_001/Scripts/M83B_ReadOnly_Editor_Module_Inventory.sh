#!/usr/bin/env bash
# M83B: READ-ONLY inventory of project editor modules; no Unreal runs or changes.
set -u
ROOT="$HOME/crownfall"
P="$ROOT/M63_REAL_MOBILE/LastFrontier_Build_001"
O="$ROOT/M70_ANDROID_STAGE_20261016T053500Z"
D="$ROOT/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
E="$HOME/UE_5.8.3"
echo '=== M83B EDITOR MODULE INVENTORY ==='
for LABEL in M70 M63 M77; do
  case "$LABEL" in
    M70) X="$O";;
    M63) X="$P";;
    M77) X="$D";;
  esac
  if [ -d "$X/Binaries/Linux" ]; then
    echo "=== $LABEL BINARIES/LINUX ==="
    find "$X/Binaries/Linux" -maxdepth 2 -type f \( -iname '*LastFrontier*' -o -name '*.modules' \) -printf '%f | %s bytes\n' | head -n 16
  else
    echo "$LABEL-EDITOR-BINARIES=ABSENT"
  fi
done
if [ -s "$D/Source/LastFrontierEditor.Target.cs" ]; then echo 'M83B_M77_EDITOR_TARGET=PASS'; else echo 'M83B_M77_EDITOR_TARGET=MISSING'; fi
if [ -x "$E/Engine/Build/BatchFiles/Linux/Build.sh" ]; then echo 'M83B_EDITOR_BUILD_TOOL=PASS'; else echo 'M83B_EDITOR_BUILD_TOOL=MISSING'; fi
if [ -s "$D/Config/DefaultEngine.ini" ]; then grep -E '^(GameDefaultMap|StoreVersion|TargetSDKVersion)=' "$D/Config/DefaultEngine.ini"; fi
if [ -s "$P/Content/Maps/TestMap.umap" ] && cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap"; then echo 'M83B_MAP_INTEGRITY=PASS'; else echo 'M83B_MAP_INTEGRITY=FAIL'; fi
echo 'M83B_INVENTORY_COMPLETE=YES'
