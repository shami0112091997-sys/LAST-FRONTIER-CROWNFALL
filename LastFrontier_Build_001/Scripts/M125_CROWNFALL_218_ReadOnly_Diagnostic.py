#!/usr/bin/env python3
"""CROWNFALL M125: one-pass, read-only Unreal Android AAB triage.

No network, build, signing, archive extraction, device access, GitHub modification,
secret-file reads, or raw output from user-controlled artifacts.
Evidence is structural; it cannot establish the cause of an Android runtime exit.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

EXPECTED_BYTES = 117411826  # Observed M118 signed v218 size; not a security checksum
TRUSTED_JAR_SHA = 'a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29'
DIST = 'http://schemas.android.com/apk/distribution'
SECTION = '[/script/androidruntimesettings.androidruntimesettings]'
MARKERS = {
    'PAD_JNI_METHOD': b'AndroidThunkJava_GooglePAD_Available',
    'PAD_JNI_PREFIX': b'AndroidThunkJava_GooglePAD_',
    'PAD_PLUGIN': b'GooglePAD',
    'PLAY_CORE': b'AssetPackManager',
    'OBBASSETS': b'obbassets',
}

def display(key, value):
    # Output only fixed-key, controlled-status or integer, never a log line or path.
    print(f'M125_{key}={value}', flush=True)

def is_regular(p):
    return p.is_file() and not p.is_symlink()

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):
            h.update(block)
    return h.hexdigest()

def ini_bool(p,name):
    if not is_regular(p):
        return 'UNAVAILABLE'
    section=False; values=[]
    try:
        for line in p.read_text(encoding='utf-8-sig',errors='replace').splitlines():
            line=line.strip()
            if line.startswith('[') and line.endswith(']'):
                section=line.lower()==SECTION
            elif section and re.match(re.escape(name)+r'\s*=',line,re.I):
                values.append(line.split('=',1)[1].strip().lower())
    except OSError:
        return 'UNAVAILABLE'
    if len(values)!=1 or values[0] not in ('true','false'):
        return 'UNKNOWN'
    return values[0].upper()

def proj_flags(p):
    if not is_regular(p): return 'UNAVAILABLE','UNAVAILABLE'
    try:
        j=json.loads(p.read_text(encoding='utf-8-sig'))
        disabled = j.get('DisableEnginePluginsByDefault') is True
        plugins=j.get('Plugins',[])
        if not isinstance(plugins,list):return 'UNKNOWN','UNKNOWN'
        pads=[v for v in plugins if isinstance(v,dict) and str(v.get('Name','')).lower()=='googlepad']
        status=('NOT_EXPLICIT' if not pads else 'ENABLED' if len(pads)==1 and pads[0].get('Enabled') is True else 'DISABLED_OR_AMBIGUOUS')
        return ('YES' if disabled else 'NO'), status
    except (OSError,ValueError,TypeError,AttributeError):
        return 'UNKNOWN','UNKNOWN'

def find_markers(stream, markers):
    result={k:False for k in markers}
    tail=b'';n=max(map(len,markers.values()))-1
    while True:
        chunk=stream.read(1048576)
        if not chunk:break
        merged=tail+chunk
        for k,needle in markers.items():
            if needle in merged:result[k]=True
        tail=merged[-n:]
    return result

def delivery(xml):
    root=ET.fromstring(xml)
    node=root.find('.//{%s}delivery'%DIST)
    if node is None:return 'NOT_DECLARED'
    modes={part.tag.rsplit('}',1)[-1] for part in node}
    found=modes&{'install-time','fast-follow','on-demand'}
    return next(iter(found)).replace('-','_').upper() if len(found)==1 else 'UNKNOWN'

def check(aab,project,config,jar):
    display('MODE','READ_ONLY_NO_PRIVATE_OUTPUT')
    if not is_regular(aab):
        display('AAB','MISSING');return 2
    try:
        s=aab.stat().st_size
    except OSError:
        display('AAB','UNREADABLE');return 2
    display('AAB_SIZE_MATCH_M118','YES' if s==EXPECTED_BYTES else 'NO_REVIEW_SOURCE')
    if s<=0 or s>2*1024**3:
        display('AAB','INVALID_SIZE');return 2
    disabled,pad=proj_flags(project)
    display('PROJECT_PLUGINS_DEFAULT_DISABLED',disabled)
    display('GOOGLEPAD_DESCRIPTOR',pad)
    in_apk=ini_bool(config,'bPackageDataInsideApk')
    display('PACKAGE_DATA_INSIDE_APK',in_apk)
    dex=0;native=0;obb=0;obb_bytes=0;obb_zip='UNVERIFIED'
    matching={'DEX':dict.fromkeys(MARKERS,False),'NATIVE':dict.fromkeys(MARKERS,False)}
    total=0;modules=set()
    try:
        with zipfile.ZipFile(aab) as z:
            for entry in z.infolist():
                name=entry.filename
                if name.endswith('/manifest/AndroidManifest.xml'):
                    modules.add(name.split('/')[0])
                if entry.is_dir():continue
                if name.endswith('/assets/main.obb.png') or name.endswith('/assets/main.obb'):
                    obb+=1;obb_bytes+=entry.file_size
                    if entry.file_size<150*1024*1024:
                        with z.open(entry) as f:
                            content=f.read(150*1024*1024+1)
                        if len(content)<=150*1024*1024:
                            obb_zip='YES' if zipfile.is_zipfile(io.BytesIO(content)) else 'NO'
                kind=('DEX' if name.endswith('.dex') else
                      'NATIVE' if name.endswith('.so') and '/lib/arm64-v8a/' in name else None)
                if kind is None:continue
                if entry.file_size<=0 or entry.file_size>512*1024*1024:
                    display('SCAN','ENTRY_BOUNDS_FAIL');return 2
                total+=entry.file_size
                if total>900*1024*1024:
                    display('SCAN','TOTAL_BOUNDS_FAIL');return 2
                with z.open(entry) as f:
                    hits=find_markers(f,MARKERS)
                for key,value in hits.items():matching[kind][key]|=value
                if kind=='DEX':dex+=1
                else:native+=1
    except (OSError,RuntimeError,zipfile.BadZipFile,ValueError):
        display('AAB','ZIP_READ_FAILED');return 2
    display('ZIP_STRUCTURE','BASE_PRESENT' if 'base' in modules else 'INVALID_NO_BASE')
    display('OBBASSETS_MODULE','YES' if 'obbassets' in modules else 'NO')
    display('OBB_ASSET_COUNT',obb)
    display('OBB_ASSET_BYTES',obb_bytes)
    display('OBB_NESTED_ZIP',obb_zip)
    display('DEX_FILES',dex)
    display('ARM64_LIBS',native)
    for kind in ('DEX','NATIVE'):
        for key in MARKERS:
            display(f'{kind}_{key}','SEEN' if matching[kind][key] else 'NOT_SEEN')
    if not is_regular(jar):
        display('BUNDLETOOL','UNAVAILABLE')
    elif digest(jar)!=TRUSTED_JAR_SHA:
        display('BUNDLETOOL','WRONG_CHECKSUM')
    elif 'obbassets' not in modules:
        display('ASSET_DELIVERY_MODE','NO_OBBASSETS_MODULE')
    else:
        try:
            result=subprocess.run(['java','-jar',str(jar),'dump','manifest',f'--bundle={aab}','--module=obbassets'],capture_output=True,text=True,timeout=90,check=False)
            if result.returncode:
                display('ASSET_DELIVERY_MODE','DUMP_FAILED')
            else:
                try:display('ASSET_DELIVERY_MODE',delivery(result.stdout))
                except ET.ParseError:display('ASSET_DELIVERY_MODE','XML_PARSE_FAILED')
        except (OSError,subprocess.TimeoutExpired):
            display('ASSET_DELIVERY_MODE','JAVA_OR_TOOL_FAILED')
    if 'obbassets' in modules and (in_apk=='TRUE' or disabled=='YES' and pad!='ENABLED'):
        display('PACKAGING_HYPOTHESIS','REVIEW_CONFIG_CONSISTENCY')
    else: display('PACKAGING_HYPOTHESIS','NO_OBVIOUS_FLAG_CONFLICT_OR_UNKNOWN')
    display('CRASH_CAUSE','UNKNOWN_NEEDS_ACTUAL_ANDROID_STACK_TRACE')
    if 'base' not in modules or dex==0 or native==0:return 3
    return 0

def main():
    p=argparse.ArgumentParser(description=__doc__)
    root=Path.home()/'crownfall/M106_RELEASE_SANDBOX_v218'
    p.add_argument('--aab',type=Path,default=root/'Binaries/Android/LastFrontier-Android-Shipping.aab')
    p.add_argument('--project',type=Path,default=root/'LastFrontier.uproject')
    p.add_argument('--config',type=Path,default=root/'Config/DefaultEngine.ini')
    p.add_argument('--jar',type=Path,default=Path.home()/'tools/bundletool-all-1.18.3.jar')
    a=p.parse_args()
    return check(a.aab,a.project,a.config,a.jar)
if __name__=='__main__':sys.exit(main())

