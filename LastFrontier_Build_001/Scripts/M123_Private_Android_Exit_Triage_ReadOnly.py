#!/usr/bin/env python3
"""M123: private, read-only triage of Android crash/exit text.

Prints category hit counts and status only. Never prints log lines, file paths,
package process IDs, device identifiers, IP addresses, or text excerpts.
IMPORTANT: keyword matches are leads, not proof of root cause.
"""
import argparse
from pathlib import Path
import re
import stat
import sys

PACKAGE = "com.crownfall.stronghold"
PATTERNS = {
    "JNI_METHOD": r"Failed to find Method|Method\s*!=\s*0|NoSuchMethodError|JNI DETECTED ERROR",
    "JAVA_EXCEPTION": r"FATAL EXCEPTION|AndroidRuntime|UnsatisfiedLinkError|ClassNotFoundException",
    "NATIVE_SIGNAL": r"Fatal signal\s+(?:6|11)|SIGABRT|SIGSEGV|signal\s+(?:6|11)\s+\(|native crash|backtrace:",
    "DYNAMIC_LINKER": r"dlopen failed|cannot locate symbol|linker.*not found|library .* not found",
    "ASSET_PACK": r"GooglePAD|AssetPack|asset.pack|obbassets|main\.obb|OBB.*not found|No OBB found",
    "UNREAL_ASSET": r"Failed to open descriptor file|LogPakFile|pak.*mount|Failed to load package|TestMap|ShaderCodeLibrary",
    "GRAPHICS": r"VK_ERROR|vkCreateInstance|Vulkan|RHIInit|EGL_BAD|OpenGL.*error",
    "MEMORY_KILL": r"lowmemorykiller|lmkd|OutOfMemoryError|REASON_LOW_MEMORY|am_kill",
    "PLANNED_EXIT": r"finishAndRemoveTask|finish\(\)|Force finishing activity|REASON_USER_REQUESTED",
}
COMPILED = {k: re.compile(v, re.I) for k,v in PATTERNS.items()}
# A word boundary also matches before a dot; reject sibling packages such as
# com.crownfall.stronghold.other while allowing Android's named subprocesses.
PROCESS_NAME = re.escape(PACKAGE) + r"(?::[A-Za-z0-9_][A-Za-z0-9_.-]*)?"
PACKAGE_CONTEXT = re.compile(
    r"(?<![A-Za-z0-9_.:-])" + PROCESS_NAME + r"(?![A-Za-z0-9_.:-])")
START_PID = re.compile(
    r"\bStart proc\s+(\d+)\s*:\s*" + PROCESS_NAME + r"(?=/|\s|$)", re.I)
JAVA_PID = re.compile(
    r"\bProcess:\s*" + PROCESS_NAME + r",\s*PID:\s*(\d+)", re.I)
LOGCAT_PID = re.compile(r"^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+\s+(\d+)\s+\d+\s+", re.I)

def triage(text):
    lines = text.splitlines()
    pids = {m.group(1) for line in lines for rx in (START_PID,JAVA_PID)
            if (m:=rx.search(line))}
    package_lines = {i for i,line in enumerate(lines) if PACKAGE_CONTEXT.search(line)}
    if not package_lines and not pids:
        return "NO_PACKAGE_EVIDENCE", {key:0 for key in COMPILED}, 0
    # Keep nearby stack/cause context, or lines tagged with a known package PID.
    near_package = set()
    for i in package_lines:
        near_package.update(range(max(0,i-2),min(len(lines),i+35)))
    relevant = set()
    for i,line in enumerate(lines):
        m=LOGCAT_PID.match(line)
        if m:
            # Without a verified package PID, a nearby log line from another
            # process is not evidence of a CROWNFALL crash. Only accept a
            # PID-tagged line if that line names the exact package itself.
            if (m.group(1) in pids) or (not pids and i in package_lines):
                relevant.add(i)
        elif i in near_package:
            # Java stack continuations may lack logcat PID prefixes.
            relevant.add(i)
    selected = [lines[i] for i in sorted(relevant)]
    result = {key:sum(bool(rx.search(line)) for line in selected)
              for key,rx in COMPILED.items()}
    return ("PACKAGE_PID_FOUND" if pids else "PACKAGE_CONTEXT_ONLY"),result,len(selected)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",type=Path,required=True,
                    help="Private Android logcat/exit-info excerpt, NOT public upload")
    args=ap.parse_args()
    p=args.input
    if p.is_symlink() or not p.is_file():
        print("M123_INPUT=MISSING_OR_SYMLINK");return 2
    s=p.stat()
    if not stat.S_ISREG(s.st_mode) or s.st_size>20*1024*1024 or s.st_size==0:
        print("M123_INPUT=EMPTY_OR_TOO_LARGE");return 2
    if s.st_mode & 0o007:
        print("M123_INPUT=WORLD_ACCESSIBLE_REVIEW");return 2
    try:
        status,counts,selected=triage(p.read_text(encoding="utf-8",errors="replace"))
    except OSError:
        print("M123_INPUT=READ_ERROR");return 2
    print("M123_MODE=READ_ONLY_NO_LOG_LINES")
    print("M123_SCOPE="+status)
    print("M123_RELEVANT_LINES="+str(min(selected,99999)))
    for name,count in counts.items():
        print("M123_"+name+"_HITS="+str(min(count,9999)))
    print("M123_CAUSE=UNCONFIRMED_NEED_MATCHED_STACK_TRACE")
    print("M123_RAW_LOG=NOT_UPLOADED")
    return 0
if __name__=="__main__":
    sys.exit(main())
