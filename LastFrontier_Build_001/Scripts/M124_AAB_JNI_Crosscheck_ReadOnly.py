#!/usr/bin/env python3
"""M124: read-only Android Unreal AAB Java/native GooglePAD method-string correlation.

Does not inspect passwords, private config, signing files or logs. Emits booleans
for named static byte patterns; strings alone do NOT prove method definitions or
runtime availability, and missing strings do NOT prove missing methods.
"""
from __future__ import annotations
import argparse
import stat
import sys
import zipfile
from pathlib import Path

PATTERNS = {
    'GOOGLEPAD_JNI': b'AndroidThunkJava_GooglePAD_',
    'GOOGLEPAD_AVAILABILITY_METHOD': b'AndroidThunkJava_GooglePAD_Available',
    'GOOGLEPAD': b'GooglePAD',
    'PLAY_ASSET_DELIVERY': b'AssetPackManager',
    'OBBASSETS': b'obbassets',
    'NATIVE_ABI_ERROR': b'UnsatisfiedLinkError',
}
LIMITS = {'.dex': 80*1024*1024, '.so': 512*1024*1024}
MAX_INSPECT = 800*1024*1024


def scan_stream(stream, patterns):
    found = {k: False for k in patterns}
    overlap = max(len(p) for p in patterns.values())-1
    tail = b''
    while True:
        b = stream.read(1024*1024)
        if not b:
            break
        combined = tail+b
        for k,pat in patterns.items():
            if not found[k] and pat in combined:
                found[k] = True
        tail = combined[-overlap:]
    return found


def check(aab):
    if aab.is_symlink() or not aab.is_file() or aab.stat().st_size > 2*1024**3:
        return 2, {'M124_INPUT': 'MISSING_UNSAFE_OR_TOO_LARGE'}
    seen = {'DEX': {p:False for p in PATTERNS},
            'NATIVE': {p:False for p in PATTERNS}}
    counts={'DEX':0,'NATIVE':0}
    total=0
    try:
        with zipfile.ZipFile(aab) as z:
            for info in z.infolist():
                name=info.filename
                kind = ('DEX' if name.endswith('.dex') else
                        'NATIVE' if name.endswith('.so') and '/lib/arm64-v8a/' in name else None)
                if not kind:
                    continue
                suffix = '.dex' if kind=='DEX' else '.so'
                if info.file_size > LIMITS[suffix] or info.file_size <= 0:
                    return 2, {'M124_BOUNDED_SCAN': 'ENTRY_TOO_LARGE_OR_EMPTY'}
                total += info.file_size
                if total>MAX_INSPECT:
                    return 2, {'M124_BOUNDED_SCAN': 'TOTAL_TOO_LARGE'}
                counts[kind]+=1
                with z.open(info) as f:
                    hits=scan_stream(f,PATTERNS)
                for k,yes in hits.items():
                    seen[kind][k] |= yes
    except (OSError, zipfile.BadZipFile, RuntimeError, ValueError):
        return 2, {'M124_INPUT':'BAD_AAB_OR_READ_ERROR'}
    out={'M124_MODE':'READ_ONLY_STATIC_STRING_CHECK',
         'M124_DEX_FILES':counts['DEX'],
         'M124_ARM64_LIBS':counts['NATIVE']}
    for kind in ('DEX','NATIVE'):
        for marker in PATTERNS:
            out['M124_'+kind+'_'+marker]='SEEN' if seen[kind][marker] else 'NOT_SEEN'
    if counts['DEX']==0 or counts['NATIVE']==0:
        out['M124_ASSESSMENT']='REVIEW_MISSING_DEX_OR_NATIVE'
        return 3,out
    if seen['NATIVE']['GOOGLEPAD_AVAILABILITY_METHOD'] and not seen['DEX']['GOOGLEPAD_AVAILABILITY_METHOD']:
        out['M124_ASSESSMENT']='REVIEW_NATIVE_JNI_STRING_WITHOUT_DEX_MATCH'
    elif seen['DEX']['GOOGLEPAD_AVAILABILITY_METHOD'] and not seen['NATIVE']['GOOGLEPAD_AVAILABILITY_METHOD']:
        out['M124_ASSESSMENT']='REVIEW_DEX_JNI_STRING_WITHOUT_NATIVE_MATCH'
    elif seen['NATIVE']['GOOGLEPAD_AVAILABILITY_METHOD'] and seen['DEX']['GOOGLEPAD_AVAILABILITY_METHOD']:
        out['M124_ASSESSMENT']='STATIC_STRING_MATCH_ONLY_NOT_PROOF_OF_RUNTIME'
    else:
        out['M124_ASSESSMENT']='NO_AVAILABILITY_METHOD_STRING_FOUND_IN_SCANNED_FILES'
    out['M124_CRASH_CAUSE']='UNPROVEN_NEEDS_DEVICE_LOG'
    return 0,out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--aab',type=Path,default=Path.home()/'crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab')
    args=ap.parse_args()
    code,lines=check(args.aab)
    for k,value in lines.items():
        print(f'{k}={value}',flush=True)
    return code

if __name__=='__main__':
    sys.exit(main())

