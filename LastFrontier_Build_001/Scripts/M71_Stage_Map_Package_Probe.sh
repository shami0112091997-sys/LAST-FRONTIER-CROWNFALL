#!/usr/bin/env bash
# M71: Read-only map package/world load probe using a standalone Python file.
# Run from existing VM; do not modify live project or invoke SaveMap/Cook.
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z"
E="$HOME/UE_5.8.3"
A="$P/Content/Maps/TestMap.umap"
B="$D/Content/Maps/TestMap.umap"
T="$HOME/crownfall/M71_world_probe.py"
L="$HOME/crownfall/M71_world_probe.log"
if [ ! -s "$A" ] || [ ! -s "$B" ] || [ ! -s "$D/LastFrontier.uproject" ] || [ ! -x "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" ] || ! cmp -s "$A" "$B"; then
  echo M71_PREFLIGHT=BLOCKED
else
  HA=$(sha256sum "$A" | cut -d' ' -f1)
  HB=$(sha256sum "$B" | cut -d' ' -f1)
  printf '%s\n' 'import unreal' 'p = unreal.load_package("/Game/Maps/TestMap")' 'assert p is not None, "PACKAGE_MISSING"' 'w = unreal.find_object(p, "TestMap", unreal.World)' 'assert w is not None, "WORLD_MISSING"' 'print("M71_WORLD_OK")' > "$T"
  if python3 -m py_compile "$T"; then
    echo M71_PYTHON_SYNTAX=PASS
    timeout 600 "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" "$D/LastFrontier.uproject" -run=pythonscript "-script=$T" -nullrhi -unattended -nosound -stdout -FullStdOutLogOutput > "$L" 2>&1
    R=$?
    echo "M71_UNREAL_EXIT=$R"
    if [ "$HA" = "$(sha256sum "$A" | cut -d' ' -f1)" ] && [ "$HB" = "$(sha256sum "$B" | cut -d' ' -f1)" ]; then
      echo M71_MAP_INTEGRITY=PASS
      I=1
    else
      echo M71_MAP_INTEGRITY=FAIL
      I=0
    fi
    if [ "$R" -eq 0 ] && [ "$I" -eq 1 ] && grep -Fq M71_WORLD_OK "$L" && ! grep -Eiq 'Serialization error|LogLinker: Error|Fatal error|Assertion failed|Traceback|LogPython: Error' "$L"; then
      echo M71_WORLD_TEST=PASS
    else
      echo M71_WORLD_TEST=FAIL
      grep -Ei 'Error|Traceback|Failed' "$L" | tail -n 12 || true
    fi
  else
    echo M71_PYTHON_SYNTAX=FAIL
  fi
fi
echo "LOG=$L"