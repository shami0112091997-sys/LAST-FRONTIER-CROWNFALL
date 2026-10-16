#!/usr/bin/env bash
# M75: Read-only project audit; never print signing secret values.
P="$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001"
D="$HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z"
C="$D/Saved/Cooked/Android_ASTC/LastFrontier/Content"
CFG="$D/Config/DefaultEngine.ini"
echo '=== M75 SHIPPING PREFLIGHT: READ ONLY ==='
for F in "$C/Maps/TestMap.umap" "$D/LastFrontier.uproject" "$CFG" "$D/Source/LastFrontier.Target.cs"; do
  if [ -s "$F" ]; then echo "PASS: $(basename "$F")"; else echo "MISSING: $(basename "$F")"; fi
done
if cmp -s "$P/Content/Maps/TestMap.umap" "$D/Content/Maps/TestMap.umap"; then echo "M75_MAP_INTEGRITY=PASS"; else echo "M75_MAP_INTEGRITY=FAIL"; fi
echo "COOKED_REAL_UASSETS=$(find "$C/Environment/Real" -type f -name '*.uasset' 2>/dev/null | wc -l)"
echo '=== RELEASE IDENTITY ==='
grep -E '^(PackageName|StoreVersion|TargetSDKVersion|bBuildForArm64|bEnableBundle)=' "$CFG" || true
echo '=== SIGNING FIELD PRESENCE ONLY (NO VALUES) ==='
for K in KeyStore KeyAlias KeyStorePassword; do
  if grep -Eq "^${K}=.+" "$CFG" 2>/dev/null; then echo "$K=CONFIGURED_REDACTED"; else echo "$K=NOT_CONFIRMED"; fi
done
echo '=== RESOURCES ==='
df -h "$D" | tail -n 1
echo 'M75_PLAY_UPLOAD_READY=NOT_YET_VERIFIED'
