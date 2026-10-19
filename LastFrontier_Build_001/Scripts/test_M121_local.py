#!/usr/bin/env python3
"""Synthetic fixture tests only, no genuine CROWNFALL binaries or secrets."""
from pathlib import Path
import io
import subprocess
import tempfile
import zipfile

D=Path(__file__).resolve().parent
S=D/'M121_AAB_AssetDelivery_ReadOnly.py'
C=D/'M121_Private_Crash_Clues_ReadOnly.py'
def test_pack(root,setting,missing=False):
    aab=root/'test.aab'
    inner=io.BytesIO()
    with zipfile.ZipFile(inner,'w') as z:
        z.writestr('LastFrontier-Android_ASTC.pak',b'fake')
    with zipfile.ZipFile(aab,'w') as z:
        z.writestr('BundleConfig.pb',b'fake')
        if not missing:
            z.writestr('base/manifest/AndroidManifest.xml',b'fake')
        z.writestr('obbassets/manifest/AndroidManifest.xml',b'fake')
        z.writestr('obbassets/assets/main.obb.png',inner.getvalue())
        z.writestr('base/lib/arm64-v8a/libUnreal.so',b'fake')
    ini=root/'DefaultEngine.ini'
    ini.write_text('[X]\nbPackageDataInsideApk=False\n[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]\nbPackageDataInsideApk='+setting+'\n')
    p=subprocess.run(['python3',str(S),'--aab',str(aab),'--ini',str(ini)],capture_output=True,text=True)
    return p
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    r=test_pack(root,'True')
    assert r.returncode==3 and 'REVIEW_MIXED' in r.stdout and 'M121_INNER_UE_ARCHIVE_COUNT=1' in r.stdout
    r=test_pack(root,'False')
    assert r.returncode==3 and 'REVIEW_INSTALL_TIME_MOUNT_ON_DEVICE' in r.stdout
    import json
    (root/'LastFrontier.uproject').write_text(json.dumps({'DisableEnginePluginsByDefault':True,'Plugins':[]}))
    r=subprocess.run(['python3',str(S),'--aab',str(root/'test.aab'),'--ini',str(root/'DefaultEngine.ini'),'--uproject',str(root/'LastFrontier.uproject')],capture_output=True,text=True)
    assert 'M121_PLUGIN_CONFIGURATION=REVIEW_GOOGLEPAD_DISABLED_BY_DEFAULT' in r.stdout
    r=test_pack(root,'False',missing=True)
    assert r.returncode==3 and 'M121_BUNDLE_STRUCTURE=REVIEW_REQUIRED' in r.stdout
    log=root/'private.txt';log.write_text('contact test_user@example.com\nFatal signal 11\nVK_ERROR_DEVICE_LOST\nobbassets missing OBB\n')
    p=subprocess.run(['python3',str(C),'--input',str(log)],capture_output=True,text=True)
    assert p.returncode==0 and 'M121_NATIVE_CRASH_HITS=1' in p.stdout and 'M121_GRAPHICS_HITS=1' in p.stdout and 'example.com' not in p.stdout
print('M121_SYNTHETIC_TESTS=PASS (5 cases)')

