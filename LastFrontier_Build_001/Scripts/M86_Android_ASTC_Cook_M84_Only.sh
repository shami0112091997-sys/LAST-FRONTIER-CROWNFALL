#!/usr/bin/env bash
# M86: Cook assets on isolated M84 ONLY. No UAT packaging/signing/upload.
set -u
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
W="$HOME/crownfall/M84_EDITOR_SANDBOX_v218"
E="$HOME/UE_5.8.3"
PREV="$HOME/crownfall/M85_EDITOR_LOAD.log"
L="$HOME/crownfall/M86_ANDROID_ASTC_COOK.log"
fail(){ echo "M86_PREFLIGHT=BLOCKED:$1"; exit 2; }
test ! -e "$L" || fail LOG_ALREADY_EXISTS
for F in "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap" "$W/LastFrontier.uproject" "$W/Binaries/Linux/UnrealEditor.modules" "$PREV"; do test -s "$F" || fail REQUIRED_FILE_MISSING; done
test -x "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" || fail EDITOR_CMD_MISSING
grep -Fq 'M85_WORLD_LOAD=PASS' "$PREV" || fail PRIOR_EDITOR_SMOKE_NOT_VERIFIED
cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap" || fail ORIGINAL_MAP_DIFFERS
cmp -s "$D/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap" || fail STAGE_MAP_DIFFERS
grep -Fqx 'StoreVersion=218' "$W/Config/DefaultEngine.ini" || fail WRONG_VERSION
[ ! -d "$W/Saved/Cooked/Android_ASTC" ] || fail EXISTING_COOK_OUTPUT
[ ! -d "$W/Saved/Sandboxes/Cooked-Android_ASTC" ] || fail EXISTING_SANDBOX_COOK
[ -z "$(find "$W/Content" -type l -print -quit)" ] || fail CONTENT_SYMLINKED
K=$(df -Pk "$W" 2>/dev/null | awk 'END{print $4}')
[[ "$K" =~ ^[0-9]+$ ]] || fail DISK_CHECK_INVALID
(( K >= 40*1024*1024 )) || fail FREE_DISK_LT_40GIB
OLDHASH=$(sha256sum "$P/Content/Maps/TestMap.umap" | cut -d' ' -f1)
echo 'M86_PREFLIGHT=PASS'
echo 'M86_ACTION=COOK_ONLY_ANDROID_ASTC'
timeout --kill-after=20s 2400 "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" "$W/LastFrontier.uproject" -run=Cook -TargetPlatform=Android_ASTC -Map=/Game/Maps/TestMap -unattended -nosound -nullrhi -stdout -FullStdOutLogOutput -UTF8Output > "$L" 2>&1
RC=$?
echo "M86_COOK_EXIT=$RC"
C="$W/Saved/Cooked/Android_ASTC/LastFrontier/Content"
if [ "$RC" -eq 0 ] && [ -s "$C/Maps/TestMap.umap" ]; then echo 'M86_COOKED_MAP=PASS'; else echo 'M86_COOKED_MAP=NOT_VERIFIED'; fi
if [ -d "$C" ]; then echo "M86_GAME_ASSET_FILES=$(find "$C" -type f \( -name '*.uasset' -o -name '*.umap' -o -name '*.uexp' \) | wc -l)"; else echo 'M86_GAME_ASSET_FILES=UNKNOWN'; fi
if [ "$OLDHASH" = "$(sha256sum "$P/Content/Maps/TestMap.umap" | cut -d' ' -f1)" ] && [ "$OLDHASH" = "$(sha256sum "$D/Content/Maps/TestMap.umap" | cut -d' ' -f1)" ] && [ "$OLDHASH" = "$(sha256sum "$W/Content/Maps/TestMap.umap" | cut -d' ' -f1)" ]; then echo 'M86_MAP_INTEGRITY=PASS'; else echo 'M86_MAP_INTEGRITY=FAIL'; fi
grep -Ei 'Packages Cooked|Packages Skipped|LogCook: Display: Done!|Success -|Error:|Fatal error|Cook failed' "$L" | tail -n 16 || true
echo "M86_LOG=$L"
