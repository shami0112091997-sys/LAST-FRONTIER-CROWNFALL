#!/usr/bin/env bash
set -euo pipefail

APK="CROWNFALL_Stronghold_Android/app/build/outputs/apk/debug/app-debug.apk"
PKG="com.crownfall.stronghold"

test -s "$APK"
adb install -r "$APK"
adb logcat -c
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/.MainActivity" | tee /tmp/crownfall_start.txt
sleep 7

PID="$(adb shell pidof "$PKG" 2>/dev/null || true)"
printf '%s\n' "$PID" | tee /tmp/crownfall_pid.txt
adb exec-out screencap -p > /tmp/crownfall_gameplay.png || true
adb logcat -d > /tmp/crownfall_gameplay_logcat.txt || true

if grep -E "FATAL EXCEPTION|AndroidRuntime.*FATAL|ANR in com\.crownfall\.stronghold" /tmp/crownfall_gameplay_logcat.txt; then
  echo "CROWNFALL_RUNTIME_FAILURE"
  exit 1
fi

test -n "$PID"
grep -q 'CROWNFALL_SMOKE.*DOM="START_OK"' /tmp/crownfall_gameplay_logcat.txt
grep -q 'CROWNFALL_GAMEPLAY_SMOKE.*RESULT="PASS:' /tmp/crownfall_gameplay_logcat.txt

grep -E 'CROWNFALL_SMOKE|CROWNFALL_GAMEPLAY_SMOKE' /tmp/crownfall_gameplay_logcat.txt | tail -20
echo "CROWNFALL_FIRST_SESSION_SMOKE_PASS"
