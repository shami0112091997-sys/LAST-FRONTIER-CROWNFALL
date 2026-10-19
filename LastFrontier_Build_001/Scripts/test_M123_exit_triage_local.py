#!/usr/bin/env python3
"""Synthetic-only checks; never reads phone data and does not trigger GitHub Actions."""
import importlib.util
from pathlib import Path
mod=Path(__file__).parent/"M123_Private_Android_Exit_Triage_ReadOnly.py"
spec=importlib.util.spec_from_file_location("m123",mod)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

none="10-19 06:25:00.000 333 444 E AndroidRuntime: FATAL EXCEPTION: main\n"
scope,counts,selected=m.triage(none)
assert scope=="NO_PACKAGE_EVIDENCE" and not any(counts.values()) and selected==0

java=(
"10-19 06:24:21.000 101 101 I ActivityManager: Start proc 505:com.crownfall.stronghold/u0a111\n"
"10-19 06:24:21.100 505 777 E AndroidRuntime: FATAL EXCEPTION: main\n"
"10-19 06:24:21.101 505 777 E AndroidRuntime: java.lang.UnsatisfiedLinkError: dlopen failed\n"
"10-19 06:24:21.200 666 777 E Vulkan: VK_ERROR from unrelated process\n")
scope,counts,selected=m.triage(java)
assert scope=="PACKAGE_PID_FOUND"
assert counts["JAVA_EXCEPTION"]>0 and counts["DYNAMIC_LINKER"]>0
assert counts["GRAPHICS"]==0

native=(
"Process: com.crownfall.stronghold, PID: 9199\n"
"10-19 06:24:22.125 9199 9199 F libc: Fatal signal 11 (SIGSEGV), code 1\n"
)
scope,counts,_=m.triage(native)
assert scope=="PACKAGE_PID_FOUND" and counts["NATIVE_SIGNAL"]>0

jni=(
"Process: com.crownfall.stronghold, PID: 9199\n"
"10-19 06:24:23.000 9199 9199 E Unreal: Assertion failed: Method != 0\n"
"10-19 06:24:23.020 9199 9199 E Unreal: Failed to find Method\n")
assert m.triage(jni)[1]["JNI_METHOD"]==2

pad=(
"Process: com.crownfall.stronghold, PID: 2001\n"
"10-19 06:24:23.000 2001 2001 E Unreal: GooglePAD asset pack obbassets not found\n")
assert m.triage(pad)[1]["ASSET_PACK"]>0

print("M123_SYNTHETIC_CASES=PASS (5; does not diagnose actual game)")
