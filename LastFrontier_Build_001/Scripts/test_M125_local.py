#!/usr/bin/env python3
"""Synthetic fixtures only: checks reporting; never reads the actual CROWNFALL AAB."""
from pathlib import Path
import tempfile
import zipfile
import io
import M125_CROWNFALL_218_ReadOnly_Diagnostic as a
from contextlib import redirect_stdout
from unittest.mock import patch

xml='<manifest xmlns:dist="http://schemas.android.com/apk/distribution"><dist:module><dist:delivery><dist:install-time/></dist:delivery></dist:module></manifest>'
assert a.delivery(xml)=='INSTALL_TIME'
assert a.delivery(xml.replace('install-time','fast-follow'))=='FAST_FOLLOW'
assert a.delivery('<manifest/>')=='NOT_DECLARED'
needle=a.MARKERS['PAD_JNI_METHOD'];split=1048576-10
assert a.find_markers(io.BytesIO(b'x'*split+needle),a.MARKERS)['PAD_JNI_METHOD']
with tempfile.TemporaryDirectory() as tmp:
    t=Path(tmp);p=t/'a.aab';proj=t/'project.uproject';ini=t/'engine.ini'
    proj.write_text('{"DisableEnginePluginsByDefault": true}')
    ini.write_text('[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]\nbPackageDataInsideApk=True\n')
    assert a.proj_flags(proj)==('YES','NOT_EXPLICIT')
    assert a.ini_bool(ini,'bPackageDataInsideApk')=='TRUE'
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('base/manifest/AndroidManifest.xml','x')
        z.writestr('obbassets/manifest/AndroidManifest.xml','x')
        z.writestr('base/dex/classes.dex',needle)
        z.writestr('base/lib/arm64-v8a/libUnreal.so',needle)
        z.writestr('obbassets/assets/main.obb.png','fake-obb')
    output=io.StringIO()
    with redirect_stdout(output):
        assert a.check(p,proj,ini,t/'missing.jar')==0
    report=output.getvalue()
    assert 'M125_OBBASSETS_MODULE=YES' in report
    assert 'M125_BUNDLETOOL=UNAVAILABLE' in report
    assert 'M125_CRASH_CAUSE=UNKNOWN_NEEDS_ACTUAL_ANDROID_STACK_TRACE' in report
    assert 'M125_PACKAGING_HYPOTHESIS=REVIEW_CONFIG_CONSISTENCY' in report
    assert 'M125_DEX_PAD_JNI_METHOD=SEEN' in report
    with redirect_stdout(io.StringIO()): assert a.check(t/'missing.aab',proj,ini,t/'no.jar')==2
print('M125_SYNTHETIC_TESTS=PASS (13 checks; no real bundle inspected)')

