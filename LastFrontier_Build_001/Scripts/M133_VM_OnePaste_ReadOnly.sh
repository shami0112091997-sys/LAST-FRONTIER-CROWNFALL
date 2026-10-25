python3 - <<'PY'
from pathlib import Path
from hashlib import sha1
from zipfile import ZipFile, BadZipFile
root = Path.home() / "crownfall"
maps = {
    "M63": root / "M63_REAL_MOBILE/LastFrontier_Build_001/Content/Maps/TestMap.umap",
    "M84": root / "M84_EDITOR_SANDBOX_v218/Content/Maps/TestMap.umap",
    "M106": root / "M106_RELEASE_SANDBOX_v218/Content/Maps/TestMap.umap",
}
bad = "965b78fc071c21412f966b70712eb30724799c20"
ids = {}
for name, path in maps.items():
    if path.is_symlink() or not path.is_file():
        print(f"MAP_{name}=NOT_FOUND_OR_UNSAFE")
        continue
    try:
        size = path.stat().st_size
        h = sha1(b"blob " + str(size).encode() + b"\0")
        with path.open("rb") as f:
            magic = f.read(4)
            h.update(magic)
            for part in iter(lambda: f.read(1024 * 1024), b""):
                h.update(part)
        ids[name] = h.hexdigest()
        print(f"MAP_{name}_BYTES={size}")
        print(f"MAP_{name}_HEADER={'YES' if magic == bytes.fromhex('c1832a9e') else 'NO'}")
        print(f"MAP_{name}_MATCHES_FAILED_GITHUB_MAP={'YES' if ids[name] == bad else 'NO'}")
    except OSError:
        print(f"MAP_{name}=READ_ERROR")
for a, b in (("M63", "M84"), ("M63", "M106"), ("M84", "M106")):
    if a not in ids or b not in ids:
        result = "UNKNOWN"
    else:
        result = "EQUAL" if ids[a] == ids[b] else "DIFFERENT"
    print(f"MAP_{a}_VS_{b}={result}")
aab = root / "M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab"
if aab.is_symlink() or not aab.is_file():
    print("AAB_218=NOT_FOUND_OR_UNSAFE")
else:
    try:
        print(f"AAB_218_BYTES={aab.stat().st_size}")
        print(f"AAB_218_SIZE_EQUALS_M118={'YES' if aab.stat().st_size == 117411826 else 'NO'}")
        with ZipFile(aab) as z:
            names = z.namelist()
            obb = [x for x in names if x.startswith("obbassets/assets/") and x.lower().endswith((".obb", ".obb.png"))]
            print(f"AAB_218_OBBASSETS_MANIFEST={'YES' if 'obbassets/manifest/AndroidManifest.xml' in names else 'NO'}")
            print(f"AAB_218_OBB_FILES={len(obb)}")
            print(f"AAB_218_ARM64_LIBS={sum(x.startswith('base/lib/arm64-v8a/') and x.endswith('.so') for x in names)}")
            print(f"AAB_218_DEX={sum(x.startswith('base/dex/') and x.endswith('.dex') for x in names)}")
    except (BadZipFile, OSError, ValueError):
        print("AAB_218=READ_OR_ZIP_ERROR")
print("CHECK=READ_ONLY; CRASH_CAUSE=UNKNOWN")
PY
