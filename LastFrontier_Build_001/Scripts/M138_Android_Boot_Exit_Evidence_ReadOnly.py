#!/usr/bin/env python3
"""M138: read-only, privacy-conscious Android startup-exit triage.

Run ONLY on a tester-controlled computer with Android platform-tools and exactly
one authorized, already-connected test device. Never install, launch, stop, or
clear logs. Print sanitized aggregate JSON, not raw device text or serial numbers.

Historic crash-buffer entries may be stale: matches are diagnostic hints, NOT
evidence that the installed build produced that particular crash.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys

PKG = "com.crownfall.stronghold"
MAX_TEXT = 4_000_000
VERSION_PATTERN = re.compile(r"\bversionCode=(\d+)\b")
STATUS_MISSING = "UNAVAILABLE_OR_DENIED"


def read_adb(argv: list[str], timeout: int = 20) -> str | None:
    try:
        result = subprocess.run(["adb", *argv], capture_output=True, text=True,
                                errors="replace", timeout=timeout, check=False)
        if result.returncode != 0 or len(result.stdout) > MAX_TEXT:
            return None
        return result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return None


def select_authorized_device(devices_text: str | None) -> str | None:
    if not devices_text:
        return None
    accepted = []
    for line in devices_text.splitlines():
        if line.startswith("List of devices") or not line.strip() or line.startswith("* daemon"):
            continue
        columns = line.split()
        if len(columns) >= 2 and columns[1] == "device":
            accepted.append(columns[0])
        else:
            return None
    return accepted[0] if len(accepted) == 1 else None


def parse_version(text: str | None) -> int | None:
    if not text:
        return None
    versions = set(VERSION_PATTERN.findall(text))
    return int(next(iter(versions))) if len(versions) == 1 else None


def classify_excerpts(crash_text: str | None, exit_text: str | None) -> dict:
    # Existing M123 classifier processes text in memory and never emits raw logs.
    try:
        from M123_Private_Android_Exit_Triage_ReadOnly import triage
    except ImportError:
        return {"status": "LOCAL_CLASSIFIER_NOT_PRESENT", "hits": {},
                "relevant_lines": 0}
    a = triage(crash_text or "")
    b = triage(exit_text or "")
    keys = set(a[1]) | set(b[1])
    return {
        "status": "PACKAGE_CONTEXT_PRESENT" if (a[2] or b[2]) else "NO_PACKAGE_CONTEXT",
        "hits": {k: min(9999, a[1].get(k, 0) + b[1].get(k, 0)) for k in sorted(keys)},
        "relevant_lines": min(99999, a[2] + b[2]),
    }


def collect() -> tuple[dict, int]:
    summary = {
        "tool": "M138", "mode": "READ_ONLY", "package": PKG,
        "installed_version_code": None, "logcat_crash_buffer": "NOT_READ",
        "exit_info": "NOT_READ",
        "evidence_level": "HINTS_ONLY_NOT_BUILD_OR_RUNTIME_PROOF",
        "log_time_correlation": "NOT_ESTABLISHED",
        "app_launched_by_script": False, "raw_logs_saved": False,
        "device_identifiers_printed": False, "device_modified": False,
        "root_cause": "UNCONFIRMED",
    }
    if not shutil.which("adb"):
        summary["status"] = "BLOCKED_ADB_NOT_INSTALLED"
        return summary, 2
    serial = select_authorized_device(read_adb(["devices"]))
    if not serial:
        summary["status"] = "BLOCKED_EXACTLY_ONE_AUTHORIZED_DEVICE_REQUIRED"
        return summary, 2
    prefix = ["-s", serial]
    paths = read_adb([*prefix, "shell", "pm", "path", PKG])
    if not paths or not paths.lstrip().startswith("package:"):
        summary["status"] = "BLOCKED_PACKAGE_NOT_INSTALLED"
        return summary, 2

    package_info = read_adb([*prefix, "shell", "dumpsys", "package", PKG])
    summary["installed_version_code"] = parse_version(package_info)
    # Never clear crash buffer: that would destroy preexisting forensic evidence.
    crash = read_adb([*prefix, "logcat", "-b", "crash", "-d", "-t", "1200", "-v", "threadtime"])
    summary["logcat_crash_buffer"] = "READ" if crash is not None else STATUS_MISSING
    exit_info = read_adb([*prefix, "shell", "dumpsys", "activity", "exit-info", PKG])
    summary["exit_info"] = "READ" if exit_info is not None else STATUS_MISSING
    summary["classifier"] = classify_excerpts(crash, exit_info)
    summary["status"] = "SNAPSHOT_COLLECTED_REQUIRES_TIME_MATCHED_REPRODUCTION"
    if summary["installed_version_code"] is None:
        summary["version_warning"] = "INSTALLED_BUILD_NOT_VERIFIED"
    return summary, 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    result, rc = collect()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main())
