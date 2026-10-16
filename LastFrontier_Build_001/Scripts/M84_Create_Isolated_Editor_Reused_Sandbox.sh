#!/usr/bin/env bash
# M84: protected copy, no cook/build/package/sign/upload; no modification of M63/M70/M77.
set -Eeuo pipefail
umask 077
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
O="$HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
W="$HOME/crownfall/M84_EDITOR_SANDBOX_v218"
E="$HOME/UE_5.8.3"
fail(){ echo "M84_BLOCKED=$1"; exit 2; }
test ! -e "$W" || fail SANDBOX_ALREADY_EXISTS
command -v rsync >/dev/null || fail RSYNC_MISSING
for X in "$P/Content/Maps/TestMap.umap" "$O/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" "$D/LastFrontier.uproject"; do test -s "$X" || fail REQUIRED_FILE_MISSING; done
for X in "$O/Binaries/Linux/UnrealEditor.modules" "$E/Engine/Binaries/Linux/UnrealEditor.modules" "$O/Binaries/Linux/libUnrealEditor-LastFrontier.so" "$O/Binaries/Linux/libUnrealEditor-LastFrontierEditor.so" "$O/Binaries/Linux/LastFrontierEditor.target"; do test -s "$X" || fail EDITOR_MODULE_FILE_MISSING; done
cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" || fail ORIGINAL_MAP_DIFFERS
cmp -s "$O/LastFrontier.uproject" "$D/LastFrontier.uproject" || fail UPROJECT_DIFFERS
diff -qr "$O/Source" "$D/Source" >/dev/null || fail SOURCE_DIFFERS
diff -qr "$O/Content" "$D/Content" >/dev/null || fail CONTENT_DIFFERS
grep -Fqx "StoreVersion=218" "$D/Config/DefaultEngine.ini" || fail VERSION_CODE_NOT_218
if [ -n "$(find "$D/Content" -type l -print -quit)" ]; then fail CONTENT_SYMLINKS; fi
python3 - "$E/Engine/Binaries/Linux/UnrealEditor.modules" "$O/Binaries/Linux/UnrealEditor.modules" <<'PY'
import json,sys
a=json.load(open(sys.argv[1],encoding="utf-8"))
b=json.load(open(sys.argv[2],encoding="utf-8"))
assert a.get("BuildId") and a["BuildId"]==b.get("BuildId"),"BUILD_ID_MISMATCH"
assert b["Modules"].get("LastFrontier")=="libUnrealEditor-LastFrontier.so","GAME_MODULE_MISSING"
assert b["Modules"].get("LastFrontierEditor")=="libUnrealEditor-LastFrontierEditor.so","EDITOR_MODULE_MISSING"
print("M84_BUILD_ID=PASS")
PY
K=$(df -Pk "$D" | awk 'END{print $4}')
[[ "$K" =~ ^[0-9]+$ ]] || fail DISK_CHECK_ERROR
(( K >= 30*1024*1024 )) || fail FREE_DISK_BELOW_30GIB
echo "M84_PREFLIGHT=PASS"
mkdir -m 700 "$W"
rsync -a --exclude="Saved/" --exclude="Intermediate/" --exclude="DerivedDataCache/" --exclude=".git/" --exclude="*.aab" --exclude="*.apk" --exclude="*.jks" --exclude="*.keystore" --exclude="*.p12" --exclude="*.pem" "$D/" "$W/"
mkdir -p "$W/Binaries/Linux"
for F in UnrealEditor.modules libUnrealEditor-LastFrontier.so libUnrealEditor-LastFrontierEditor.so LastFrontierEditor.target; do cp -p "$O/Binaries/Linux/$F" "$W/Binaries/Linux/$F"; done
cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap" || fail SANDBOX_MAP_DIFFERS
cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap" || fail ORIGINAL_CHANGED
echo "M84_SANDBOX=$W"
echo "M84_EDITOR_MODULES_PREPARED=PASS"
echo "M84_MAP_INTEGRITY=PASS"
echo "M84_EDITOR_LOAD=NOT_YET_TESTED"
echo "M84_COOK=NOT_STARTED"
echo "M84_AAB=NOT_BUILT"
