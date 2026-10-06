#!/usr/bin/env bash
set -euo pipefail

APK="CROWNFALL_Stronghold_Android/app/build/outputs/apk/debug/app-debug.apk"
PKG="com.crownfall.stronghold"

test -s "$APK"
adb install -r "$APK"

# Keep emulator launcher ANR dialogs from covering the game during cold boot.
adb shell settings put global show_first_crash_dialog 0 || true
adb shell settings put secure anr_show_background 0 || true
adb shell am force-stop com.android.launcher3 || true
adb shell input keyevent 4 || true

adb logcat -c
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/.MainActivity" | tee /tmp/crownfall_start.txt

PASS=0
for i in $(seq 1 35); do
  PID="$(adb shell pidof "$PKG" 2>/dev/null || true)"
  printf '%s\n' "$PID" > /tmp/crownfall_pid.txt
  adb logcat -d > /tmp/crownfall_gameplay_logcat.txt || true

  if grep -E "FATAL EXCEPTION|AndroidRuntime.*FATAL|ANR in com\.crownfall\.stronghold" /tmp/crownfall_gameplay_logcat.txt; then
    echo "CROWNFALL_RUNTIME_FAILURE"
    exit 1
  fi

  if grep -q 'CROWNFALL_GAMEPLAY_SMOKE.*RESULT="PASS:' /tmp/crownfall_gameplay_logcat.txt; then
    PASS=1
    break
  fi

  if grep -q 'CROWNFALL_GAMEPLAY_SMOKE.*RESULT="FAIL:' /tmp/crownfall_gameplay_logcat.txt; then
    grep -E 'CROWNFALL_SMOKE|CROWNFALL_GAMEPLAY_SMOKE' /tmp/crownfall_gameplay_logcat.txt | tail -30 || true
    echo "CROWNFALL_GAMEPLAY_SMOKE_REPORTED_FAILURE"
    exit 1
  fi

  sleep 1
done

adb exec-out screencap -p > /tmp/crownfall_gameplay.png || true
adb logcat -d > /tmp/crownfall_gameplay_logcat.txt || true

test -n "$(cat /tmp/crownfall_pid.txt)"
grep -q 'CROWNFALL_SMOKE.*DOM="START_OK"' /tmp/crownfall_gameplay_logcat.txt
test "$PASS" -eq 1

grep -E 'CROWNFALL_SMOKE|CROWNFALL_GAMEPLAY_SMOKE' /tmp/crownfall_gameplay_logcat.txt | tail -30
echo "CROWNFALL_FIRST_SESSION_SMOKE_PASS"
