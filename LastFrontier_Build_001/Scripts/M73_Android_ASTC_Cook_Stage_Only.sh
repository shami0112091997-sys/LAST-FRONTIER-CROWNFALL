#!/usr/bin/env bash
# M73: Android ASTC cook-only; run manually on existing VM after M72 PASS.
# No package/sign/upload. Writes cooked output to isolated M70 stage.
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z"
E="$HOME/UE_5.8.3"
L="$HOME/crownfall/M73_ANDROID_ASTC_COOK.log"
A="$P/Content/Maps/TestMap.umap"
B="$D/Content/Maps/TestMap.umap"
K=$(df -Pk "$D" 2>/dev/null | awk 'END{print $4}')
if [ -s "$A" ] && [ -s "$B" ] && [ -s "$D/LastFrontier.uproject" ] && [ -x "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" ] && cmp -s "$A" "$B" && [[ "$K" =~ ^[0-9]+$ ]] && [ "$K" -ge 62914560 ]; then
 H=$(sha256sum "$A" | cut -d' ' -f1)
 echo 'M73_ANDROID_COOK=STARTED'
 timeout 2700 "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" "$D/LastFrontier.uproject" -run=Cook -TargetPlatform=Android_ASTC -Map=/Game/Maps/TestMap -unattended -nosound -nullrhi -stdout -FullStdOutLogOutput -UTF8Output >"$L" 2>&1
 R=$?
 echo "M73_COOK_EXIT=$R"
 if [ "$H" = "$(sha256sum "$A" | cut -d' ' -f1)" ] && [ "$H" = "$(sha256sum "$B" | cut -d' ' -f1)" ]; then echo 'M73_MAP_INTEGRITY=PASS'; else echo 'M73_MAP_INTEGRITY=FAIL'; fi
 echo '=== COOK RESULT LINES ==='
 grep -Ei 'Cook (completed|finished|success)|Success - 0 error|LogCook: Error|LogLinker: Error|Serialization error|Fatal error|Assertion failed|Unknown Target Platform' "$L" | tail -n 20 || true
 echo '=== COOKED FILES ==='
 find "$D/Saved/Cooked" "$D/Saved/Sandboxes" -type f 2>/dev/null | head -n 8 || true
else
 echo 'M73_PREFLIGHT=BLOCKED'
fi
echo "LOG=$L"