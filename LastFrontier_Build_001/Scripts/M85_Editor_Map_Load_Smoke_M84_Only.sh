#!/usr/bin/env bash
# M85: bounded Editor+TestMap smoke on M84 sandbox; no Cook/package/upload.
set -u
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
W="$HOME/crownfall/M84_EDITOR_SANDBOX_v218"
E="$HOME/UE_5.8.3"
L="$HOME/crownfall/M85_EDITOR_LOAD.log"
S="$HOME/crownfall/M85_EDITOR_PROBE.py"
if [ -e "$L" ] || [ -e "$S" ]; then echo 'M85_BLOCKED=EXISTING_RESULTS'; exit 2; fi
for F in "$P/Content/Maps/TestMap.umap" "$W/LastFrontier.uproject" "$W/Content/Maps/TestMap.umap" "$W/Binaries/Linux/UnrealEditor.modules" "$W/Binaries/Linux/libUnrealEditor-LastFrontier.so" "$W/Binaries/Linux/libUnrealEditor-LastFrontierEditor.so"; do
  if [ ! -s "$F" ]; then echo 'M85_BLOCKED=MISSING_FILES'; exit 2; fi
done
if [ ! -x "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" ] || ! cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap"; then echo 'M85_BLOCKED=ENGINE_OR_MAP'; exit 2; fi
cat > "$S" <<'PY'
import unreal
package = unreal.load_package('/Game/Maps/TestMap')
if package is None:
    raise RuntimeError('M85_MAP_PACKAGE_MISSING')
world = unreal.find_object(package, 'TestMap', unreal.World)
if world is None:
    raise RuntimeError('M85_WORLD_MISSING')
unreal.log('M85_WORLD_LOAD=PASS')
PY
if ! python3 -m py_compile "$S"; then echo 'M85_BLOCKED=PYTHON_SYNTAX'; exit 2; fi
echo 'M85_PREFLIGHT=PASS'
timeout --kill-after=10s 900 "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" "$W/LastFrontier.uproject" -run=pythonscript -script="$S" -nullrhi -unattended -nosound -stdout -FullStdOutLogOutput -UTF8Output >"$L" 2>&1
R=$?
echo "M85_EXIT=$R"
if [ "$R" -eq 0 ] && grep -Fq 'M85_WORLD_LOAD=PASS' "$L" && ! grep -Eiq 'LogPython: Error|Serialization error|Fatal error|Assertion failed' "$L"; then
  echo 'M85_EDITOR_LOAD=PASS'
else
  echo 'M85_EDITOR_LOAD=FAIL'
fi
if cmp -s "$P/Content/Maps/TestMap.umap" "$W/Content/Maps/TestMap.umap"; then echo 'M85_MAP_INTEGRITY=PASS'; else echo 'M85_MAP_INTEGRITY=FAIL'; fi
grep -Ei 'M85_|Error:|Fatal error|ModuleManager|Failed to load|Result:|Success - ' "$L" | tail -n 20 || true
echo "M85_LOG=$L"
