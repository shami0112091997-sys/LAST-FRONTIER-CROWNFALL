#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$PROJECT_DIR/LastFrontier.uproject"
UE_ROOT="${UE_ROOT:-}"
PLATFORM="${PLATFORM:-Linux}"
CONFIG="${CONFIG:-Development}"
LOG_DIR="$PROJECT_DIR/Saved/RecoveryLogs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/M44_Compile_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
fail(){ echo "M44_COMPILE_STATUS=BLOCKED_OR_FAILED"; echo "REASON=$1"; exit "$2"; }
[[ -n "$UE_ROOT" ]] || fail "UE_ROOT is not set" 2
UBT="$UE_ROOT/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool"
[[ -x "$UBT" ]] || fail "UnrealBuildTool not found/executable: $UBT" 3
[[ -f "$PROJECT" ]] || fail "uproject not found: $PROJECT" 4
echo "[M44 Recovery] Compile Editor target"
"$UBT" LastFrontierEditor "$PLATFORM" "$CONFIG" -Project="$PROJECT" -Progress -NoHotReloadFromIDE
echo "[M44 Recovery] Compile Game target"
"$UBT" LastFrontier "$PLATFORM" "$CONFIG" -Project="$PROJECT" -Progress -NoHotReloadFromIDE
echo "M44_COMPILE_STATUS=PASS"
echo "LOG=$LOG"
