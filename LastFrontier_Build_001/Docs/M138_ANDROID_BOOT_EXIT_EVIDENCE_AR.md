# M138 — Android boot/exit evidence (tester machine, read-only)

## Purpose

Issue #3 is still blocked by the absence of the **actual installed versionCode** and **first time-matched Android/Unreal crash** for Play v218. Prior M69 performance sampling requires an already-running process, so it cannot investigate an app that exits at its splash screen.

This tool collects a **private, limited snapshot** from a separate tester-owned/authorized Android device using `adb`, then emits a **sanitized JSON summary**. It does not install, start, stop, or manipulate CROWNFALL; it does not clear log buffers or upload any device data.

## Prerequisites
- Licensed, authorized physical Android test device with the game already installed, attached to a tester's computer with Android platform-tools (`adb`).
- Exactly one connected authorized device; on a phone-only workflow, use a trusted tester computer instead. **No access to the user's phone is needed or requested.**
- Python 3.10+ and files from the `m138-android-startup-evidence-agent` branch (includes `M123_Private_Android_Exit_Triage_ReadOnly.py`).

## Usage on tester's machine

```bash
cd LastFrontier_Build_001/Scripts
python3 M138_Android_Boot_Exit_Evidence_ReadOnly.py
python3 -m unittest -v test_M138_readonly.py
```

A tester should reproduce the crash *manually*, note the exact device-local time and then take this snapshot immediately. Do not share raw Android logs, serial numbers or Android application data publicly.

## Limitations

- A `versionCode=218` value reports the **currently installed version**, not its Play Console delivery path or the version installed when an earlier crash occurred.
- The `logcat` **crash** buffer can contain old entries; it omits many native/asset-pack initialization messages from other buffers.
- `dumpsys activity exit-info` may be unavailable on some Android versions or privilege configurations.
- The classifier returns **counts**, not exception stacks. It is not a root-cause determination.
- Real verification still needs a timestamp-matched **first fatal event**, source/AAB provenance, UE Editor load + Cook, signed test package >218, and a monitored physical device launch.

**Nothing in this PR establishes UE Compile, Cook, AAB 218 health or successful Android launch.** No build is triggered by this change.
