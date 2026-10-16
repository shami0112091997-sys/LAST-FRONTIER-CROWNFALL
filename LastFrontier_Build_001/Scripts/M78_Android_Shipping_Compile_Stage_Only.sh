#!/usr/bin/env bash
# M78: Android Shipping native compile in isolated M77 stage; NO package/sign/upload.
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
E="$HOME/UE_5.8.3"
L="$HOME/crownfall/M78_ANDROID_SHIPPING_COMPILE.log"
K=$(df -Pk "$D" 2>/dev/null | awk 'END{print $4}')
if [ -e "$L" ]; then
  echo "M78_EXISTING_LOG=STOP"
elif [ -s "$D/LastFrontier.uproject" ] && [ -s "$D/Source/LastFrontier.Target.cs" ] && [ -x "$E/Engine/Build/BatchFiles/Linux/Build.sh" ] && grep -Fqx 'StoreVersion=218' "$D/Config/DefaultEngine.ini" && cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" && [[ "$K" =~ ^[0-9]+$ ]] && [ "$K" -gt 52428800 ]; then
  echo "M78_PREFLIGHT=PASS"
  timeout 2400 "$E/Engine/Build/BatchFiles/Linux/Build.sh" LastFrontier Android Shipping "$D/LastFrontier.uproject" -NoHotReloadFromIDE -Progress > "$L" 2>&1
  R=$?
  echo "M78_COMPILE_EXIT=$R"
  grep -Ei 'Result:|error:|fatal error:|BUILD SUCCEEDED|BUILD FAILED|ERROR:' "$L" | tail -n 25 || true
  if cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap"; then echo 'M78_MAP_INTEGRITY=PASS'; else echo 'M78_MAP_INTEGRITY=FAIL'; fi
else
  echo "M78_PREFLIGHT=BLOCKED"
fi
echo "LOG=$L"
