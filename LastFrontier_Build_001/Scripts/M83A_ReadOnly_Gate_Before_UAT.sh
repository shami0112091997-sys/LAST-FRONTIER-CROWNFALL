#!/usr/bin/env bash
# M83A: READ ONLY verification before any UAT BuildCookRun; never prints credentials.
set -u
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z"
E="$HOME/UE_5.8.3"
echo '=== M83A READ ONLY PREFLIGHT ==='
if [ ! -s "$D/LastFrontier.uproject" ] || [ ! -s "$D/Content/Maps/TestMap.umap" ] || [ ! -s "$D/Config/DefaultEngine.ini" ] || [ ! -s "$P/Content/Maps/TestMap.umap" ]; then echo "M83A_PROJECT=BLOCKED"; exit 2; fi
echo 'M83A_PROJECT=PASS'
if cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap"; then echo "M83A_MAP=PASS"; else echo "M83A_MAP=FAIL"; exit 2; fi
if [ -x "$E/Engine/Build/BatchFiles/RunUAT.sh" ] && [ -x "$E/Engine/Binaries/Linux/UnrealEditor-Cmd" ]; then echo "M83A_UAT_EDITOR=PASS"; else echo "M83A_UAT_EDITOR=BLOCKED"; exit 2; fi
echo '=== GAME MAP AND RELEASE CONFIG ==='
grep -E "^(GameDefaultMap|PackageName|StoreVersion|TargetSDKVersion|bBuildForArm64|bEnableBundle)=" "$D/Config/DefaultEngine.ini" || true
echo '=== PACKAGING SETTINGS ==='
grep -E "^bUseZenStore=" "$D/Config/DefaultGame.ini" || true
echo '=== STAGED EDITOR BINARIES (PRESENCE ONLY) ==='
if [ -d "$D/Binaries/Linux" ]; then find "$D/Binaries/Linux" -maxdepth 1 -type f -printf "%f\n" | head -n 12; else echo "M83A_STAGE_EDITOR_BINARIES=ABSENT"; fi
echo '=== EXISTING STAGE CONTENT (PRESENCE ONLY) ==='
if [ -d "$D/Saved/Cooked/Android_ASTC" ]; then echo "M83A_STAGE_COOK=EXISTS"; else echo "M83A_STAGE_COOK=ABSENT"; fi
if [ -d "$D/Saved/StagedBuilds" ]; then echo "M83A_STAGED_OUTPUT=EXISTS"; else echo "M83A_STAGED_OUTPUT=ABSENT"; fi
echo '=== EXISTING AAB (NEVER UPLOAD THIS DEBUG BUILD) ==='
if [ -s "$D/Binaries/Android/LastFrontier-Android-Shipping.aab" ]; then echo "M83A_DEBUG_AAB=EXISTS_NOT_READY"; else echo "M83A_AAB=MISSING"; fi
echo '=== FREE DISK / MEMORY ==='
df -h "$D" | tail -n 1
free -h | head -n 2
echo 'M83A_PREFLIGHT_COMPLETE=YES'
