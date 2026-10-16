#!/usr/bin/env bash
# LAST FRONTIER: CROWNFALL M67 — read-only StreetLamp LOD diagnostics.
# Captures logs/source/config without modifying project content or Unreal.
set -Eeuo pipefail
P="${P:-$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001}"
E="${E:-$HOME/UE_5.8.3}"
LODLOG="${LODLOG:-$HOME/crownfall/M63_STREETLAMP_LOD.log}"
OUT="${OUT:-$HOME/crownfall/M67_LOD_DIAGNOSTICS}"
mkdir -p "$OUT"
REPORT="$OUT/M67_StreetLampLOD_$(date -u +%Y%m%dT%H%M%SZ).txt"
exec > >(tee "$REPORT") 2>&1
section() { printf '\n===== %s =====\n' "$1"; }
echo "CROWNFALL M67 READ-ONLY STREETLAMP LOD DIAGNOSIS"
printf 'HOST=%s\nPROJECT=%s\nENGINE=%s\nLOG=%s\nREPORT=%s\n' "$(hostname)" "$P" "$E" "$LODLOG" "$REPORT"
section 'PROJECT'
[[ -f "$P/LastFrontier.uproject" ]] && echo UPROJECT_FOUND=YES || echo UPROJECT_FOUND=NO
[[ -d "$E/Engine" ]] && echo ENGINE_FOUND=YES || echo ENGINE_FOUND=NO
section 'ASSET HASH BEFORE ANY RETEST'
if [[ -d "$P/Content" ]]; then
  while IFS= read -r -d '' file; do stat -c 'ASSET=%n BYTES=%s' "$file"; sha256sum "$file"; done < <(find "$P/Content" -type f \( -iname '*StreetLamp*.uasset' -o -iname '*street*lamp*.uasset' \) -print0 2>/dev/null)
else
  echo PROJECT_CONTENT_MISSING
fi
section 'M63 LOD LOG RESULT + CAUSAL CONTEXT'
if [[ -f "$LODLOG" ]]; then
  printf 'LOG_BYTES=%s\n' "$(wc -c < "$LODLOG")"
  grep -nEi -C 6 'SET_LODS|REDUCT|SIMPLYGON|QUADRIC|MESHREDUCTION|LODS?|ERROR|FAILED|FATAL|EXCEPTION|WARNING|ROLLBACK|DEPRECAT|PLUGIN' "$LODLOG" | tail -n 240 || true
  section 'LOG TAIL'
  tail -n 110 "$LODLOG" || true
else
  echo LOD_LOG_MISSING
fi
section 'UE 5.8.3 LOCAL API SOURCE'
SRC="$E/Engine/Source/Editor/StaticMeshEditor/Private/StaticMeshEditorSubsystem.cpp"
if [[ -f "$SRC" ]]; then
  echo "UE_SOURCE=$SRC"
  grep -nE 'SetLodsWithNotification|SetLods\(|MeshReduction|ReductionSettings' "$SRC" | head -n 80 || true
  LN="$(grep -n -m1 'SetLodsWithNotification' "$SRC" | cut -d: -f1 || true)"
  if [[ "$LN" =~ ^[0-9]+$ ]]; then
    A=$((LN>12 ? LN-12 : 1)); B=$((LN+130)); sed -n "${A},${B}p" "$SRC"
  fi
else
  echo "UE_SOURCE_MISSING=$SRC"
fi
section 'REDUCTION MODULES'
for dir in "$E/Engine/Binaries/Linux" "$E/Engine/Plugins"; do
  if [[ -d "$dir" ]]; then
    find "$dir" -type f \( -iname '*meshreduction*' -o -iname '*simplygon*' -o -iname '*quadric*' \) -print 2>/dev/null | head -n 90 || true
  else
    echo "MISSING_DIRECTORY=$dir"
  fi
done
section 'CONFIG REFERENCES'
for cfg in "$P/Config/DefaultEngine.ini" "$E/Engine/Config/BaseEngine.ini"; do
  if [[ -f "$cfg" ]]; then
    echo "CONFIG=$cfg"
    grep -nEi 'MeshReduction|ReductionModule|Simplygon|Quadric|StaticMesh' "$cfg" | head -n 90 || true
  fi
done
section 'DIAGNOSIS STATE'
if [[ -f "$LODLOG" ]]; then
  grep -q 'SET_LODS_RESULT=-1' "$LODLOG" && echo NEGATIVE_RETURN=OBSERVED || echo NEGATIVE_RETURN=NOT_FOUND
  grep -Eq 'ROLLBACK[-=]PASS|ROLLBACK-PASS' "$LODLOG" && echo ROLLBACK_PASS=OBSERVED || echo ROLLBACK_PASS=NOT_FOUND
fi
echo UNREAL_EDITOR_LAUNCHED=NO
echo PROJECT_ASSETS_MODIFIED=NO
echo ROOT_CAUSE=AWAITING_LOG_INTERPRETATION
echo "REPORT=$REPORT"
