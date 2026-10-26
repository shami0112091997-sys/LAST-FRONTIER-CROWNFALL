#!/usr/bin/env python3
"""M135: read-only hard safety gate for the historically failed Unreal map.

This is NOT a UE map-load test. It blocks the exact TestMap Git blob that
failed a real UE 5.8 cook (GitHub Actions 37645589203). Another blob may also
be invalid, so a PASS means ONLY that the known failed bytes were not seen.
Does not read secrets, execute Unreal, edit maps or launch any build.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import stat
import sys

KNOWN_FAILED_UE_COOK_MAP_OID = "965b78fc071c21412f966b70712eb30724799c20"
UNREAL_PACKAGE_MAGIC = bytes.fromhex("c1832a9e")
MAX_MAP_SIZE = 256 * 1024 * 1024


def inspect_map(path: Path) -> tuple[str, int]:
    try:
        meta = path.lstat()
        if not stat.S_ISREG(meta.st_mode) or not 32 <= meta.st_size <= MAX_MAP_SIZE:
            return "BLOCKED_MISSING_OR_UNSAFE_MAP", 2
        digest = hashlib.sha1(b"blob " + str(meta.st_size).encode("ascii") + b"\0")
        with path.open("rb") as source:
            signature = source.read(4)
            digest.update(signature)
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        if signature != UNREAL_PACKAGE_MAGIC:
            return "BLOCKED_BAD_UNREAL_PACKAGE_HEADER", 2
        if digest.hexdigest() == KNOWN_FAILED_UE_COOK_MAP_OID:
            return "BLOCKED_HISTORIC_UE_COOK_FAILURE", 2
        return "NOT_KNOWN_BAD_STILL_REQUIRES_UE_LOAD_AND_COOK", 0
    except FileNotFoundError:
        return "BLOCKED_MISSING_OR_UNSAFE_MAP", 2
    except OSError:
        return "BLOCKED_MAP_READ_FAILED", 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    args = parser.parse_args(argv)
    status, code = inspect_map(args.map)
    print(f"M135_MAP_STATUS={status}")
    print("M135_UE_LOAD_OR_COOK=NOT_RUN")
    print("M135_ANDROID_LAUNCH=NOT_TESTED")
    print("M135_RELEASE_APPROVAL=NOT_GRANTED")
    return code


if __name__ == "__main__":
    sys.exit(main())
