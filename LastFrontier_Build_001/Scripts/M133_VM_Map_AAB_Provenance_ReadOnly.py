#!/usr/bin/env python3
"""M133 — read-only M63/M84/M106 map provenance + original AAB inventory.

No writes, no network, no device access, no signing-key/config reads, no Build,
Cook, GitHub Actions trigger, or Google Play upload. Does not extract AAB files.
Prints only bounded statuses/counts, not private paths or raw asset bytes.
A structural result can NEVER diagnose or prove a launch-time crash.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import stat
import sys
import zipfile

PROJECT_NAME = "LastFrontier_Build_001"
MAP_PATH = "Content/Maps/TestMap.umap"
AAB_PATH = "Binaries/Android/LastFrontier-Android-Shipping.aab"
UNREAL_PACKAGE_TAG = bytes.fromhex("c1832a9e")
HISTORIC_BAD_GITHUB_MAP_GIT_OID = "965b78fc071c21412f966b70712eb30724799c20"
M118_RECORDED_218_AAB_BYTES = 117_411_826
MAX_MAP_BYTES = 1024 * 1024 * 1024
MAX_AAB_BYTES = 2 * 1024 * 1024 * 1024
MAX_ZIP_MEMBERS = 50_000


@dataclass(frozen=True)
class MapFact:
    status: str
    git_oid: str = ""
    size: int = 0
    header_ok: bool = False


def safe_regular(path: Path, max_size: int) -> bool:
    """Reject symlinks and special files without opening them."""
    try:
        meta = path.lstat()
        return stat.S_ISREG(meta.st_mode) and 0 < meta.st_size <= max_size
    except (OSError, ValueError):
        return False


def read_map(path: Path) -> MapFact:
    if not safe_regular(path, MAX_MAP_BYTES):
        return MapFact("MISSING_OR_UNSAFE")
    try:
        size = path.stat().st_size
        oid = hashlib.sha1(b"blob " + str(size).encode("ascii") + b"\0")
        with path.open("rb") as stream:
            header = stream.read(4)
            oid.update(header)
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                oid.update(chunk)
        return MapFact("PRESENT", oid.hexdigest(), size, header == UNREAL_PACKAGE_TAG)
    except (OSError, ValueError):
        return MapFact("READ_FAILED")


def inspect_maps(paths: dict[str, Path]) -> tuple[dict[str, str], bool]:
    out: dict[str, str] = {}
    facts = {name: read_map(path) for name, path in paths.items()}
    valid = True
    for name, fact in facts.items():
        out[f"{name}_MAP"] = fact.status
        if fact.status != "PRESENT":
            valid = False
            out[f"{name}_MAP_HEADER"] = "UNAVAILABLE"
            out[f"{name}_HISTORIC_BAD_GITHUB_BLOB"] = "UNAVAILABLE"
            continue
        out[f"{name}_MAP_SIZE_BYTES"] = str(fact.size)
        out[f"{name}_MAP_HEADER"] = "UNREAL_MAGIC_ONLY" if fact.header_ok else "INVALID"
        out[f"{name}_HISTORIC_BAD_GITHUB_BLOB"] = (
            "YES" if fact.git_oid == HISTORIC_BAD_GITHUB_MAP_GIT_OID else "NO"
        )
        if not fact.header_ok:
            valid = False

    pairs = (("M63", "M84"), ("M63", "M106"), ("M84", "M106"))
    for a, b in pairs:
        x, y = facts[a], facts[b]
        key = f"{a}_VS_{b}_MAP"
        out[key] = ("EQUAL" if x.git_oid == y.git_oid else "DIFFERENT") if (
            x.status == "PRESENT" and y.status == "PRESENT"
        ) else "UNAVAILABLE"
    out["GITHUB_BAD_BLOB_MATCHED_BY_VM"] = (
        "YES" if any(f.status == "PRESENT" and
                     f.git_oid == HISTORIC_BAD_GITHUB_MAP_GIT_OID
                     for f in facts.values()) else "NO_OR_UNAVAILABLE"
    )
    out["MAP_PROVENANCE_STATUS"] = "COMPLETE_STRUCTURAL_ONLY" if valid else "INCOMPLETE"
    return out, valid


def inspect_aab(path: Path) -> tuple[dict[str, str], bool]:
    info: dict[str, str] = {}
    if not safe_regular(path, MAX_AAB_BYTES):
        return {"AAB_FILE": "MISSING_OR_UNSAFE"}, False
    try:
        meta = path.stat()
        info["AAB_SIZE_BYTES"] = str(meta.st_size)
        info["AAB_SIZE_MATCH_M118_RECORD"] = (
            "YES" if meta.st_size == M118_RECORDED_218_AAB_BYTES else "NO_REVIEW_PROVENANCE"
        )
        with zipfile.ZipFile(path, mode="r") as bundle:
            entries = bundle.infolist()  # read only central directory: do NOT decompress assets
            if len(entries) > MAX_ZIP_MEMBERS:
                return {"AAB_FILE": "EXCESSIVE_ZIP_MEMBERS"}, False
            names = [item.filename for item in entries if not item.is_dir()]
            unique = set(names)
            info["AAB_ENTRY_COUNT"] = str(len(names))
            info["AAB_DUPLICATE_ENTRY_NAMES"] = "YES" if len(unique) != len(names) else "NO"
            modules = {n.split("/")[0] for n in unique if n.endswith("/manifest/AndroidManifest.xml")}
            info["AAB_BASE_MODULE"] = "YES" if "base" in modules else "NO"
            info["AAB_BUNDLE_CONFIG"] = "YES" if "BundleConfig.pb" in unique else "NO"
            info["AAB_OBBASSETS_MODULE"] = "YES" if "obbassets" in modules else "NO"
            info["AAB_DEX_COUNT"] = str(sum(n.startswith("base/dex/") and n.endswith(".dex") for n in names))
            info["AAB_ARM64_SO_COUNT"] = str(sum(n.startswith("base/lib/arm64-v8a/") and n.endswith(".so") for n in names))
            obb = [e for e in entries if
                   e.filename.startswith("obbassets/assets/") and
                   e.filename.lower().endswith((".obb", ".obb.png"))]
            info["AAB_INSTALL_PACK_OBB_COUNT"] = str(len(obb))
            info["AAB_INSTALL_PACK_OBB_BYTES"] = str(sum(e.file_size for e in obb))
            visible_ue = [n for n in names if n.lower().endswith((".pak", ".ucas", ".utoc"))]
            info["AAB_VISIBLE_UE_ARCHIVE_COUNT"] = str(len(visible_ue))
            info["AAB_ARCHIVE_INSIDE_OBB"] = "NOT_INSPECTED"
            info["AAB_DELIVERY_MODE"] = "NOT_DERIVED_NEEDS_BUNDLETOOL_OR_PLAY"
            info["AAB_VERSION_CODE"] = "NOT_DERIVED_NEEDS_BUNDLETOOL"
            structurally_ok = (
                len(unique) == len(names)
                and "base" in modules
                and "BundleConfig.pb" in unique
                and "base/manifest/AndroidManifest.xml" in unique
                and int(info["AAB_DEX_COUNT"]) > 0
                and int(info["AAB_ARM64_SO_COUNT"]) > 0
                and ("obbassets" not in modules or len(obb) > 0)
            )
            info["AAB_STRUCTURE"] = "PASS_METADATA_ONLY" if structurally_ok else "REVIEW"
            info["AAB_FILE"] = "READABLE_ZIP"
            return info, structurally_ok
    except (OSError, zipfile.BadZipFile, RuntimeError, ValueError):
        return {"AAB_FILE": "BAD_ZIP_OR_READ_FAILED"}, False


def inspect_jni(aab: Path) -> dict[str, str]:
    """Optional deeper M126 parser; not proof of runtime JNI calling correctness."""
    try:
        from M126_GooglePAD_Dex_Method_Audit_ReadOnly import audit
        rc, result = audit(aab)
        keep = (
            "M126_ASSESSMENT",
            "M126_NATIVE_PAD_METHOD_REFERENCES",
            "M126_DEX_MATCHED_CLASS_METHOD_DEFINITIONS",
            "M126_MISSING_CLASS_METHOD_DEFINITIONS",
            "M126_NATIVE_METHODS_NOT_DEFINED_ON_ACTIVITY",
            "M126_DEX_AVAILABLE_NOARGS_BOOL_DEFINITION",
        )
        out = {k.replace("M126_", "JNI_"): str(result[k]) for k in keep if k in result}
        out["JNI_INSPECTION_RESULT"] = "STATIC_ONLY" if rc == 0 else "REVIEW_OR_FAILED"
        return out
    except (ImportError, OSError, RuntimeError, ValueError, MemoryError):
        return {"JNI_INSPECTION_RESULT": "UNAVAILABLE"}


def main(argv: list[str] | None = None) -> int:
    home = Path.home()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m63-map", type=Path,
                        default=home / "crownfall/M63_REAL_MOBILE/LastFrontier_Build_001" / MAP_PATH)
    parser.add_argument("--m84-map", type=Path,
                        default=home / "crownfall/M84_EDITOR_SANDBOX_v218" / MAP_PATH)
    parser.add_argument("--m106-map", type=Path,
                        default=home / "crownfall/M106_RELEASE_SANDBOX_v218" / MAP_PATH)
    parser.add_argument("--aab", type=Path,
                        default=home / "crownfall/M106_RELEASE_SANDBOX_v218" / AAB_PATH)
    parser.add_argument("--scan-jni", action="store_true",
                        help="Use existing M126 bounded DEX/native static parser (read-only).")
    args = parser.parse_args(argv)
    maps, map_ok = inspect_maps({"M63": args.m63_map, "M84": args.m84_map,
                                  "M106": args.m106_map})
    aab, aab_ok = inspect_aab(args.aab)
    print("M133_MODE=READ_ONLY_NO_SECRET_DATA")
    for key, value in sorted({**maps, **aab}.items()):
        print(f"M133_{key}={value}")
    if args.scan_jni:
        if aab_ok:
            for key, value in sorted(inspect_jni(args.aab).items()):
                print(f"M133_{key}={value}")
        else:
            print("M133_JNI_INSPECTION_RESULT=SKIPPED_AAB_NOT_VALIDATED")
    else:
        print("M133_JNI_INSPECTION_RESULT=NOT_REQUESTED")
    print("M133_AAB_CRC_OR_CONTENT=NOT_VERIFIED")
    print("M133_218_ACTUAL_LAUNCH=NOT_TESTED")
    print("M133_218_CRASH_CAUSE=UNCONFIRMED")
    print("M133_BUILD_COOK_PACKAGE_SIGN_UPLOAD=NOT_PERFORMED")
    print("M133_RESULT=STRUCTURAL_AUDIT_COMPLETE" if map_ok and aab_ok
          else "M133_RESULT=INCOMPLETE_MISSING_OR_UNVERIFIED_INPUTS")
    return 0 if map_ok and aab_ok else 2


if __name__ == "__main__":
    sys.exit(main())
