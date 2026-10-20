#!/usr/bin/env python3
"""CROWNFALL M126: compare native AndroidThunkJava_GooglePAD_* references
with DEX **class_data method entries**, not mere ASCII string occurrences.

Read-only, bounded ZIP/DEX parser. Never opens private keystores, logs or source
files; prints only fixed statuses, counts and sanitized nonsecret API method names.
Checks that static definitions are in GameActivity/GameApplication and checks
Available()Z when native text references it. Other signatures and inheritance
are not resolved. A mismatch is a forensic lead, not a crash diagnosis.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import re
from pathlib import Path
import struct
import sys
import zipfile

NAME_RX = re.compile(rb'AndroidThunkJava_GooglePAD_[A-Za-z0-9_]{2,80}')
MAX_BUNDLE_BYTES = 2 * 1024**3
MAX_DEX_BYTES = 100 * 1024**2
MAX_NATIVE_BYTES = 500 * 1024**2
MAX_TOTAL_BYTES = 900 * 1024**2
MAX_METHOD_IDS = 300_000
MAX_CLASS_DEFS = 100_000
MAX_STRINGS = 1_000_000


class DexProblem(Exception):
    pass


def le32(b: bytes, at: int) -> int:
    if at < 0 or at + 4 > len(b):
        raise DexProblem('TRUNCATED_INTEGER')
    return struct.unpack_from('<I', b, at)[0]


def uleb(b: bytes, at: int) -> tuple[int,int]:
    value = 0
    for shift in range(0, 35, 7):
        if at >= len(b):
            raise DexProblem('TRUNCATED_ULEB')
        val = b[at]
        at += 1
        value |= (val & 127) << shift
        if not val & 128:
            if value > 0xFFFFFFFF:
                raise DexProblem('OVERSIZED_ULEB')
            return value,at
    raise DexProblem('OVERSIZED_ULEB')


def bounded_range(b: bytes, start: int, count: int, stride: int) -> None:
    if count < 0 or start < 0 or start + count*stride > len(b):
        raise DexProblem('INVALID_TABLE_RANGE')


def dex_method_entries(b: bytes, interesting: set[str]) -> tuple[set[str],set[str],set[str],set[str]]:
    """Return method_id names, defined names, activity names, and Available()Z matches.
    Counts only class_data direct/virtual methods as defined; merely present
    string_ids or method_id is NOT treated as a defined method.
    """
    if len(b) < 0x70 or not b.startswith(b'dex\n') or b[7] != 0:
        raise DexProblem('INVALID_DEX_MAGIC')
    if le32(b, 0x20) != len(b) or le32(b, 0x24) != 0x70:
        raise DexProblem('INVALID_DEX_HEADER')
    string_n, string_at = le32(b, 0x38), le32(b, 0x3C)
    type_n, type_at = le32(b, 0x40), le32(b, 0x44)
    proto_n, proto_at = le32(b, 0x48), le32(b, 0x4C)
    method_n, method_at = le32(b, 0x58), le32(b, 0x5C)
    class_n, class_at = le32(b, 0x60), le32(b, 0x64)
    if string_n > MAX_STRINGS or method_n > MAX_METHOD_IDS or class_n > MAX_CLASS_DEFS:
        raise DexProblem('EXCESSIVE_DEX_COUNTS')
    for st,n,stride in [(string_at,string_n,4),(type_at,type_n,4),(proto_at,proto_n,12),(method_at,method_n,8),(class_at,class_n,32)]:
        bounded_range(b,st,n,stride)

    target_names = set(interesting)
    strings = {}
    activity_type_ids=set()
    bool_type_ids=set()
    for type_idx in range(type_n):
        text_idx=le32(b,type_at+4*type_idx)
        if text_idx>=string_n:raise DexProblem('INVALID_TYPE_STRING_INDEX')
        start=le32(b,string_at+4*text_idx)
        _,start=uleb(b,start)
        stop=b.find(b'\0',start,min(len(b),start+250))
        if stop>=start:
            descriptor=b[start:stop]
            if descriptor.endswith(b'/GameActivity;') or descriptor.endswith(b'/GameApplication;'):
                activity_type_ids.add(type_idx)
            if descriptor==b'Z': bool_type_ids.add(type_idx)
    for i in range(string_n):
        at = le32(b, string_at+i*4)
        _, at = uleb(b, at)
        end = b.find(b'\0',at,min(len(b),at+256))
        if end == -1:
            # A long non-target string is fine; we do not parse it further.
            continue
        raw=b[at:end]
        if raw.startswith(b'AndroidThunkJava_GooglePAD_'):
            try: name=raw.decode('ascii')
            except UnicodeDecodeError: continue
            if name in target_names: strings[i]=name

    candidates={}
    for idx in range(method_n):
        at=method_at+idx*8
        class_idx,proto_idx,name_idx=struct.unpack_from('<HHI',b,at)
        if name_idx in strings and class_idx < type_n:
            if proto_idx>=proto_n: raise DexProblem('INVALID_PROTO_INDEX')
            proto_pos=proto_at+12*proto_idx
            ret_type=le32(b,proto_pos+4)
            parameter_off=le32(b,proto_pos+8)
            available_sig=(ret_type in bool_type_ids and parameter_off==0)
            candidates[idx]=(class_idx,strings[name_idx],available_sig)
    seen_ids={name for _,name,_ in candidates.values()}
    if not candidates:
        return seen_ids,set(),set(),set()

    # Check class index and code declaration, do not accept method_ids alone.
    class_to_data={}
    for i in range(class_n):
        pos=class_at+i*32
        idx=le32(b,pos)
        data_off=le32(b,pos+24)
        if idx >= type_n: raise DexProblem('INVALID_CLASS_INDEX')
        if data_off:
            if data_off>=len(b):raise DexProblem('INVALID_CLASS_DATA_OFFSET')
            if idx in class_to_data:raise DexProblem('DUPLICATE_CLASS_DEF')
            class_to_data[idx]=data_off

    defined=set()
    activity_defined=set()
    available_bool_defined=set()
    for class_idx, pos in class_to_data.items():
        static_n,pos=uleb(b,pos);inst_n,pos=uleb(b,pos)
        direct_n,pos=uleb(b,pos);virtual_n,pos=uleb(b,pos)
        if static_n+inst_n+direct_n+virtual_n>MAX_METHOD_IDS*2:
            raise DexProblem('EXCESSIVE_CLASS_DATA')
        for _ in range(static_n+inst_n):
            _,pos=uleb(b,pos);_,pos=uleb(b,pos)
        for n in (direct_n,virtual_n):
            index=0
            for _ in range(n):
                diff,pos=uleb(b,pos)
                index+=diff
                _,pos=uleb(b,pos) # flags
                _,pos=uleb(b,pos) # code_off: zero valid for native/abstract
                if index >= method_n:raise DexProblem('INVALID_METHOD_INDEX')
                match=candidates.get(index)
                if match and match[0]==class_idx:
                    defined.add(match[1])
                    if class_idx in activity_type_ids:
                        activity_defined.add(match[1])
                        if match[1]=='AndroidThunkJava_GooglePAD_Available' and match[2]:
                            available_bool_defined.add(match[1])
    return seen_ids,defined,activity_defined,available_bool_defined


def native_methods(blob: bytes) -> set[str]:
    return {match.group().decode('ascii') for match in NAME_RX.finditer(blob)}


def audit(aab: Path) -> tuple[int,dict[str,str|int]]:
    info={'M126_MODE':'READ_ONLY_DEX_METHOD_DEFINITIONS',
          'M126_CRASH_CAUSE':'UNCONFIRMED_REQUIRES_DEVICE_STACK_TRACE'}
    if aab.is_symlink() or not aab.is_file():
        info['M126_INPUT']='MISSING_OR_SYMLINK';return 2,info
    try:
        size=aab.stat().st_size
        if not (1<=size<=MAX_BUNDLE_BYTES):
            info['M126_INPUT']='INVALID_SIZE';return 2,info
        native=set(); method_ids=set();defined=set();activity_defs=set();available_bool=set();dex_count=0;so_count=0;total=0
        with zipfile.ZipFile(aab) as z:
            for ent in z.infolist():
                name=ent.filename
                kind=('DEX' if name.startswith('base/dex/') and name.endswith('.dex') else
                      'SO' if name.startswith('base/lib/arm64-v8a/') and name.endswith('.so') else None)
                if not kind:continue
                limit=MAX_DEX_BYTES if kind=='DEX' else MAX_NATIVE_BYTES
                if ent.file_size<=0 or ent.file_size>limit:
                    info['M126_INPUT']='OVERSIZED_OR_EMPTY_ENTRY';return 2,info
                total+=ent.file_size
                if total>MAX_TOTAL_BYTES:
                    info['M126_INPUT']='EXCEEDED_SCAN_BUDGET';return 2,info
                data=z.read(ent)
                if len(data)!=ent.file_size:
                    info['M126_INPUT']='TRUNCATED_ZIP';return 2,info
                if kind=='SO':
                    so_count+=1;native.update(native_methods(data))
                else:
                    dex_count+=1
                    # Native methods can appear in later SO entries; collect DEX
                    # and parse all GooglePAD method definitions independent of SO order.
                    ids,defs,act_defs,bool_defs=dex_method_entries(data,{
                        x.decode('ascii') for x in NAME_RX.findall(data)})
                    method_ids.update(ids);defined.update(defs);activity_defs.update(act_defs);available_bool.update(bool_defs)
        missing=native-defined
        only_string=native-method_ids
        not_activity=native-activity_defs
        available_required = 'AndroidThunkJava_GooglePAD_Available' in native
        available_signature_ok = 'AndroidThunkJava_GooglePAD_Available' in available_bool
        info.update({
          'M126_DEX_FILES':dex_count,
          'M126_ARM64_LIBS':so_count,
          'M126_NATIVE_PAD_METHOD_REFERENCES':len(native),
          'M126_DEX_MATCHED_METHOD_IDS':len(native&method_ids),
          'M126_DEX_MATCHED_CLASS_METHOD_DEFINITIONS':len(native&defined),
          'M126_MISSING_CLASS_METHOD_DEFINITIONS':len(missing),
          'M126_DEX_GAME_ACTIVITY_METHOD_DEFINITIONS':len(native&activity_defs),
          'M126_DEX_AVAILABLE_NOARGS_BOOL_DEFINITION': 'YES' if 'AndroidThunkJava_GooglePAD_Available' in available_bool else 'NO_OR_NOT_APPLICABLE',
          'M126_ONLY_NATIVE_NO_DEX_METHOD_ID':len(only_string),
          'M127_NATIVE_PAD_NAMES_NOT_IN_GAME_ACTIVITY':len(not_activity),
          'M127_AVAILABLE_REQUIRED_BY_NATIVE':'YES' if available_required else 'NO',
          'M127_AVAILABLE_GAME_ACTIVITY_BOOL_SIGNATURE':'MATCH' if available_signature_ok else 'UNMATCHED_OR_UNNEEDED',
        })
        if not dex_count or not so_count:
            info['M126_ASSESSMENT']='INCOMPLETE_CODE_ASSETS';return 3,info
        if not native:
            info['M126_ASSESSMENT']='NO_NATIVE_GOOGLEPAD_JNI_NAMES_FOUND';return 0,info
        if missing:
            info['M126_ASSESSMENT']='REVIEW_POTENTIAL_JNI_METHOD_MISMATCH';return 3,info
        # A definition in an unrelated DEX class is NOT evidence that Unreal's
        # Java bridge can call it on its GameActivity/GameApplication instance.
        # A custom activity can use a different name: flag for review rather
        # than falsely claim the actual runtime will fail.
        if not_activity:
            info['M126_ASSESSMENT']='REVIEW_METHOD_NOT_DEFINED_IN_EXPECTED_ACTIVITY';return 3,info
        # Unlike a textual match, this exact method has a documented no-args
        # boolean JNI signature. A non-matching overload is not sufficient.
        if available_required and not available_signature_ok:
            info['M126_ASSESSMENT']='REVIEW_AVAILABLE_JNI_SIGNATURE_MISMATCH';return 3,info
        info['M126_ASSESSMENT']='STATIC_ACTIVITY_DEFINITIONS_PRESENT_OTHER_SIGNATURES_UNVERIFIED'
        return 0,info
    except DexProblem:
        info['M126_INPUT']='DEX_PARSE_FAILED';return 2,info
    except (OSError,RuntimeError,zipfile.BadZipFile,ValueError,MemoryError):
        info['M126_INPUT']='ZIP_OR_READ_FAILED';return 2,info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--aab',type=Path,
      default=Path.home()/'crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab')
    args=p.parse_args()
    code,out=audit(args.aab)
    for key,value in out.items(): print(f'{key}={value}',flush=True)
    return code

if __name__=='__main__':sys.exit(main())
