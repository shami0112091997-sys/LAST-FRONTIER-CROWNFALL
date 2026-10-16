#!/usr/bin/env bash
# M91: QA AAB audit; no publishing, repackaging, keystore, or upload.
set -u
A="$HOME/crownfall/M84_EDITOR_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab"
L="$HOME/crownfall/M91_QA_AAB_SIGNATURE.log"
if [ ! -s "$A" ]; then echo 'M91_AAB=MISSING'; exit 2; fi
echo '=== M91 QA AAB FILE ==='
echo "M91_BYTES=$(stat -c %s "$A")"
sha256sum "$A" | sed 's/^/M91_AAB_SHA256=/' 
echo '=== M91 ZIP / MODULE / CONTENT ==='
python3 - "$A" <<'PY'
import zipfile,sys
p=sys.argv[1]
if not zipfile.is_zipfile(p):
 print('M91_ZIP=FAIL');sys.exit(2)
with zipfile.ZipFile(p) as z:
 bad=z.testzip()
 if bad:
  print('M91_ZIP=FAIL_ENTRY:'+bad);sys.exit(2)
 print('M91_ZIP=PASS')
 n=z.namelist()
 for path,label in [('BundleConfig.pb','BUNDLE_CONFIG'),('base/manifest/AndroidManifest.xml','BASE_MANIFEST')]:
  print('M91_'+label+'='+('PRESENT' if path in n else 'MISSING'))
 print('M91_ARM64_LIBS='+str(sum(i.startswith('base/lib/arm64-v8a/') and i.endswith('.so') for i in n)))
 print('M91_DEX='+str(sum(i.startswith('base/dex/') and i.endswith('.dex') for i in n)))
 candidates=[x for x in z.infolist() if not x.is_dir() and (x.filename.startswith('base/assets/') or '/assets/' in x.filename or x.filename.lower().endswith(('.pak','.ucas','.utoc','.obb','.obb.png')))]
 print('M91_ASSET_PAYLOAD_FILES='+str(len(candidates)))
 for x in sorted(candidates,key=lambda q:q.file_size,reverse=True)[:24]:
  print('M91_PAYLOAD='+x.filename+' | '+str(x.file_size)+' bytes')
 print('M91_ZIP_ENTRIES='+str(len(n)))
PY
R=$?
if [ "$R" -ne 0 ]; then echo "M91_CONTENT_AUDIT_EXIT=$R"; exit "$R"; fi
echo '=== M91 PUBLIC CERTIFICATE ==='
keytool -printcert -jarfile "$A" 2>&1 | grep -Ei '^Owner:|^Issuer:|SHA256:' | head -n 6 || true
echo '=== M91 SIGNATURE CHECK ==='
if [ -e "$L" ]; then
 echo 'M91_SIGNATURE_LOG_ALREADY_EXISTS=YES'
else
 jarsigner -verify -strict "$A" > "$L" 2>&1
 R=$?
 echo "M91_JARSIGNER_STRICT_EXIT=$R"
 grep -Ei 'jar verified|jar is unsigned|self-signed|error:|warning:|chain not validated' "$L" | tail -n 10 || true
fi
echo "M91_SIGNATURE_LOG=$L"
echo "M91_QA_ONLY=TRUE"
