#!/usr/bin/env bash
# CROWNFALL M127: run M125 asset-pack and corrected M126 JNI static audits.
# No downloads, build, signing, publishing, file writes or private log output.
set -u
umask 077
BASE="$HOME/crownfall/M106_RELEASE_SANDBOX_v218"
AAB="$BASE/Binaries/Android/LastFrontier-Android-Shipping.aab"
SCRIPTS="${1:-$HOME/crownfall}"
if [ -L "$AAB" ] || [ ! -s "$AAB" ]; then
  printf '%s\n' 'M127_AAB=ABSENT_OR_UNSAFE' 'M127_RUNTIME_CAUSE=UNCONFIRMED'
  exit 2
fi
for script in M125_CROWNFALL_218_ReadOnly_Diagnostic.py M126_GooglePAD_Dex_Method_Audit_ReadOnly.py; do
  if [ -L "$SCRIPTS/$script" ] || [ ! -s "$SCRIPTS/$script" ]; then
    printf '%s\n' 'M127_SCRIPTS=MISSING_OR_UNSAFE' 'M127_RUNTIME_CAUSE=UNCONFIRMED'
    exit 2
  fi
done
printf '%s\n' 'M127_MODE=READ_ONLY_STATIC_NO_DEVICE_LOG'
python3 "$SCRIPTS/M125_CROWNFALL_218_ReadOnly_Diagnostic.py" --aab "$AAB" --project "$BASE/LastFrontier.uproject" --config "$BASE/Config/DefaultEngine.ini"
S1=$?
python3 "$SCRIPTS/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py" --aab "$AAB"
S2=$?
printf 'M127_PAD_AAB_SCAN_EXIT=%s\nM127_JNI_CLASS_SCAN_EXIT=%s\n' "$S1" "$S2"
printf '%s\n' 'M127_RUNTIME_CAUSE=NOT_DETERMINED_NO_DEVICE_STACK_TRACE'
if [ "$S1" -eq 2 ] || [ "$S2" -eq 2 ]; then exit 2; fi
if [ "$S1" -ne 0 ] || [ "$S2" -ne 0 ]; then exit 3; fi
exit 0
