import contextlib
import hashlib
import io
from pathlib import Path
import tempfile
from unittest.mock import patch
import zipfile
import sys
sys.path.insert(0,str(Path(__file__).parent))
import M122_AssetPack_Delivery_Audit_ReadOnly as m

DIST='http://schemas.android.com/apk/distribution'
for kind in ('install-time','fast-follow','on-demand'):
    xml=f'<manifest xmlns:dist="{DIST}"><dist:module><dist:delivery><dist:{kind}/></dist:delivery></dist:module></manifest>'
    assert m.parse_delivery(xml)==kind.upper().replace('-','_')
assert m.parse_delivery('<manifest/>')=='NOT_DECLARED'
with tempfile.TemporaryDirectory() as t:
    t=Path(t)
    project=t/'p.uproject';project.write_text('{"DisableEnginePluginsByDefault":true}')
    config=t/'x.ini';config.write_text('[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]\nbPackageDataInsideApk=True\n')
    assert m.project_flags(project)==('YES','NOT_EXPLICIT')
    assert m.android_bool_setting(config,'bPackageDataInsideApk')=='TRUE'
    aab=t/'a.aab';jar=t/'b.jar';jar.write_bytes(b'mock official jar')
    with zipfile.ZipFile(aab,'w') as z:
        z.writestr('base/manifest/AndroidManifest.xml','base')
        z.writestr('obbassets/manifest/AndroidManifest.xml','asset')
        z.writestr('obbassets/assets/main.obb.png','mock-obb')
    xml=f'<manifest xmlns:dist="{DIST}"><dist:module><dist:delivery><dist:install-time/></dist:delivery></dist:module></manifest>'
    import subprocess
    out=subprocess.CompletedProcess(args=[],returncode=0,stdout=xml,stderr='')
    with patch.object(m,'BUNDLETOOL_SHA256',hashlib.sha256(jar.read_bytes()).hexdigest()),patch.object(m.subprocess,'run',return_value=out):
        s=io.StringIO()
        with contextlib.redirect_stdout(s):
            assert m.run(aab=aab,jar=jar,ini=config,uproject=project)==0
        v=s.getvalue()
        assert 'M122_ASSET_PACK_DELIVERY=INSTALL_TIME' in v
        assert 'M122_GOOGLEPAD_PLUGIN=REVIEW_EFFECTIVE_ENGINE_SETTINGS' in v
        assert 'M122_ASSET_PACK_ANDROID_CONFIG=REVIEW_CONSISTENCY' in v
print('M122_SYNTHETIC_TESTS=PASS (7 checks; no actual game inspected)')
