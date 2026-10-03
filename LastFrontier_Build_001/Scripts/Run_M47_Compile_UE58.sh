#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$PROJECT_DIR/LastFrontier.uproject"
PLATFORM="${PLATFORM:-Linux}"
CONFIG="${CONFIG:-Development}"
LOG_DIR="$PROJECT_DIR/Saved/M47Logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/M47_Compile_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

fail(){ echo "M47_COMPILE_STATUS=BLOCKED_OR_FAILED"; echo "REASON=$1"; echo "LOG=$LOG"; exit "$2"; }

resolve_ue_root(){
  if [[ -n "${UE_ROOT:-}" && -d "${UE_ROOT}" ]]; then printf '%s\n' "$UE_ROOT"; return 0; fi
  local candidates=(
    "$HOME/UnrealEngine"
    "$HOME/UE_5.8"
    "/opt/UnrealEngine"
    "/opt/UE_5.8"
    "/usr/local/UnrealEngine"
    "/usr/local/UE_5.8"
  )
  local c
  for c in "${candidates[@]}"; do
    [[ -d "$c/Engine" ]] && { printf '%s\n' "$c"; return 0; }
  done
  return 1
}

[[ -f "$PROJECT" ]] || fail "uproject not found: $PROJECT" 3
UE_ROOT_RESOLVED="$(resolve_ue_root || true)"
[[ -n "$UE_ROOT_RESOLVED" ]] || fail "UE 5.8 root not found. Set UE_ROOT to the Unreal Engine 5.8 installation." 2
export UE_ROOT="$UE_ROOT_RESOLVED"
echo "UE_ROOT=$UE_ROOT"
echo "PROJECT=$PROJECT"
echo "PLATFORM=$PLATFORM"
echo "CONFIG=$CONFIG"

BUILD_SH="$UE_ROOT/Engine/Build/BatchFiles/Linux/Build.sh"
[[ -x "$BUILD_SH" ]] || BUILD_SH="$UE_ROOT/Engine/Build/BatchFiles/Build.sh"

run_ubt_direct(){
  local target="$1"
  local ubt_native="$UE_ROOT/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool"
  local ubt_dll="$UE_ROOT/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll"
  if [[ -x "$ubt_native" ]]; then
    "$ubt_native" "$target" "$PLATFORM" "$CONFIG" -Project="$PROJECT" -Progress -NoHotReloadFromIDE
  elif [[ -f "$ubt_dll" ]] && command -v dotnet >/dev/null 2>&1; then
    dotnet "$ubt_dll" "$target" "$PLATFORM" "$CONFIG" -Project="$PROJECT" -Progress -NoHotReloadFromIDE
  else
    fail "Neither Build.sh nor runnable UnrealBuildTool was found under $UE_ROOT" 4
  fi
}

compile_target(){
  local target="$1"
  echo "[M47] Compiling $target ($PLATFORM $CONFIG)"
  if [[ -x "$BUILD_SH" ]]; then
    "$BUILD_SH" "$target" "$PLATFORM" "$CONFIG" "$PROJECT" -Progress -NoHotReloadFromIDE
  else
    run_ubt_direct "$target"
  fi
}

# IMPORTANT: Compile is intentionally independent of game map assets.
compile_target LastFrontierEditor
compile_target LastFrontier

if [[ ! -d "$PROJECT_DIR/Binaries" ]]; then
  fail "UBT returned success but project Binaries/ was not produced" 10
fi
ARTIFACT_COUNT="$(find "$PROJECT_DIR/Binaries" -type f 2>/dev/null | wc -l | tr -d ' ')"
[[ "$ARTIFACT_COUNT" -gt 0 ]] || fail "UBT returned success but no project binary artifacts were found" 11

echo "M47_BINARY_ARTIFACT_COUNT=$ARTIFACT_COUNT"
find "$PROJECT_DIR/Binaries" -type f -maxdepth 4 -print | sort | sed -n '1,200p'
echo "M47_COMPILE_STATUS=PASS"
echo "LOG=$LOG"
