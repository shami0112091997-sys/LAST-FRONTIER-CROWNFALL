#!/usr/bin/env python3
"""Read-only CROWNFALL Android App Bundle layout + Unreal/PAD diagnostic.
Only prints invariant counts/status, never credentials, APK contents, or file paths.
Exit 0 = completed examination, 2 = cannot inspect, 3 = potential mismatch/review.
This is not a runtime crash explanation or a Google Play acceptance check.
"""
import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path


def emit(key, value):
    print(f'M121_{key}={value}', flush=True)


def config_value(path, key):
    if not path or not path.is_file() or path.is_symlink():
        return 'UNAVAILABLE'
    # Only read the explicitly named non-secret entry in the Android section.
    content = path.read_text(encoding='utf-8-sig', errors='replace')
    section = False
    matches = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith('[') and s.endswith(']'):
            section = s.lower() == '[/script/androidruntimesettings.androidruntimesettings]'
            continue
        if section and re.match(rf'^{re.escape(key)}\s*=', s, re.I):
            matches.append(s.split('=', 1)[1].strip().lower())
    return matches[0] if len(matches) == 1 and matches[0] in {'true','false'} else 'UNKNOWN'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--aab', type=Path, default=Path.home()/'crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab')
    p.add_argument('--ini', type=Path, default=Path.home()/'crownfall/M106_RELEASE_SANDBOX_v218/Config/DefaultEngine.ini')
    p.add_argument('--uproject', type=Path, default=Path.home()/'crownfall/M106_RELEASE_SANDBOX_v218/LastFrontier.uproject')
    args = p.parse_args()
    emit('MODE', 'READ_ONLY_NO_SECRETS')
    aab = args.aab
    if not aab.is_file() or aab.is_symlink():
        emit('AAB', 'MISSING_OR_UNSAFE_PATH')
        return 2
    try:
        with zipfile.ZipFile(aab) as z:
            info = [i for i in z.infolist() if not i.is_dir()]
            entries = {i.filename for i in info}
            if not {'BundleConfig.pb','base/manifest/AndroidManifest.xml'}.issubset(entries):
                emit('BUNDLE_STRUCTURE','REVIEW_REQUIRED')
                return 3
            emit('BUNDLE_STRUCTURE', 'PASS')
            modules = sorted({x.split('/')[0] for x in entries if x.endswith('/manifest/AndroidManifest.xml')})
            emit('BASE_PRESENT', 'YES' if 'base' in modules else 'NO')
            emit('MODULE_COUNT', len(modules))
            packs = [m for m in modules if m != 'base']
            emit('EXTRA_MODULE_COUNT',len(packs))
            obb = [i for i in info if i.filename.endswith('/assets/main.obb.png') or i.filename.endswith('/assets/main.obb')]
            emit('OBB_ASSET_COUNT',len(obb))
            emit('OBB_ASSET_BYTES',sum(i.file_size for i in obb))
            arch = [i for i in info if i.filename.endswith(('.pak','.utoc','.ucas'))]
            emit('VISIBLE_UE_ARCHIVE_COUNT',len(arch))
            arm64 = [i for i in info if i.filename.startswith('base/lib/arm64-v8a/') and i.filename.endswith('.so')]
            emit('ARM64_LIB_COUNT',len(arm64))
            embedded = 0
            nested = 0
            skipped = 0
            for f in obb:
                if f.file_size > 192*1024*1024:
                    skipped += 1
                    continue
                with z.open(f) as fh:
                    raw = fh.read(192*1024*1024+1)
                if len(raw) > 192*1024*1024:
                    skipped += 1
                elif zipfile.is_zipfile(io.BytesIO(raw)):
                    with zipfile.ZipFile(io.BytesIO(raw)) as inner:
                        nested += 1
                        embedded += sum(n.lower().endswith(('.pak','.ucas','.utoc')) for n in inner.namelist())
            emit('INNER_OBB_ZIP_COUNT',nested)
            emit('INNER_UE_ARCHIVE_COUNT',embedded)
            emit('OBB_TOO_LARGE_TO_INSPECT',skipped)
    except (OSError, zipfile.BadZipFile, RuntimeError, ValueError):
        emit('ARCHIVE', 'FAILED_TO_READ')
        return 2
    if args.uproject.is_file() and not args.uproject.is_symlink():
        try:
            proj=json.loads(args.uproject.read_text(encoding='utf-8'))
            defaults=proj.get('DisableEnginePluginsByDefault',False) is True
            explicit=[x for x in proj.get('Plugins',[]) if x.get('Name','').lower()=='googlepad' and x.get('Enabled') is True]
            emit('ENGINE_PLUGINS_DISABLED_BY_DEFAULT','YES' if defaults else 'NO')
            emit('GOOGLEPAD_EXPLICITLY_ENABLED','YES' if explicit else 'NO')
            if defaults and not explicit and obb:
                emit('PLUGIN_CONFIGURATION','REVIEW_GOOGLEPAD_DISABLED_BY_DEFAULT')
        except (ValueError,OSError,TypeError):
            emit('PROJECT_DESCRIPTOR','REVIEW_REQUIRED')
    else:
        emit('PROJECT_DESCRIPTOR','UNAVAILABLE')
    setting = config_value(args.ini, 'bPackageDataInsideApk')
    emit('ANDROID_PACKAGE_DATA_INSIDE_APK', setting.upper())
    if obb and setting == 'true':
        emit('PAD_CONFIGURATION', 'REVIEW_MIXED_OBB_ASSETS_AND_PACKAGE_INSIDE_APK')
        return 3
    if obb and setting == 'false':
        emit('PAD_CONFIGURATION','REVIEW_INSTALL_TIME_MOUNT_ON_DEVICE')
        return 3
    if obb:
        emit('PAD_CONFIGURATION','REVIEW_CONFIG_UNAVAILABLE')
        return 3
    emit('PAD_CONFIGURATION','NO_OBB_PACK_FOUND_VERIFY_BASE_ASSETS')
    return 0

if __name__ == '__main__':
    sys.exit(main())

