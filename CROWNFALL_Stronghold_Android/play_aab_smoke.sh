#!/usr/bin/env bash
set -euo pipefail

PKG="com.crownfall.stronghold"
APK="/tmp/CROWNFALL-2.1.2-universal.apk"

adb install -r "$APK"
adb shell settings put secure immersive_mode_confirmations confirmed || true
adb logcat -c
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/.MainActivity" | tee /tmp/crownfall_start.txt
sleep 10

PID="$(adb shell pidof "$PKG" 2>/dev/null || true)"
printf '%s\n' "$PID" | tee /tmp/crownfall_pid.txt
adb exec-out screencap -p > /tmp/crownfall_play_screen.png || true
adb logcat -d > /tmp/crownfall_play_logcat.txt || true

if grep -E "FATAL EXCEPTION|AndroidRuntime.*FATAL|ANR in com\.crownfall\.stronghold" /tmp/crownfall_play_logcat.txt; then
  echo "CROWNFALL_PLAY_AAB_RUNTIME_FAILURE"
  exit 1
fi

if [ -z "$PID" ]; then
  echo "CROWNFALL_PLAY_AAB_PROCESS_NOT_RUNNING"
  grep -E "com\.crownfall\.stronghold|AndroidRuntime|chromium|WebView" /tmp/crownfall_play_logcat.txt | tail -120 || true
  exit 1
fi

echo "CROWNFALL_PLAY_AAB_SMOKE_PASS PID=$PID"
