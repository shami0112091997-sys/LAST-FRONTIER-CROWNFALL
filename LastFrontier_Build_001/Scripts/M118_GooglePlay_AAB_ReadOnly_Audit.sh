#!/usr/bin/env bash
# CROWNFALL: app bundle acceptance evidence ONLY, no editing/repacking/signing/upload.
set -uo pipefail
export LC_ALL=C
AAB="${M118_AAB:-$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab}"
UPLOAD_SHA256='40:C0:DB:40:40:BE:0B:F9:B2:50:BD:4D:64:F9:7E:34:05:33:06:C2:C0:25:DC:3F:86:EC:48:BC:2A:DE:A1:B8'
errors=0
warns=0
pass(){ printf 'M118_%s=PASS\n' "$1"; }
fail(){ printf 'M118_%s=BLOCKED\n' "$1"; errors=$((errors+1)); }
warn(){ printf 'M118_%s=REVIEW\n' "$1"; warns=$((warns+1)); }
if [[ ! -f "$AAB" || ! -s "$AAB" || -L "$AAB" ]]; then fail AAB_EXISTS; exit 2; fi
pass AAB_EXISTS
printf 'M118_AAB_SIZE_BYTES=%s\n' "$(stat -c '%s' -- "$AAB" 2>/dev/null)"
if python3 - "$AAB" <<'PY'
import sys,zipfile
p=sys.argv[1]
if not zipfile.is_zipfile(p): sys.exit(2)
with zipfile.ZipFile(p) as z:
 if z.testzip() is not None: sys.exit(2)
 n=set(z.namelist())
 if not {'BundleConfig.pb','base/manifest/AndroidManifest.xml'}.issubset(n): sys.exit(2)
 if not any(x.startswith('base/lib/arm64-v8a/') and x.endswith('.so') for x in n): sys.exit(2)
 # Require actual game payload, not only tiny UECommandLine/vkquality metadata.
 payload=sum(v.file_size for v in z.infolist() if v.filename.startswith('obbassets/assets/') and (v.filename.endswith('.obb.png') or v.filename.endswith('.obb')))
 payload+=sum(v.file_size for v in z.infolist() if (v.filename.startswith('base/assets/') or '/assets/' in v.filename) and v.filename.endswith(('.pak','.ucas','.utoc')))
 if payload < 5_000_000: sys.exit(2)
PY
then pass ZIP_STRUCTURE_ARM64_ASSETS; else fail ZIP_STRUCTURE_ARM64_ASSETS; fi
if command -v jarsigner >/dev/null 2>&1 && jarsigner -verify "$AAB" >/dev/null 2>&1; then pass JAR_SIGNATURE_INTEGRITY; else fail JAR_SIGNATURE_INTEGRITY; fi
if command -v keytool >/dev/null 2>&1; then
  certs="$(keytool -printcert -jarfile "$AAB" 2>/dev/null | sed -nE 's/^.*SHA256:[[:space:]]*([0-9A-Fa-f:]{95}).*$/\1/p' | tr '[:lower:]' '[:upper:]')"
  if [[ "$certs" == "$UPLOAD_SHA256" ]]; then pass PLAY_UPLOAD_CERT_MATCH; else fail PLAY_UPLOAD_CERT_MATCH; fi
else fail KEYTOOL_AVAILABLE; fi
BT=()
if command -v bundletool >/dev/null 2>&1; then BT=("$(command -v bundletool)")
elif [[ -n "${M118_BUNDLETOOL_JAR:-}" && -r "${M118_BUNDLETOOL_JAR}" ]]; then BT=(java -jar "$M118_BUNDLETOOL_JAR")
else fail BUNDLETOOL_AVAILABLE; fi
if (( ${#BT[@]} > 0 )); then
 if "${BT[@]}" validate --bundle="$AAB" >/dev/null 2>&1; then pass BUNDLETOOL_VALIDATION; else fail BUNDLETOOL_VALIDATION; fi
 val(){ "${BT[@]}" dump manifest --bundle="$AAB" --xpath="$1" 2>/dev/null | tr -d '\r\n\"'; }
 if [[ "$(val /manifest/@package)" == "com.crownfall.stronghold" ]]; then pass PACKAGE_NAME; else fail PACKAGE_NAME; fi
 if [[ "$(val /manifest/@android:versionCode)" == "218" ]]; then pass VERSION_CODE_218; else fail VERSION_CODE_218; fi
 if [[ "$(val /manifest/uses-sdk/@android:targetSdkVersion)" == "36" ]]; then pass TARGET_API_36; else fail TARGET_API_36; fi
 DEBUGGABLE="$(val /manifest/application/@android:debuggable)"
 if [[ -z "$DEBUGGABLE" || "$DEBUGGABLE" == "false" ]]; then pass NON_DEBUGGABLE; else fail NON_DEBUGGABLE; fi
 TESTONLY="$(val /manifest/application/@android:testOnly)"
 if [[ -z "$TESTONLY" || "$TESTONLY" == "false" ]]; then pass NON_TEST_ONLY; else fail NON_TEST_ONLY; fi
 CONFIG="$("${BT[@]}" dump config --bundle="$AAB" 2>/dev/null || true)"
 if [[ "$CONFIG" == *PAGE_ALIGNMENT_16K* ]]; then pass BUNDLE_PAGE_ALIGNMENT_16K
 elif [[ "$CONFIG" == *PAGE_ALIGNMENT_4K* ]]; then warn BUNDLE_PAGE_ALIGNMENT_4K
 else warn BUNDLE_PAGE_ALIGNMENT_UNKNOWN; fi
fi
printf 'M118_PLAY_CONSOLE_VERSION_218_AVAILABILITY=UNVERIFIED\n'
printf 'M118_DEVICE_INSTALL_AND_GAMEPLAY=UNVERIFIED\n'
printf 'M118_STORE_POLICY_DECLARATIONS=REVIEW_REQUIRED\n'
printf 'M118_ERRORS=%s\nM118_WARNINGS=%s\n' "$errors" "$warns"
printf 'M118_UPLOAD_PERFORMED=NO\n'
if (( errors > 0 )); then printf 'M118_STATUS=BLOCKED\n'; exit 2; fi
printf 'M118_STATUS=TECHNICAL_PASS_PENDING_PLAY_AND_DEVICE_CHECKS\n'