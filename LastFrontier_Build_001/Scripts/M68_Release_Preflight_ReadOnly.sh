#!/usr/bin/env bash
# LAST FRONTIER: CROWNFALL — M68 release preflight (read-only project).
# Existing GCP VM only. No engines installed, no cloud resources provisioned.
set -Eeuo pipefail
umask 077
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
E="$HOME/UE_5.8.3"
OUT="$HOME/crownfall/M68_RELEASE_AUDIT"
mkdir -p "$OUT"
LOG="$OUT/M68_$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee "$LOG") 2>&1
section(){ printf '\n=== %s ===\n' "$1"; }
fail(){ echo "M68_BLOCKED=$1"; echo "REPORT=$LOG"; exit 2; }
echo "CROWNFALL_M68_AUDIT_ONLY=TRUE"
echo "HOST=$(hostname)"
echo "PROJECT=$P"
echo "ENGINE=$E"
echo "REPORT=$LOG"
section "CHECK EXISTING REAL PROJECT"
test -f "$P/LastFrontier.uproject" || fail "PROJECT_NOT_FOUND"
test -s "$P/Content/Maps/TestMap.umap" || fail "TESTMAP_MISSING"
test -d "$P/Source" || fail "SOURCE_MISSING"
test -x "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" || fail "UE_EDITOR_MISSING"
test -x "$E/Engine/Build/BatchFiles/Linux/Build.sh" || fail "UE_BUILD_MISSING"
test -x "$E/Engine/Build/BatchFiles/RunUAT.sh" || fail "UE_UAT_MISSING"
section "SOURCE IMMUTABILITY HASHES"
sha256sum "$P/LastFrontier.uproject" "$P/Content/Maps/TestMap.umap"
stat -c 'MAP_BYTES=%s' "$P/Content/Maps/TestMap.umap"
if test -d "$P/Content/Environment/Real"; then
 echo "REAL_ASSETS=$(find "$P/Content/Environment/Real" -type f -name '*.uasset' | wc -l)"
 du -sh "$P/Content/Environment/Real"
else
 echo "WARNING=REAL_ASSETS_NOT_FOUND_ON_THIS_PROJECT_PATH"
fi
section "ANDROID CONFIG VS PLAY POLICY"
CFG="$P/Config/DefaultEngine.ini"
test -f "$CFG" || fail "ANDROID_CONFIG_MISSING"
for v in 'PackageName=com.crownfall.stronghold' 'TargetSDKVersion=36' 'bBuildForArm64=True' 'bEnableBundle=True'; do
 grep -Fqx "$v" "$CFG" || fail "CONFIG_MISMATCH:$v"
done
CURRENT="$(sed -n 's/^StoreVersion=//p' "$CFG" | tail -1)"
case "$CURRENT" in ''|*[!0-9]*) fail "STORE_VERSION_INVALID";; esac
echo "SOURCE_STORE_VERSION=$CURRENT"
if test "$CURRENT" -le 217; then
 echo "PLAY_VERSION_RISK=SOURCE_CODE_NOT_ABOVE_RECORDED_217"
fi
echo "PLAY_MAX_CODE_MUST_BE_CONFIRMED_FROM_CONSOLE=TRUE"
echo "API36_BUILD_COMPATIBILITY=NOT_YET_TESTED"
section "STREETLAMP DIAGNOSTIC STATE"
if test -f "$HOME/crownfall/M63_STREETLAMP_LOD.log"; then
 grep -E 'SET_LODS_RESULT|ROLLBACK' "$HOME/crownfall/M63_STREETLAMP_LOD.log" | tail -10 || true
else
 echo "LOD_LOG_MISSING"
fi
echo "LOD_MUTATION=BLOCKED_PENDING_CAUSE"
section "COMPUTE RESOURCES / SDK (NO MODIFICATIONS)"
df -h "$HOME" "$OUT" || true
free -h || true
for c in java javac jarsigner unzip readelf rsync python3; do
 command -v "$c" >/dev/null 2>&1 && echo "FOUND_TOOL=$c" || echo "MISSING_TOOL=$c"
done
for d in "$E/Engine/Platforms/Android" "$HOME/Android/Sdk"; do
 test -d "$d" && echo "FOUND_DIR=$d" || echo "MISSING_DIR=$d"
done
section "RELEASE CONDITIONS"
echo "M60_GITHUB_COOK_MAP_SERIALIZATION_ERROR=CONFIRMED_IN_37645589203"
echo "M63_VM_MAP=NEEDS_REAL_LOAD_PROBE"
echo "REAL_ANDROID_SHIPPING_AAB=NOT_VERIFIED"
echo "SIGNING_KEY_MATCH_TO_PLAY=NOT_VERIFIED"
echo "16KB_ELF_ALIGNMENT=NOT_VERIFIED"
echo "DATA_SAFETY_PRIVACY_AGE_RATING=NEEDS_PLAY_CONSOLE_REVIEW"
echo "DEVICE_TEST=NOT_VERIFIED"
echo "M68_AUDIT_COMPLETE=YES"
echo "M68_FINAL_UPLOAD_READY=NO"
echo "REPORT=$LOG"
