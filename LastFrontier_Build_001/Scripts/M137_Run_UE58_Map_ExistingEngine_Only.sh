#!/usr/bin/env bash
# M137: Isolated Unreal Editor map regeneration using an ALREADY INSTALLED UE5.8.
# Never downloads the engine or performs build/cook/sign/upload. No sudo.
set -euo pipefail

fail() { printf 'M137_STATUS=BLOCKED_%s\n' "$1" >&2; exit 2; }

if [[ $# -ne 3 ]]; then
  printf 'USAGE: bash %s <GitHub_repo_root> <EXISTING_UE58_root> <NEW_abs_sandbox_path>\n' "$0" >&2
  exit 2
fi
command -v python3 >/dev/null || fail PYTHON3_MISSING
command -v timeout >/dev/null || fail TIMEOUT_MISSING
command -v tee >/dev/null || fail TEE_MISSING

REPO="$(realpath -e -- "$1")" || fail REPO_MISSING
UE_ROOT="$(realpath -e -- "$2")" || fail ENGINE_ROOT_MISSING
SANDBOX="$(realpath -m -- "$3")"
[[ ! -e "$SANDBOX" ]] || fail SANDBOX_ALREADY_EXISTS
[[ "$SANDBOX" != "$REPO" && "$SANDBOX"/ != "$REPO"/* && "$REPO"/ != "$SANDBOX"/* ]] ||
  fail SANDBOX_NOT_ISOLATED
[[ "$SANDBOX" != "$UE_ROOT" && "$SANDBOX"/ != "$UE_ROOT"/* && "$UE_ROOT"/ != "$SANDBOX"/* ]] ||
  fail SANDBOX_COLLIDES_ENGINE_DIRECTORY
[[ -f "$REPO/LastFrontier_Build_001/LastFrontier.uproject" ]] || fail PROJECT_NOT_FOUND

EDITOR="$UE_ROOT/Engine/Binaries/Linux/UnrealEditor"
if [[ ! -x "$EDITOR" ]]; then
  EDITOR="$UE_ROOT/Engine/Binaries/Linux/UnrealEditor-Cmd"
fi
[[ -x "$EDITOR" ]] || fail NO_EXISTING_UNREAL_EDITOR
[[ -x "$UE_ROOT/Engine/Build/BatchFiles/Build.sh" ]] || fail UE_BUILD_TOOLS_MISSING
VERSION="$UE_ROOT/Engine/Build/Build.version"
[[ -f "$VERSION" ]] || fail UNREAL_VERSION_METADATA_MISSING
python3 - "$VERSION" <<'PY' || fail ENGINE_NOT_UE58
from pathlib import Path
import json, sys
v = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert v.get("MajorVersion") == 5 and v.get("MinorVersion") == 8, "Only Unreal 5.8 is permitted"
print("M137_ENGINE_VERSION=5.8_EXISTING")
PY

if [[ -z "${DISPLAY:-}" ]] && ! command -v xvfb-run >/dev/null; then
  fail NO_DISPLAY_OR_XVFB
fi

# The sandbox copies only explicitly whitelisted code/INI and the known
# failed TestMap (quarantined immediately). Absolutely no signing files.
python3 "$REPO/LastFrontier_Build_001/Scripts/M136_Isolated_Map_Sandbox.py" \
  prepare --repo "$REPO" --sandbox "$SANDBOX"
PROJECT="$SANDBOX/LastFrontier_Build_001/LastFrontier.uproject"
GENERATE="$SANDBOX/LastFrontier_Build_001/Scripts/M136_Create_TestMap_In_Unreal.py"
LOG="$SANDBOX/M137_UnrealEditor_GenerateAndReload.log"
[[ -f "$GENERATE" ]] || fail NO_EDITOR_PYTHON_SCRIPT

# Confirm Editor actually creates and reloads the map. A successful Python
# syntax test alone cannot satisfy these requirements.
cmd=(
  "$EDITOR" "$PROJECT" "-ExecutePythonScript=$GENERATE"
  -unattended -nop4 -nosplash -nullrhi -log
)
if [[ -z "${DISPLAY:-}" ]]; then
  cmd=(xvfb-run -a "${cmd[@]}")
fi
echo 'M137_EXISTING_UE_EDITOR_INVOCATION=STARTING'
set +e
timeout --signal=TERM --kill-after=20s 900 "${cmd[@]}" 2>&1 | tee "$LOG"
rc=${PIPESTATUS[0]}
set -e
if (( rc != 0 )); then
  printf 'M137_EXISTING_UE_EDITOR_EXIT_CODE=%s\n' "$rc" >&2
  fail EDITOR_MAP_CREATE_OR_RELOAD_FAILED
fi
grep -Fq 'CROWNFALL_M136_UE_LEVEL_GENERATED=PASS' "$LOG" ||
  fail GENERATOR_MARKER_NOT_FOUND
grep -Fq 'CROWNFALL_M137_UE_TESTMAP_EDITOR_RELOAD=PASS' "$LOG" ||
  fail RELOAD_MARKER_NOT_FOUND
if grep -Eq 'CROWNFALL_M136_FAILURE=|Fatal error:|Assertion failed:' "$LOG"; then
  fail EDITOR_FATAL_IN_LOG
fi

python3 "$REPO/LastFrontier_Build_001/Scripts/M136_Isolated_Map_Sandbox.py" \
  finalize --sandbox "$SANDBOX" --editor-log "$LOG"

# Explicitly refuse to interpret this as an Android AAB or a successful Cook.
printf '%s\n' \
  'M137_EDITOR_GENERATE_AND_RELOAD=REPORTED_SUCCESS' \
  'M137_UNREAL_COOK_AND_ANDROID_BUILD=NOT_RUN' \
  'M137_ANDROID_RUNTIME_V218=NOT_TESTED' \
  'M137_ORIGINAL_GITHUB_MAP_MODIFIED=NO' \
  'M137_M84_M106_AND_GOOGLE_PLAY_MODIFIED=NO'
