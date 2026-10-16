#!/usr/bin/env bash
set -euo pipefail

P="${P:-$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001}"
E="${E:-$HOME/UE_5.8.3}"
OUT="${OUT:-$HOME/crownfall/M66_SMART_RESUME}"
STAMP="$(date +%Y%m%d-%H%M%S)"
R="$OUT/$STAMP"
REPORT="$R/M66_SMART_RESUME_REPORT.txt"
ARCHIVE="$R/M63_CRITICAL_RECOVERY.tar.gz"

mkdir -p "$R"

exec > >(tee "$REPORT") 2>&1

echo "========================================"
echo " CROWNFALL M66 SMART RESUME / READ-ONLY"
echo "========================================"
echo "HOST=$(hostname)"
echo "PROJECT=$P"
echo "ENGINE=$E"
echo "REPORT=$REPORT"

test -f "$P/LastFrontier.uproject" || { echo "FATAL: UPROJECT_MISSING"; exit 10; }
test -d "$P/Content" || { echo "FATAL: CONTENT_MISSING"; exit 11; }
test -d "$P/Source" || { echo "FATAL: SOURCE_MISSING"; exit 12; }

echo
echo "===== DISK ====="
df -h "$HOME" || true
du -sh "$P" "$P/Content" "$P/Source" "$P/Config" 2>/dev/null || true

echo
echo "===== CRITICAL MAPS ====="
for f in   "$P/Content/Maps/TestMap.umap"   "$P/Content/Maps/TestMap_M63_Atomic.umap"
do
  if [ -f "$f" ]; then
    stat -c "FILE=%n SIZE=%s MTIME=%y" "$f"
    sha256sum "$f"
  else
    echo "MISSING=$f"
  fi
done

echo
echo "===== EDITOR COMMANDLET ====="
find "$P/Source" -type f -iname '*CrownfallAtomicMapCommandlet*' -print -exec sha256sum {} \; 2>/dev/null || true

echo
echo "===== REAL CONTENT ====="
REAL="$P/Content/Environment/Real"
if [ -d "$REAL" ]; then
  echo "REAL_SIZE=$(du -sh "$REAL" | awk '{print $1}')"
  echo "UASSETS=$(find "$REAL" -type f -name '*.uasset' | wc -l)"
  find "$REAL" -type f -name '*.uasset' -printf '%s %p\n' | sort -nr | head -40
  find "$REAL" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | sed 's/^/REAL_TREE_SHA256=/'
else
  echo "REAL_CONTENT_MISSING"
fi

echo
echo "===== KNOWN M63 LOG GATES ====="
for log in   "$HOME/crownfall/M63_CPP_COMMANDLET_EMPTY_RUN.log"   "$HOME/crownfall/M63_CPP_LOAD_ONLY_RUN.log"   "$HOME/crownfall/M63_ATOMIC_RUN.log"   "$HOME/crownfall/M63_ATOMIC_VERIFY.log"   "$HOME/crownfall/M63_REAL_ASSET_QUALITY_AUDIT.log"   "$HOME/crownfall/M63_TEXTURE_COLLISION_AUDIT.log"   "$HOME/crownfall/M63_BODYSETUP_AUDIT.log"   "$HOME/crownfall/M63_STREETLAMP_LOD.log"
do
  if [ -f "$log" ]; then
    echo
    echo "--- $log ---"
    grep -Ei       'PASS|FAIL|ERROR|WARNING|PROCESS_EXIT|CRASH_MARKERS|SET_LODS_RESULT|ROLLBACK|LOD[0-9_]|TRIANGLES|STATIC_MESH_COUNT|TEXTURE_COUNT|BODYSETUP'       "$log" | tail -120 || true
  fi
done

echo
echo "===== STREETLAMP LOD FAILURE CONTEXT ====="
LODLOG="$HOME/crownfall/M63_STREETLAMP_LOD.log"
if [ -f "$LODLOG" ]; then
  grep -nEi     'set_lods|reduc|mesh reduction|quadric|simplygon|lod|error|warning|failed|cannot|could not|unsupported'     "$LODLOG" | tail -240 || true
else
  echo "LOD_LOG_MISSING"
fi

echo
echo "===== LOCAL UE 5.8.3 SETLODS SOURCE ====="
SRC="$E/Engine/Source/Editor/StaticMeshEditor/Private/StaticMeshEditorSubsystem.cpp"
if [ -f "$SRC" ]; then
  L="$(grep -n -m1 'SetLodsWithNotification' "$SRC" | cut -d: -f1 || true)"
  if [ -n "$L" ]; then
    S=$((L-30)); [ "$S" -lt 1 ] && S=1
    T=$((L+220))
    nl -ba "$SRC" | sed -n "${S},${T}p"
  else
    echo "SETLODS_SOURCE_SYMBOL_NOT_FOUND"
  fi
else
  echo "STATIC_MESH_EDITOR_SOURCE_MISSING"
fi

echo
echo "===== REDUCTION MODULES ====="
find "$E/Engine/Binaries/Linux" "$E/Engine/Plugins"   -type f \( -iname '*MeshReduction*' -o -iname '*Simplygon*' -o -iname '*Quadric*' \)   -printf '%p\n' 2>/dev/null | head -200 || true

echo
echo "===== PROJECT GIT STATE ====="
if git -C "$P" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$P" remote -v || true
  git -C "$P" status --short || true
  git -C "$P" branch --show-current || true
  git -C "$P" log -1 --oneline || true
else
  echo "PROJECT_NOT_A_GIT_WORKTREE"
fi

echo
echo "===== CREATE CRITICAL RECOVERY ARCHIVE ====="
tar -C "$P" -czf "$ARCHIVE"   LastFrontier.uproject   Config   Source   Content   Build   2>/dev/null || tar -C "$P" -czf "$ARCHIVE"   LastFrontier.uproject   Config   Source   Content

ls -lh "$ARCHIVE"
sha256sum "$ARCHIVE"

echo
echo "========================================"
echo "M66_SMART_RESUME_AUDIT=PASS"
echo "READ_ONLY_PROJECT=TRUE"
echo "CRITICAL_RECOVERY_ARCHIVE=$ARCHIVE"
echo "REPORT=$REPORT"
echo "========================================"
