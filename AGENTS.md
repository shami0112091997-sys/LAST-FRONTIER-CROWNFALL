# CROWNFALL — Instructions for AI coding agents

## Mission
Help recover **LAST FRONTIER: CROWNFALL** as a real Unreal Engine Android game. Prioritize evidence-backed diagnosis of the Android splash-then-exit failure. Issue #3 is the active blocker and the primary project status reference.

## Evidence and truthfulness
- Do **not** claim that a Python, WebView, mock, lint or static check proves Unreal Engine can Compile, Cook, Stage, Package or launch on Android.
- Treat historic `TestMap.umap` serialization/cook failure as verified **historical** evidence, not a proven cause of Google Play versionCode 218's runtime crash.
- Confirm actual package provenance and the installed `versionCode` before attributing device crashes.
- Distinguish the WebView and native Unreal project paths even if they share an Android package ID.
- State explicitly when UE 5.8, SDK/NDK, signing tools or Android devices are unavailable. Never invent build logs, tests or pass states.

## Safety boundaries
- Work only on a **separate feature/recovery branch**. Never modify, force-push or directly commit to `main`, `m66`, original M84/M106 backups or original Play v218.
- No automatic merge, public Play release, Play Console uploads, production secrets, keystores/JKS or credentials.
- Do not incur cloud compute charges, start resource-intensive UE builds or change billing without an explicit approval for that operation.
- Never read, copy, upload or print private signing keys, passwords, API tokens or unrelated private research.
- Prefer read-only inspections and reversible changes. Keep each change small and reviewable.
- Do not discard user assets. Preserve suspect binary `.umap` files for forensic comparison; replace only in an isolated Unreal Editor sandbox.

## Work allocation and handoff
- **Coordinator:** choose the next evidence-driven task, decompose work and enforce stop conditions.
- **Unreal / Map:** examine map provenance, create a new test map in a real UE 5.8 editor sandbox, prove editor load and Cook.
- **Android / Packaging:** distinguish AAB/APK asset delivery, Google PAD/Pak/JNI, and collect package version + first fatal Android/Unreal log from an authorized test device.
- **Code / Codex:** inspect scripts and CI, propose minimal branch-only changes and unit tests.
- **QA / Evidence:** independently review logs/artifacts and mark proof levels (unverified, static, actual build, device test).
- **Release reviewer:** only after reproducible success, check permissions, versionCode >218, signing and policy compliance before proposing *internal testing only*.

## Acceptance criteria
1. Obtain real `versionCode` + first fatal Android/Unreal device log for the crashing build.
2. Obtain and validate authentic relevant AAB / VM / map provenance without handling signing secrets.
3. Load / cook a valid map in a licensed genuine Unreal environment.
4. Demonstrate successful native Compile + Cook + Stage + Package with preserved logs.
5. Independently launch a newer, previously unused versionCode (>218) on Android, enter the intended map and remain running.
6. Submit evidence and reviewable PRs; do not announce resolution or publish until steps are independently verified.

When a dependency cannot be verified or access is missing, stop at the evidence boundary and give the exact next non-destructive step.
