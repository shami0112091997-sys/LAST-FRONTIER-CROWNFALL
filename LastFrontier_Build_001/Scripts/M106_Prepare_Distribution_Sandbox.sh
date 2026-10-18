#!/usr/bin/env bash
# CROWNFALL M106: prepare an isolated Android Distribution workspace, NOT a build, NOT a signing step.
set -Eeuo pipefail
umask 077
SRC="${M106_SOURCE:-$HOME/crownfall/M84_EDITOR_SANDBOX_v218}"
CANON="${M106_CANONICAL:-$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001}"
DEST="${M106_DEST:-$HOME/crownfall/M106_RELEASE_SANDBOX_v218}"
ENGINE="${M106_ENGINE:-$HOME/UE_5.8.3}"
MIN_FREE_KB="${M106_MIN_FREE_KB:-26214400}" # 25 GiB
abort() { echo "M106_BLOCKED=$1"; exit 2; }

[[ "$SRC" != "$DEST" && "$CANON" != "$DEST" ]] || abort SAME_SOURCE_AND_DESTINATION
[[ ! -e "$DEST" && ! -L "$DEST" ]] || abort DESTINATION_ALREADY_EXISTS
command -v rsync >/dev/null || abort RSYNC_NOT_FOUND
[[ -s "$SRC/LastFrontier.uproject" ]] || abort SOURCE_PROJECT_MISSING
[[ -s "$SRC/Content/Maps/TestMap.umap" ]] || abort SOURCE_MAP_MISSING
[[ -s "$CANON/Content/Maps/TestMap.umap" ]] || abort CANONICAL_MAP_MISSING
cmp -s "$SRC/Content/Maps/TestMap.umap" "$CANON/Content/Maps/TestMap.umap" || abort MAP_MISMATCH
[[ -s "$SRC/Config/DefaultEngine.ini" ]] || abort ENGINE_INI_MISSING
[[ -s "$SRC/Saved/Cooked/Android_ASTC/LastFrontier/Content/Maps/TestMap.umap" ]] || abort COOKED_MAP_MISSING
[[ -s "$SRC/Binaries/Android/LastFrontier-Android-Shipping-arm64.so" ]] || abort SHIPPING_BINARY_MISSING
[[ -x "$ENGINE/Engine/Build/BatchFiles/RunUAT.sh" ]] || abort ENGINE_UAT_MISSING
for entry in 'PackageName=com.crownfall.stronghold' 'StoreVersion=218' 'TargetSDKVersion=36' 'bEnableBundle=True'; do
  grep -Fqx "$entry" "$SRC/Config/DefaultEngine.ini" || abort "CONFIG_MISSING:$entry"
done
[[ "$MIN_FREE_KB" =~ ^[0-9]+$ ]] || abort DISK_THRESHOLD_INVALID
FREE_KB=$(df -Pk "$SRC" | awk 'END{print $4}')
[[ "$FREE_KB" =~ ^[0-9]+$ && "$FREE_KB" -ge "$MIN_FREE_KB" ]] || abort LOW_DISK_SPACE
mkdir -p "$(dirname "$DEST")"
source_map_sha=$(sha256sum "$SRC/Content/Maps/TestMap.umap" | cut -d ' ' -f1)
source_ini_sha=$(sha256sum "$SRC/Config/DefaultEngine.ini" | cut -d ' ' -f1)
source_original_ini_sha=$(sha256sum "$SRC/Config/DefaultGame.ini" | cut -d ' ' -f1) || abort DEFAULT_GAME_INI_MISSING
[[ -s "$SRC/Config/DefaultGame.ini" ]] || abort DEFAULT_GAME_INI_MISSING

echo 'M106_PREFLIGHT=PASS'
TMP=$(mktemp -d "${DEST}.partial.XXXXXXXX")
cleanup() { if [[ -n "${TMP:-}" && -d "$TMP" ]]; then rm -rf -- "$TMP"; fi; }
trap cleanup EXIT
rsync -a --exclude='.git/' --exclude='Intermediate/' --exclude='Saved/StagedBuilds/' \
  --exclude='Saved/Logs/' --exclude='Saved/Sandboxes/' --exclude='*.aab' --exclude='*.apk' \
  --exclude='*.jks' --exclude='*.keystore' --exclude='*.p12' --exclude='*.pfx' \
  "$SRC/" "$TMP/"

# Preserve original Content/Source; set packaging properties ONLY in the copied DefaultGame.ini.
python3 - "$TMP/Config/DefaultGame.ini" <<'PY'
from pathlib import Path
import sys, re
p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8')
header = '[/Script/UnrealEd.ProjectPackagingSettings]'
lines = s.splitlines(keepends=True)
start = next((i for i,l in enumerate(lines) if l.strip().lower() == header.lower()), None)
if start is None:
    if lines and not lines[-1].endswith('\n'):
        lines.append('\n')
    lines += ['\n', header+'\n']
    start = len(lines) - 1
end = next((i for i in range(start+1,len(lines)) if re.match(r'^\s*\[.+\]\s*$',lines[i])),len(lines))
keys = {'BuildConfiguration':'PPBC_Shipping','ForDistribution':'True','IncludeDebugFiles':'False'}
old_section = lines[start+1:end]
for key in keys:
    old_section = [l for l in old_section if not re.match(r'^\s*'+re.escape(key)+r'\s*=',l,re.I)]
old_section.extend(f'{key}={value}\n' for key,value in keys.items())
new_lines = lines[:start+1]+old_section+lines[end:]
p.write_text(''.join(new_lines),encoding='utf-8')
for key,value in keys.items():
    assert re.findall(r'(?m)^'+re.escape(key)+r'\s*=\s*([^\r\n]+)', ''.join(old_section),re.I) == [value], key
print('M106_DISTRIBUTION_CONFIG=PASS')
PY

cmp -s "$SRC/Content/Maps/TestMap.umap" "$TMP/Content/Maps/TestMap.umap" || abort STAGED_MAP_CHANGED
cmp -s "$SRC/Config/DefaultEngine.ini" "$TMP/Config/DefaultEngine.ini" || abort STAGED_ANDROID_CONFIG_CHANGED
[[ -s "$TMP/Saved/Cooked/Android_ASTC/LastFrontier/Content/Maps/TestMap.umap" ]] || abort STAGED_COOKED_MAP_MISSING
[[ -s "$TMP/Binaries/Android/LastFrontier-Android-Shipping-arm64.so" ]] || abort STAGED_SHIPPING_BINARY_MISSING
if find "$TMP" -type f \( -iname '*.jks' -o -iname '*.keystore' -o -iname '*.p12' -o -iname '*.pfx' -o -iname '*.aab' -o -iname '*.apk' \) -print -quit | grep -q .; then
  abort PRIVATE_OR_PREVIOUS_BINARY_INCLUDED
fi
[[ "$source_map_sha" == "$(sha256sum "$SRC/Content/Maps/TestMap.umap" | cut -d ' ' -f1)" ]] || abort SOURCE_MAP_CHANGED
[[ "$source_ini_sha" == "$(sha256sum "$SRC/Config/DefaultEngine.ini" | cut -d ' ' -f1)" ]] || abort SOURCE_ANDROID_CONFIG_CHANGED
[[ "$source_original_ini_sha" == "$(sha256sum "$SRC/Config/DefaultGame.ini" | cut -d ' ' -f1)" ]] || abort SOURCE_GAME_CONFIG_CHANGED
mv -- "$TMP" "$DEST"
TMP=''
echo 'M106_SOURCE_UNCHANGED=PASS'
echo 'M106_MAP_INTEGRITY=PASS'
echo 'M106_COOK_PRESERVED=PASS'
echo 'M106_OLD_GRADLE_EXCLUDED=PASS'
echo 'M106_BUILD_NOT_STARTED=CONFIRMED'
echo "M106_SANDBOX_PATH=$DEST"
echo 'M106_PREPARE_COMPLETE=PASS'
