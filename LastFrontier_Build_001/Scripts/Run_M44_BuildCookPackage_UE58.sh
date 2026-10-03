#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$PROJECT_DIR/LastFrontier.uproject"
UE_ROOT="${UE_ROOT:-}"
PLATFORM="${PLATFORM:-Linux}"
CONFIG="${CONFIG:-Development}"
ARCHIVE_DIR="${ARCHIVE_DIR:-$PROJECT_DIR/Packaged}"
fail(){ echo "M44_PACKAGE_STATUS=BLOCKED_OR_FAILED"; echo "REASON=$1"; exit "$2"; }
[[ -n "$UE_ROOT" ]] || fail "UE_ROOT is not set" 2
RUNUAT="$UE_ROOT/Engine/Build/BatchFiles/RunUAT.sh"
[[ -x "$RUNUAT" ]] || fail "RunUAT not found/executable: $RUNUAT" 3
MAP="$PROJECT_DIR/Content/Maps/TestMap.umap"
[[ -s "$MAP" ]] || fail "genuine TestMap.umap missing; create/save it in UE 5.8 before Cook/Package" 5
mkdir -p "$ARCHIVE_DIR"
"$RUNUAT" BuildCookRun -project="$PROJECT" -noP4 -build -cook -stage -pak -archive -archivedirectory="$ARCHIVE_DIR" -platform="$PLATFORM" -clientconfig="$CONFIG" -utf8output
if ! find "$ARCHIVE_DIR" -type f \( -name 'LastFrontier*' -o -name '*.pak' -o -name '*.ucas' \) -print -quit | grep -q .; then fail "no expected packaged artifact found" 20; fi
echo "M44_PACKAGE_STATUS=PASS"
