#!/usr/bin/env bash
# M88: Reuse M86 cook and M78 Android binaries. Stage only on M84. No build/cook/package/distribution/upload flags.
set -u
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
W="$HOME/crownfall/M84_EDITOR_SANDBOX_v218"
E="$HOME/UE_5.8.3"
L="$HOME/crownfall/M88_STAGE_ANDROID_ASTC.log"
C="$W/Saved/Cooked/Android_ASTC/LastFrontier/Content"
S="$W/Saved/StagedBuilds"
stop(){ echo "M88_PREFLIGHT=BLOCKED:$1"; exit 2; }
[ ! -e "$L" ] || stop EXISTING_LOG
[ ! -d "$S" ] || stop EXISTING_STAGE_DIR
for F in "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap" "$W/LastFrontier.uproject" "$C/Maps/TestMap.umap" "$W/Binaries/Android/LastFrontier-Android-Shipping-arm64.so"; do [ -s "$F" ] || stop REQUIRED_FILE_MISSING; done
[ -x "$E/Engine/Build/BatchFiles/RunUAT.sh" ] || stop UAT_MISSING
grep -Fqx 'StoreVersion=218' "$W/Config/DefaultEngine.ini" || stop WRONG_VERSION
grep -Fqx 'PackageName=com.crownfall.stronghold' "$W/Config/DefaultEngine.ini" || stop WRONG_PACKAGE
cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap" || stop M84_MAP_MISMATCH
cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" || stop M77_MAP_MISMATCH
[ -z "$(find "$W/Content" -type l -print -quit)" ] || stop SYMLINKED_CONTENT
K=$(df -Pk "$W" | awk 'END{print $4}')
[[ "$K" =~ ^[0-9]+$ ]] || stop DISK_UNKNOWN
(( K >= 40*1024*1024 )) || stop NEED_40GIB_FREE
OLD=$(sha256sum "$P/Content/Maps/TestMap.umap" | cut -d' ' -f1)
echo "M88_PREFLIGHT=PASS"
echo "M88_ACTION=SKIPCOOK_STAGE_PAK"
timeout --kill-after=20s 2700 "$E/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun \
  -project="$W/LastFrontier.uproject" -noP4 \
  -platform=Android -cookflavor=ASTC -clientconfig=Shipping \
  -skipcook -stage -pak -unattended -utf8output >"$L" 2>&1
RC=$?
echo "M88_UAT_EXIT=$RC"
if [ "$OLD" = "$(sha256sum "$P/Content/Maps/TestMap.umap" | cut -d' ' -f1)" ] && [ "$OLD" = "$(sha256sum "$D/Content/Maps/TestMap.umap" | cut -d' ' -f1)" ] && [ "$OLD" = "$(sha256sum "$W/Content/Maps/TestMap.umap" | cut -d' ' -f1)" ]; then
  echo "M88_MAP_INTEGRITY=PASS"
else
  echo "M88_MAP_INTEGRITY=FAIL"
fi
echo "=== STAGED GAME CONTENT ARCHIVES ==="
if [ -d "$S" ]; then
  find "$S" -type f \( -name '*.pak' -o -name '*.ucas' -o -name '*.utoc' \) -printf '%p | %s bytes\n' | head -n 12
  COUNT=$(find "$S" -type f \( -name '*.pak' -o -name '*.ucas' -o -name '*.utoc' \) | wc -l)
else
  COUNT=0
fi
echo "M88_STAGE_ARCHIVES=$COUNT"
if [ "$RC" -eq 0 ] && [ "$COUNT" -gt 0 ]; then echo "M88_STAGE_CONTENT=PASS"; else echo "M88_STAGE_CONTENT=NOT_VERIFIED"; fi
echo "=== UAT SUMMARY ==="
grep -Ei 'AutomationTool exiting|BUILD FAILED|Fatal error|Error:|Exception:' "$L" | tail -n 18 || true
echo "M88_LOG=$L"
echo "M88_PLAY_UPLOAD=NOT_PERFORMED"
