#!/usr/bin/env python3
"""Synthetic tests only. Does not use real phone logs, assets, JKS, or AAB."""
import io, sys, zipfile, tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import M124_AAB_JNI_Crosscheck_ReadOnly as m

pattern=m.PATTERNS['GOOGLEPAD_AVAILABILITY_METHOD']
def make_aab(path,dex=b'',native=b''):
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('base/dex/classes.dex',dex)
        z.writestr('base/lib/arm64-v8a/libUnreal.so',native)
with tempfile.TemporaryDirectory() as t:
    t=Path(t)
    f=t/'f.aab'
    make_aab(f,dex=b'x'*100+pattern, native=b'y'*100+pattern)
    rc,out=m.check(f)
    assert rc==0 and out['M124_ASSESSMENT']=='STATIC_STRING_MATCH_ONLY_NOT_PROOF_OF_RUNTIME'
    make_aab(f,dex=b'dex-not-method',native=pattern)
    rc,out=m.check(f)
    assert rc==0 and out['M124_ASSESSMENT']=='REVIEW_NATIVE_JNI_STRING_WITHOUT_DEX_MATCH'
    make_aab(f,dex=pattern,native=b'native-not-method')
    rc,out=m.check(f)
    assert rc==0 and out['M124_ASSESSMENT']=='REVIEW_DEX_JNI_STRING_WITHOUT_NATIVE_MATCH'
    make_aab(f,dex=b'no',native=b'no')
    rc,out=m.check(f)
    assert rc==0 and out['M124_ASSESSMENT']=='NO_AVAILABILITY_METHOD_STRING_FOUND_IN_SCANNED_FILES'
    assert out['M124_CRASH_CAUSE']=='UNPROVEN_NEEDS_DEVICE_LOG'
    with zipfile.ZipFile(f,'w') as z:
        z.writestr('base/dex/classes.dex',b'only-dex')
    assert m.check(f)[0]==3
    f.write_text('bad zip')
    assert m.check(f)[0]==2
    assert m.check(t/'missing.aab')[0]==2
    # Check split pattern crossing chunk boundary.
    start=1024*1024-len(pattern)//2
    assert m.scan_stream(io.BytesIO(b'x'*start+pattern+b'y'),{'PAD':pattern})['PAD']
print('M124_SYNTHETIC_TESTS=PASS 8/8')

