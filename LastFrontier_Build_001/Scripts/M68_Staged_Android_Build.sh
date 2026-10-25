#!/usr/bin/env bash
# CROWNFALL M68 -- explicitly authorized staging build on the EXISTING VM.
# Never changes live source or TestMap; never provisions clouds or uploads to Play.
set -Eeuo pipefail
umask 077
SRC="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
UE="$HOME/UE_5.8.3"
ROOT="$HOME/crownfall/M68_STAGED_BUILDS"
NEXT="${NEXT_VERSION_CODE:-}"
MAX="${CONFIRMED_PLAY_MAX_CODE:-}"
stop(){ echo "M68_BLOCKED=$1"; exit 2; }
test "${M68_BUILD_APPROVED:-}" = YES || stop APPROVAL_REQUIRED
test "${M68_ASSETS_APPROVED:-}" = YES || stop VERIFY_VM_ASSETS_FIRST
test "${M68_LOCAL_SIGNING_CONFIRMED:-}" = YES || stop UPLOAD_KEY_NOT_CONFIRMED
[[ "$NEXT" =~ ^[0-9]+$ && "$MAX" =~ ^[0-9]+$ ]] || stop VERSION_INVALID
# Version 218 has already appeared in Google Play. Never reuse it, even if
# a stale or incorrect CONFIRMED_PLAY_MAX_CODE is supplied.
(( NEXT > MAX && NEXT > 218 )) || stop VERSION_NOT_ABOVE_PLAY_218
test -f "$SRC/LastFrontier.uproject" || stop SOURCE_NOT_FOUND
test -s "$SRC/Content/Maps/TestMap.umap" || stop MAP_MISSING
test -x "$UE/Engine/Binaries/Linux/UnrealEditor-Cmd" || stop UE_EDITOR_MISSING
test -x "$UE/Engine/Build/BatchFiles/Linux/Build.sh" || stop UE_BUILD_MISSING
test -x "$UE/Engine/Build/BatchFiles/RunUAT.sh" || stop UE_UAT_MISSING
test -d "$UE/Engine/Platforms/Android" || stop ANDROID_PLATFORM_MISSING
for cmd in rsync unzip python3 readelf jarsigner timeout; do
  command -v "$cmd" >/dev/null || stop "MISSING_TOOL:$cmd"
done
mkdir -p "$ROOT"
FREE="$(df -Pk "$ROOT" | awk 'END {print $4}')"
[[ "$FREE" =~ ^[0-9]+$ ]] || stop FREE_SPACE_UNKNOWN
(( FREE >= 80*1024*1024 )) || stop NEED_80GB_FREE
RUN="$ROOT/$(date -u +%Y%m%dT%H%M%SZ)"
test ! -e "$RUN" || stop RUN_EXISTS
mkdir -p "$RUN/stage" "$RUN/logs" "$RUN/archive"
exec > >(tee "$RUN/logs/gate.log") 2>&1
echo "M68_RUN=$RUN"
echo "NO_ENGINE_DOWNLOAD=TRUE"
echo "NO_PLAY_UPLOAD=TRUE"
echo "SOURCE_ORIGINAL=$SRC"
# Time-stamped isolated copy, excluding derived/temporary folders only.
# Reject symlinked content to avoid accidentally acting on files outside staged source.
if [[ -n "$(find "$SRC/Content" -type l -print -quit)" ]]; then stop SYMLINKED_CONTENT_NOT_SAFE; fi
rsync -a --exclude='Saved/' --exclude='Intermediate/' --exclude='Binaries/' \
 --exclude='DerivedDataCache/' --exclude='.git/' "$SRC/" "$RUN/stage/" || stop COPY_FAILED
PROJ="$RUN/stage/LastFrontier.uproject"
CFG="$RUN/stage/Config/DefaultEngine.ini"
ORIG_HASH="$(sha256sum "$SRC/Content/Maps/TestMap.umap" | cut -d' ' -f1)"
COPY_HASH="$(sha256sum "$RUN/stage/Content/Maps/TestMap.umap" | cut -d' ' -f1)"
test "$ORIG_HASH" = "$COPY_HASH" || stop MAP_COPY_HASH_MISMATCH
grep -Fqx 'PackageName=com.crownfall.stronghold' "$CFG" || stop PACKAGE_MISMATCH
grep -Fqx 'TargetSDKVersion=36' "$CFG" || stop TARGET_SDK_MISMATCH
grep -Fqx 'bBuildForArm64=True' "$CFG" || stop ARM64_MISSING
grep -Fqx 'bEnableBundle=True' "$CFG" || stop AAB_MISSING
python3 - "$CFG" "$NEXT" <<'PY'
import sys,re,pathlib
p=pathlib.Path(sys.argv[1]);s=p.read_text()
assert len(re.findall(r"(?m)^StoreVersion=\d+(?=\r?$)",s,re.M))==1
s=re.sub(r"(?m)^StoreVersion=\d+(?=\r?$)","StoreVersion="+sys.argv[2],s,count=1,flags=re.M)
p.write_text(s)
PY
grep -Fqx "StoreVersion=$NEXT" "$CFG" || stop VERSION_NOT_UPDATED
# Epic's Python commandlet requires PythonScriptPlugin enabled in this project.
# With DisableEnginePluginsByDefault, fail BEFORE paying for a long compile.
python3 - "$PROJ" <<'PY'
import json, sys
p=json.load(open(sys.argv[1], encoding="utf-8"))
plugins={x.get("Name"):x.get("Enabled", True) for x in p.get("Plugins", [])}
if p.get("DisableEnginePluginsByDefault") is True and plugins.get("PythonScriptPlugin") is not True:
    print("M68_BLOCKED=PYTHON_PLUGIN_DISABLED_USE_APPROVED_EDITOR_ONLY_MAP_LOADER")
    sys.exit(2)
PY

"$UE/Engine/Build/BatchFiles/Linux/Build.sh" LastFrontierEditor Linux Development "$PROJ" \
 -NoHotReloadFromIDE -Progress > "$RUN/logs/editor.log" 2>&1 || {
 tail -n 100 "$RUN/logs/editor.log"; stop EDITOR_BUILD_FAILED;
}
echo "M68_REAL_EDITOR_BUILD=PASS"
# Load the map through REAL Unreal Python editor commandlet AFTER compiling staged game module.
cat > "$RUN/logs/verify_map.py" <<'PY'
import unreal
package=unreal.load_package("/Game/Maps/TestMap")
if package is None:
    raise RuntimeError("M68_MAP_PACKAGE_MISSING")
world=unreal.find_object(package, "TestMap", unreal.World)
if world is None:
    raise RuntimeError("M68_MAP_WORLD_MISSING")
unreal.log("M68_MAP_LOADED_OK")
PY
set +e
timeout 900 "$UE/Engine/Binaries/Linux/UnrealEditor-Cmd" "$PROJ" \
 -run=pythonscript -script="$RUN/logs/verify_map.py" \
 -nullrhi -unattended -nosound -stdout -FullStdOutLogOutput \
 > "$RUN/logs/map.log" 2>&1
RC=$?
set -e
if (( RC != 0 )) || ! grep -Fq M68_MAP_LOADED_OK "$RUN/logs/map.log" ||
  grep -Eiq 'Serialization error|FName.*outside of the valid range|LogLinker: Error|Fatal error|Assertion failed' "$RUN/logs/map.log"; then
 tail -n 80 "$RUN/logs/map.log"; stop MAP_LOAD_FAILED
fi
echo "M68_REAL_MAP_LOAD=PASS"

# Locally configured upload signing must already be present. Never print passwords.
"$UE/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun -project="$PROJ" -noP4 \
 -platform=Android -cookflavor=ASTC -clientconfig=Shipping \
 -build -cook -stage -pak -package -archive -distribution -unattended -utf8output \
 -archivedirectory="$RUN/archive" > "$RUN/logs/android.log" 2>&1 || {
 tail -n 120 "$RUN/logs/android.log"; stop ANDROID_COOK_OR_BUILD_FAILED;
}
COUNT="$(find "$RUN/archive" -type f -name '*.aab' | wc -l)"
test "$COUNT" -eq 1 || stop EXPECTED_ONE_AAB
AAB="$(find "$RUN/archive" -type f -name '*.aab' -print -quit)"
test -s "$AAB" || stop EMPTY_AAB
unzip -Z1 "$AAB" > "$RUN/logs/entries.txt" || stop BROKEN_AAB
grep -Fqx 'base/manifest/AndroidManifest.xml' "$RUN/logs/entries.txt" || stop AAB_MANIFEST_MISSING
grep -Eq '^base/lib/arm64-v8a/.*\.so$' "$RUN/logs/entries.txt" || stop ARM64_LIBS_MISSING
jarsigner -verify -strict "$AAB" > "$RUN/logs/signature.txt" 2>&1 || stop SIGNATURE_INVALID
# Check native ELF segment alignment (separate from Play's APK ZIP alignment checks).
mkdir -p "$RUN/native"
while IFS= read -r LIB; do
  BASENAME="$(basename "$LIB")"
  unzip -p "$AAB" "$LIB" > "$RUN/native/$BASENAME" || stop SO_EXTRACT_FAILED
  ALIGNS="$(readelf -W -l "$RUN/native/$BASENAME" | awk '/^[[:space:]]*LOAD[[:space:]]/ {print $NF}')"
  test -n "$ALIGNS" || stop NO_ELF_LOAD_SEGMENTS
  for V in $ALIGNS; do
    [[ "$V" =~ ^0x[[:xdigit:]]+$ ]] || stop ELF_ALIGN_UNREADABLE
    (( V >= 0x4000 )) || stop ELF_NOT_16KB_ALIGNED
  done
done < <(grep -E '^base/lib/arm64-v8a/.*\.so$' "$RUN/logs/entries.txt")
sha256sum "$AAB" > "$RUN/logs/AAB_SHA256.txt"
echo "M68_SIGNED_AAB_BUILT_AND_STRUCTURALLY_AUDITED=$AAB"
echo "M68_READY_FOR_PLAY_UPLOAD=NO"
echo "PENDING=VERIFY_PACKAGE_VERSION_VIA_BUNDLETOOL_UPLOAD_CERT_FINGERPRINT_16KB_APK_ALIGNMENT_DEVICE_TEST_AND_PLAY_CONSOLE_POLICY"
FINAL_HASH="$(sha256sum "$SRC/Content/Maps/TestMap.umap" | cut -d' ' -f1)"
test "$FINAL_HASH" = "$ORIG_HASH" || stop LIVE_MAP_CHANGED
echo "SOURCE_VM_PROJECT_MODIFIED=NO"
