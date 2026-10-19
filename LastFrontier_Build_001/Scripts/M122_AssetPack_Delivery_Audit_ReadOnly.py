#!/usr/bin/env python3
"""CROWNFALL M122: inspect installed-asset delivery in an AAB without changing it.

Reads only the designated AAB, the isolated M106 project descriptor/config,
and the verified official bundletool JAR. Never prints full manifests, passwords,
filesystem paths, or device identifiers. A technical mismatch is not a crash diagnosis.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

BUNDLETOOL_SHA256 = 'a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29'
ANDROID_SECTION = '[/script/androidruntimesettings.androidruntimesettings]'
DIST_NS = 'http://schemas.android.com/apk/distribution'

def emit(name, value):
    print('M122_' + name + '=' + str(value), flush=True)

def readable_file(p):
    return p.is_file() and not p.is_symlink()

def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):
            h.update(chunk)
    return h.hexdigest()

def android_bool_setting(p, key):
    if not readable_file(p):
        return 'UNAVAILABLE'
    section = False
    vals = []
    for line in p.read_text(encoding='utf-8-sig',errors='replace').splitlines():
        s=line.strip()
        if s.startswith('[') and s.endswith(']'):
            section=s.casefold()==ANDROID_SECTION
            continue
        if section and re.match(r'^' + re.escape(key) + r'\s*=',s,re.IGNORECASE):
            vals.append(s.split('=',1)[1].strip().casefold())
    if len(vals)==1 and vals[0] in ('true','false'):
        return vals[0].upper()
    return 'UNKNOWN'

def project_flags(p):
    if not readable_file(p):
        return ('UNKNOWN','UNKNOWN')
    try:
        j=json.loads(p.read_text(encoding='utf-8-sig'))
        disabled = j.get('DisableEnginePluginsByDefault') is True
        entries = [p for p in j.get('Plugins',[]) if isinstance(p,dict) and p.get('Name','').casefold()=='googlepad']
        if len(entries)>1:
            pad='DUPLICATE'
        elif not entries:
            pad='NOT_EXPLICIT'
        else:
            pad='ENABLED' if entries[0].get('Enabled') is True else 'DISABLED'
        return ('YES' if disabled else 'NO',pad)
    except (ValueError,OSError,TypeError,AttributeError):
        return ('UNKNOWN','UNKNOWN')

def parse_delivery(xml_string):
    root=ET.fromstring(xml_string)
    el=root.find('.//{' + DIST_NS + '}delivery')
    if el is None:
        return 'NOT_DECLARED'
    tags={c.tag.rsplit('}',1)[-1].replace('-','_').upper() for c in el}
    modes=tags.intersection({'INSTALL_TIME','FAST_FOLLOW','ON_DEMAND'})
    return next(iter(modes)) if len(modes)==1 else 'UNKNOWN'

def run(*,aab,jar,ini,uproject,java='java'):
    emit('MODE','READ_ONLY')
    if not readable_file(aab):
        emit('AAB','MISSING');return 2
    if not readable_file(jar) or sha256(jar)!=BUNDLETOOL_SHA256:
        emit('TRUSTED_BUNDLETOOL','MISSING_OR_SHA_MISMATCH');return 2
    emit('TRUSTED_BUNDLETOOL','PASS')
    try:
        with zipfile.ZipFile(aab) as z:
            files=set(z.namelist())
            names=sorted({x.split('/')[0] for x in files if x.endswith('/manifest/AndroidManifest.xml')})
            if 'base' not in names:
                emit('BASE_MODULE','MISSING');return 2
            packs=[n for n in names if n!='base']
            emit('ADDITIONAL_MODULES',len(packs))
            has_obb='obbassets' in packs
            emit('OBBASSETS_MODULE','YES' if has_obb else 'NO')
            emit('OBB_CONTENT','YES' if any(x.startswith('obbassets/assets/') and ('main.obb' in x) for x in files) else 'NO')
    except (OSError,zipfile.BadZipFile):
        emit('AAB','INVALID_ZIP');return 2
    pkg_inside=android_bool_setting(ini,'bPackageDataInsideApk')
    plugins_off,pad=project_flags(uproject)
    emit('PACKAGE_DATA_INSIDE_APK',pkg_inside)
    emit('ENGINE_PLUGINS_DISABLED_BY_DEFAULT',plugins_off)
    emit('GOOGLEPAD_PLUGIN_ENTRY',pad)
    if not has_obb:
        emit('ASSET_PACK_DELIVERY','NOT_APPLICABLE')
        emit('STATUS','REVIEW_BASE_GAME_CONTENT')
        return 0
    try:
        completed=subprocess.run([java,'-jar',str(jar),'dump','manifest',f'--bundle={aab}','--module=obbassets'],capture_output=True,text=True,timeout=90,check=False)
    except (OSError,subprocess.TimeoutExpired):
        emit('ASSET_PACK_DELIVERY','TOOL_UNAVAILABLE');return 2
    if completed.returncode:
        emit('ASSET_PACK_DELIVERY','DUMP_FAILED');return 2
    try:
        mode=parse_delivery(completed.stdout)
    except ET.ParseError:
        emit('ASSET_PACK_DELIVERY','XML_PARSE_FAILED');return 2
    emit('ASSET_PACK_DELIVERY',mode)
    if mode=='INSTALL_TIME':
        emit('INSTALL_TIME','YES')
    elif mode in ('FAST_FOLLOW','ON_DEMAND'):
        emit('STARTUP_MAY_PRECEDE_ASSETS','YES')
    else:
        emit('INSTALL_TIME','UNVERIFIED')
    if plugins_off=='YES' and pad!='ENABLED':
        emit('GOOGLEPAD_PLUGIN','REVIEW_EFFECTIVE_ENGINE_SETTINGS')
    if pkg_inside=='TRUE':
        emit('ASSET_PACK_ANDROID_CONFIG','REVIEW_CONSISTENCY')
    emit('CRASH_CAUSE','UNCONFIRMED_NEED_DEVICE_STACK_TRACE')
    return 0

def main():
    default=Path.home()/'crownfall/M106_RELEASE_SANDBOX_v218'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aab',type=Path,default=default/'Binaries/Android/LastFrontier-Android-Shipping.aab')
    parser.add_argument('--jar',type=Path,default=Path.home()/'tools/bundletool-all-1.18.3.jar')
    parser.add_argument('--ini',type=Path,default=default/'Config/DefaultEngine.ini')
    parser.add_argument('--uproject',type=Path,default=default/'LastFrontier.uproject')
    args=parser.parse_args()
    sys.exit(run(aab=args.aab,jar=args.jar,ini=args.ini,uproject=args.uproject))

if __name__=='__main__':main()
