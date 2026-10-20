#!/usr/bin/env python3
"""M126 synthetic DEX structure tests; no user AAB, app data or device logs."""
from pathlib import Path
import contextlib,io,struct,sys,tempfile,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
import M126_GooglePAD_Dex_Method_Audit_ReadOnly as m

METHOD='AndroidThunkJava_GooglePAD_Available'
CLASS='Lcom/epicgames/unreal/GameActivity;'

def leb(n):
    out=bytearray()
    while True:
        v=n&127;n>>=7
        out.append(v|128 if n else v)
        if not n:return bytes(out)

def dex(*,has_method_id=True,has_class_data=True,defined_name=METHOD):
    b=bytearray(0x200)
    b[:8]=b'dex\n035\0'
    struct.pack_into('<II',b,0x20,len(b),0x70)
    # String data contains a class descriptor + one or two method names.
    words=[CLASS,defined_name]
    if METHOD not in words:words.append(METHOD)
    string_at=0x70;type_at=0x80;proto_at=0x84;method_at=0x90;class_at=0x98
    struct.pack_into('<II',b,0x38,len(words),string_at)
    struct.pack_into('<II',b,0x40,1,type_at)
    struct.pack_into('<II',b,0x48,1,proto_at)
    struct.pack_into('<II',b,0x58,1 if has_method_id else 0,method_at)
    struct.pack_into('<II',b,0x60,1,class_at)
    struct.pack_into('<I',b,type_at,0)
    if has_method_id: struct.pack_into('<HHI',b,method_at,0,0,1)
    struct.pack_into('<I',b,class_at,0)
    struct.pack_into('<I',b,class_at+24,0xC0 if has_class_data else 0)
    pos=0xD0
    for i,text in enumerate(words):
        raw=text.encode('ascii')
        struct.pack_into('<I',b,string_at+4*i,pos)
        val=leb(len(text))+raw+b'\0';b[pos:pos+len(val)]=val;pos+=len(val)
    if has_class_data:
        b[0xC0:0xC0+8]=b'\0\0\1\0\0\x01\x80\x02'
    return bytes(b)

def bundle(path,dex_bytes,so_bytes):
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('base/dex/classes.dex',dex_bytes)
        z.writestr('base/lib/arm64-v8a/libUnreal.so',so_bytes)

checks=0
assert m.uleb(b'\x80\x02',0)==(256,2);checks+=1
assert m.native_methods(METHOD.encode()+b'\0')=={METHOD};checks+=1
ids,defs,act=m.dex_method_entries(dex(),{METHOD})
assert ids==defs==act=={METHOD};checks+=1
ids,defs,act=m.dex_method_entries(dex(has_class_data=False),{METHOD})
assert ids=={METHOD} and not defs and not act;checks+=1
ids,defs,act=m.dex_method_entries(dex(has_method_id=False),{METHOD})
assert not ids and not defs and not act;checks+=1
ids,defs,act=m.dex_method_entries(dex(defined_name='AndroidThunkJava_GooglePAD_Unrelated'),{METHOD})
assert not ids and not defs and not act;checks+=1
try:
    m.dex_method_entries(b'FAKE DEX',{METHOD})
    raise AssertionError('bad dex accepted')
except m.DexProblem:checks+=1
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'game.aab'
    bundle(p,dex(),METHOD.encode()+b'\0')
    status,out=m.audit(p)
    assert status==0 and out['M126_DEX_MATCHED_CLASS_METHOD_DEFINITIONS']==1 and out['M126_DEX_GAME_ACTIVITY_METHOD_DEFINITIONS']==1;checks+=1
    bundle(p,dex(has_class_data=False),METHOD.encode()+b'\0')
    status,out=m.audit(p)
    assert status==3 and out['M126_ASSESSMENT']=='REVIEW_POTENTIAL_JNI_METHOD_MISMATCH';checks+=1
    bundle(p,dex(has_method_id=False),METHOD.encode()+b'\0')
    status,out=m.audit(p)
    assert status==3 and out['M126_ONLY_NATIVE_NO_DEX_METHOD_ID']==1;checks+=1
    bundle(p,dex(),b'no native method named here')
    status,out=m.audit(p)
    assert status==0 and out['M126_ASSESSMENT']=='NO_NATIVE_GOOGLEPAD_JNI_NAMES_FOUND';checks+=1
    bundle(p,b'not real dex',METHOD.encode())
    status,out=m.audit(p)
    assert status==2 and out['M126_INPUT']=='DEX_PARSE_FAILED';checks+=1
print(f'M126_SYNTHETIC_CHECKS=PASS ({checks} cases; NOT game AAB)')
