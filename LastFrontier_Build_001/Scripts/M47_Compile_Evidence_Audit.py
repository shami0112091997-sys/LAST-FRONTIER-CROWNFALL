from __future__ import annotations
import pathlib, sys
root=pathlib.Path(__file__).resolve().parents[1]
logs=sorted((root/"Saved/M47Logs").glob("M47_Compile_*.log"), key=lambda p:p.stat().st_mtime, reverse=True)
if not logs:
    print("M47_EVIDENCE_STATUS=NO_REAL_COMPILE_LOG"); sys.exit(4)
log=logs[0]; txt=log.read_text(encoding="utf-8",errors="replace")
if "M47_COMPILE_STATUS=PASS" not in txt:
    print("M47_EVIDENCE_STATUS=COMPILE_NOT_PROVEN"); print(f"LOG={log}"); sys.exit(5)
bins=[p for p in (root/"Binaries").rglob("*") if p.is_file()] if (root/"Binaries").exists() else []
if not bins:
    print("M47_EVIDENCE_STATUS=PASS_MARKER_WITHOUT_BINARY_ARTIFACTS"); print(f"LOG={log}"); sys.exit(6)
print("M47_EVIDENCE_STATUS=REAL_COMPILE_PASS")
print(f"LOG={log}")
print(f"BINARY_ARTIFACTS={len(bins)}")
for p in bins[:100]: print(p.relative_to(root))
