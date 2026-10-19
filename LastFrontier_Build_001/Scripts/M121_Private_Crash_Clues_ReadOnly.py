#!/usr/bin/env python3
"""Summarize occurrence counts of known Android/UE crash indicators in a private text log.
Never prints log lines, names, passwords, URLs, file paths, IDs or personal data.
Best used on logcat excerpt or Play pre-launch stack text after redaction.
Not a diagnostic proof; categories are keyword indicators only.
"""
import argparse
import re
from pathlib import Path

CATEGORIES = {
 'FATAL_JAVA': r'FATAL EXCEPTION|AndroidRuntime|RuntimeException|SecurityException',
 'NATIVE_CRASH': r'Fatal signal|SIGSEGV|SIGABRT|backtrace:|tombstone',
 'MISSING_NATIVE_LIBRARY': r'UnsatisfiedLinkError|dlopen failed|cannot locate symbol|linker.*not found',
 'ASSET_DELIVERY': r'GooglePAD|asset pack|AssetPack_|obbassets|missing.*obb|obb.*not found',
 'UNREAL_CONTENT': r'Failed to open descriptor|PakFile|Failed to mount|TestMap|Failed to load package|ShaderCodeLibrary',
 'GRAPHICS': r'Vulkan|VK_ERROR|EGL_BAD|OpenGL|RHI failed|vulkan loader',
 'PERMISSION_OR_STORAGE': r'Permission denied|EACCES|storage access|FileNotFoundException',
 'ANDROID_TERMINATION': r'Force finishing activity|Killing.*crownfall|Process .*crownfall.*has died',
}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True,type=Path)
    arg=ap.parse_args()
    if not arg.input.is_file() or arg.input.is_symlink():
        print('M121_CRASH_INPUT=MISSING_OR_UNSAFE_PATH')
        return 2
    if arg.input.stat().st_size > 40*1024*1024:
        print('M121_CRASH_INPUT=TOO_LARGE')
        return 2
    txt=arg.input.read_text(encoding='utf-8',errors='replace')
    print('M121_CRASH_TRIAGE=KEYWORD_COUNTS_ONLY')
    for label,rx in CATEGORIES.items():
        count=len(re.findall(rx,txt,re.I))
        print(f'M121_{label}_HITS={min(count,9999)}')
    print('M121_CAUSE=NOT_YET_PROVEN')
    return 0
if __name__=='__main__':
    raise SystemExit(main())

