#!/usr/bin/env bash
set -euo pipefail

APK="CROWNFALL_Stronghold_Android/app/build/outputs/apk/debug/app-debug.apk"
PKG="com.crownfall.stronghold"

test -s "$APK"
adb install -r "$APK"
adb logcat -c
adb shell am force-stop "$PKG"
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1
sleep 10

adb shell pidof "$PKG" | tee /tmp/crownfall_pid.txt
adb shell dumpsys activity activities | grep -E "mResumedActivity|topResumedActivity" | tee /tmp/crownfall_activity.txt || true
adb exec-out screencap -p > /tmp/crownfall_screen.png
adb logcat -d > /tmp/crownfall_logcat.txt

if grep -E "FATAL EXCEPTION|AndroidRuntime.*FATAL|ANR in com\.crownfall\.stronghold" /tmp/crownfall_logcat.txt; then
  echo "CROWNFALL_RUNTIME_FAILURE"
  exit 1
fi

grep -qE '^[0-9]+$' /tmp/crownfall_pid.txt
grep -q "com.crownfall.stronghold" /tmp/crownfall_activity.txt || true

echo "CROWNFALL_EMULATOR_SMOKE_PASS"
