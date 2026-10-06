#!/usr/bin/env bash
set -euo pipefail

APK="CROWNFALL_Stronghold_Android/app/build/outputs/apk/debug/app-debug.apk"
PKG="com.crownfall.stronghold"

test -s "$APK"
adb install -r "$APK"
adb logcat -c
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/.MainActivity" | tee /tmp/crownfall_start.txt
sleep 10

PID="$(adb shell pidof "$PKG" 2>/dev/null || true)"
printf '%s\n' "$PID" | tee /tmp/crownfall_pid.txt
adb shell dumpsys activity activities | grep -E "mResumedActivity|topResumedActivity|ResumedActivity" | tee /tmp/crownfall_activity.txt || true
adb exec-out screencap -p > /tmp/crownfall_screen.png || true
adb logcat -d > /tmp/crownfall_logcat.txt || true

if grep -E "FATAL EXCEPTION|AndroidRuntime.*FATAL|ANR in com\.crownfall\.stronghold" /tmp/crownfall_logcat.txt; then
  echo "CROWNFALL_RUNTIME_FAILURE"
  exit 1
fi

if [ -z "$PID" ]; then
  echo "CROWNFALL_PROCESS_NOT_RUNNING"
  grep -E "com\.crownfall\.stronghold|AndroidRuntime|chromium|WebView" /tmp/crownfall_logcat.txt | tail -120 || true
  exit 1
fi

if ! grep -q 'CROWNFALL_SMOKE.*DOM="START_OK"' /tmp/crownfall_logcat.txt; then
  echo "CROWNFALL_DOM_NOT_READY"
  grep -E "CROWNFALL_SMOKE|chromium|WebView" /tmp/crownfall_logcat.txt | tail -120 || true
  exit 1
fi

echo "CROWNFALL_EMULATOR_SMOKE_PASS PID=$PID DOM=START_OK"
