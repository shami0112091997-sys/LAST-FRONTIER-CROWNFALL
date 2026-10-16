#!/usr/bin/env bash
# CROWNFALL M77: defaults to read-only, explicit approval needed to create a new release stage.
# No access to keys, passwords, tokens, Play Console or GCP APIs.
set -Eeuo pipefail
umask 077
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
S="$HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z"
OUT="$HOME/crownfall/M77_RELEASE_STAGES"
CFG="$S/Config/DefaultEngine.ini"
stop(){ echo "M77_BLOCKED=$1"; exit 2; }
test -s "$P/Content/Maps/TestMap.umap" || stop ORIGINAL_MAP_MISSING
test -s "$S/Content/Maps/TestMap.umap" || stop STAGE_MAP_MISSING
test -s "$S/LastFrontier.uproject" || stop STAGE_PROJECT_MISSING
test -s "$CFG" || stop CONFIG_MISSING
cmp -s "$P/Content/Maps/TestMap.umap" "$S/Content/Maps/TestMap.umap" || stop MAPS_DIVERGED
for V in "PackageName=com.crownfall.stronghold" "TargetSDKVersion=36" "bBuildForArm64=True" "bEnableBundle=True"; do grep -Fqx "$V" "$CFG" || stop "CONFIG_MISSING:$V"; done
CURRENT="$(sed -n 's/^StoreVersion=\([0-9][0-9]*\)\r*$/\1/p' "$CFG" | tail -1)"
[[ "$CURRENT" =~ ^[0-9]+$ ]] || stop BAD_CURRENT_VERSION
echo "M77_SOURCE_VALID=PASS"
echo "M77_STAGE_CURRENT_VERSION=$CURRENT"
if [[ "${M77_MODE:-AUDIT}" == "AUDIT" ]]; then
  echo "M77_MODE=READ_ONLY"
  echo "M77_PLAY_MAX=NOT_CONFIRMED"
  echo "M77_UPLOAD_CERTIFICATE=NOT_MATCHED_TO_CONSOLE"
  echo "M77_AAB=NOT_BUILT"
  exit 0
fi
[[ "${M77_MODE:-}" == "STAGE" && "${M77_APPROVED:-}" == "YES" ]] || stop APPROVAL_REQUIRED
MAX="${PLAY_MAX_CONFIRMED:-}"
NEXT="${NEXT_VERSION_CODE:-}"
[[ "$MAX" =~ ^[1-9][0-9]*$ && "$NEXT" =~ ^[1-9][0-9]*$ ]] || stop PLAY_VERSION_NOT_CONFIRMED
(( NEXT > MAX && NEXT > CURRENT && NEXT < 2100000000 )) || stop VERSION_OUT_OF_RANGE
command -v rsync >/dev/null 2>&1 || stop RSYNC_NOT_FOUND
K="$(df -Pk "$HOME" | awk 'END{print $4}')"
[[ "$K" =~ ^[0-9]+$ ]] || stop DISK_CHECK_INVALID
(( K > 50*1024*1024 )) || stop FREE_DISK_LT_50_GB
B="$(sha256sum "$P/Content/Maps/TestMap.umap" | cut -d' ' -f1)"
DEST="$OUT/M77_v${NEXT}_$(date -u +%Y%m%dT%H%M%SZ)"
[[ ! -e "$DEST" ]] || stop STAGE_ALREADY_EXISTS
mkdir -p "$DEST"
chmod 700 "$DEST"
rsync -a --exclude="Saved/" --exclude="Intermediate/" --exclude="Binaries/" --exclude="DerivedDataCache/" --exclude=".git/" "$S/" "$DEST/" || stop COPY_FAILED
[[ "$(sha256sum "$DEST/Content/Maps/TestMap.umap" | cut -d' ' -f1)" == "$B" ]] || stop MAP_COPY_HASH_MISMATCH
python3 - "$DEST/Config/DefaultEngine.ini" "$NEXT" <<'PY'
import pathlib,re,sys
p=pathlib.Path(sys.argv[1]); data=p.read_text()
patterns=list(re.finditer(r"(?m)^StoreVersion=[0-9]+(?=\r?$)",data))
if len(patterns)!=1: raise SystemExit("M77_BLOCKED=AMBIGUOUS_STORE_VERSION")
m=patterns[0]
p.write_text(data[:m.start()] + "StoreVersion="+sys.argv[2]+data[m.end():])
PY
grep -Fqx "StoreVersion=$NEXT" "$DEST/Config/DefaultEngine.ini" || stop VERSION_NOT_UPDATED
[[ "$(sha256sum "$P/Content/Maps/TestMap.umap" | cut -d' ' -f1)" == "$B" ]] || stop ORIGINAL_HASH_CHANGED
[[ "$(sha256sum "$S/Content/Maps/TestMap.umap" | cut -d' ' -f1)" == "$B" ]] || stop STAGE_HASH_CHANGED
echo "M77_NEW_RELEASE_STAGE=$DEST"
echo "M77_NEXT_VERSION=$NEXT"
echo "M77_MAP_INTEGRITY=PASS"
echo "M77_KEY_IMPORTED=NO"
echo "M77_AAB_BUILT=NO"
echo "M77_PLAY_UPLOAD=NO"
