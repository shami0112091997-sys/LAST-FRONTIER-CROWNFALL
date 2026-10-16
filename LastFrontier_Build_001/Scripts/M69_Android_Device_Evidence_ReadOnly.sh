#!/usr/bin/env bash
# Read-only Android device evidence collection for CROWNFALL.
# Run on a computer with adb and a connected Android test device, NOT on the GCP build VM.
set -Eeuo pipefail
umask 077
PKG='com.crownfall.stronghold'
OUT="${M69_OUT:-$HOME/crownfall/M69_DEVICE_EVIDENCE}"
DURATION="${M69_DURATION_SECONDS:-900}"
INTERVAL="${M69_SAMPLE_INTERVAL_SECONDS:-300}"
fail() { printf 'M69_BLOCKED=%s\n' "$1" >&2; exit 2; }
command -v adb >/dev/null || fail ADB_NOT_INSTALLED
[[ "$DURATION" =~ ^[0-9]+$ ]] || fail BAD_DURATION
[[ "$INTERVAL" =~ ^[0-9]+$ ]] || fail BAD_INTERVAL
(( DURATION >= 60 && DURATION <= 1800 && INTERVAL >= 30 && INTERVAL <= DURATION )) || fail BAD_TEST_RANGE
NUM="$(adb devices | awk 'NR>1 && $2=="device"{n++} END{print n+0}')"
[[ "$NUM" == 1 ]] || fail EXACTLY_ONE_AUTHORIZED_DEVICE_REQUIRED
PM_PATH="$(adb shell pm path "$PKG" 2>/dev/null | tr -d '\r' || true)"
[[ "$PM_PATH" == package:* ]] || fail PACKAGE_NOT_INSTALLED
PID="$(adb shell pidof "$PKG" | tr -d '\r' || true)"
[[ -n "$PID" ]] || fail APP_NOT_RUNNING_START_MANUALLY
mkdir -p "$OUT"
RUN="$OUT/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -m 700 "$RUN"
exec > >(tee "$RUN/summary.txt") 2>&1
printf 'M69_ANDROID_FIRST_READ_ONLY_EVIDENCE=START\nPACKAGE=%s\nDURATION_SECONDS=%s\nINTERVAL_SECONDS=%s\nDIRECTORY=%s\n' "$PKG" "$DURATION" "$INTERVAL" "$RUN"
printf 'SDK_VERSION=%s\n' "$(adb shell getprop ro.build.version.sdk | tr -d '\r')"
printf 'PAGE_SIZE=%s\n' "$(adb shell getconf PAGE_SIZE | tr -d '\r' || echo unknown)"
printf 'SAMPLES_ARE_SUPPORTING_DATA_NOT_VALIDATED_FPS=TRUE\n'
SECONDS_ELAPSED=0
N=0
while :; do
  N=$((N+1))
  F="$RUN/sample_$(printf '%02d' "$N")"
  mkdir -m 700 "$F"
  PID="$(adb shell pidof "$PKG" | tr -d '\r' || true)"
  if [[ -z "$PID" ]]; then
    echo 'M69_APP_PROCESS_EXITED=YES'; exit 3
  fi
  echo "SAMPLE=$N ELAPSED_SECONDS=$SECONDS_ELAPSED APP_RUNNING=YES"
  adb shell dumpsys meminfo "$PKG" > "$F/memory.txt" || echo 'MEMORY_CAPTURE_FAILED'
  adb shell dumpsys gfxinfo "$PKG" framestats > "$F/gfxinfo.txt" || echo 'GFXINFO_CAPTURE_FAILED'
  adb shell dumpsys thermalservice > "$F/thermal.txt" || echo 'THERMAL_CAPTURE_FAILED'
  if (( SECONDS_ELAPSED >= DURATION )); then break; fi
  WAIT=$INTERVAL
  if (( SECONDS_ELAPSED + WAIT > DURATION )); then WAIT=$((DURATION-SECONDS_ELAPSED)); fi
  sleep "$WAIT"
  SECONDS_ELAPSED=$((SECONDS_ELAPSED+WAIT))
done
printf 'M69_DEVICE_SNAPSHOTS_COMPLETED=YES\nFPS_P95_VERIFIED=NO\nUE_INSIGHTS_AND_GAMEPLAY_TEST_STILL_REQUIRED=YES\n'
printf 'PRIVACY=EVIDENCE_STORED_LOCALLY_ONLY_DO_NOT_COMMIT_RAW_LOGS\n'