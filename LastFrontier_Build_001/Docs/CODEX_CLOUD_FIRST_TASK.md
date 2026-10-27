# CROWNFALL — Codex Cloud first task / المهمة الأولى لوكيل Codex

## Setup
- Repo: `shami0112091997-sys/LAST-FRONTIER-CROWNFALL`
- **Required starting ref:** `m138-android-startup-evidence-agent`, based on `m137-secure-map-recovery`.
- Authoritative issue: #3. Draft review: #5. Guardrails from draft PR #4 must be followed even though that separate branch has not been merged.
- Use a **separate worktree/task branch**, never modify `main`, `m66`, original M84/M106, Play v218, keystores or credentials.
- No automatic GitHub PR merges, publishing, signing, paid cloud builds, or live Android-device access.

## First Codex task (copy into a new Codex Cloud task)

Analyze the unresolved Unreal 5.8 Android **splash then exit** blocker (#3) for `LAST-FRONTIER-CROWNFALL`.
Read #3, this document, docs/M138_ANDROID_BOOT_EXIT_EVIDENCE_AR.md and existing M131–M137 evidence. Run a **source-only and test-only** audit, keeping WebView 214 separate from the native Unreal source with StoreVersion 215 and unverified Play AAB 218.

1. Validate M138 Python syntax and run the four tests in `Scripts/test_M138_readonly.py` in a sandbox. Audit the agent's ADB call allowlist, redaction, package/version parsing and stale-log caveats.
2. Independently review prior M137 tests and M136 isolated map runner. No mock test can establish UE Editor/Cook/Android success.
3. Identify the smallest real evidence gaps preventing diagnosis: installed build `versionCode`, timestamp-aligned first Android/Unreal fatal log, original AAB/build provenance, genuine UE 5.8 map load+Cook.
4. If source-code bugs are found, propose **minimal, reversible patches on a new feature branch** and tests. Keep all output in a draft PR, with no automatic merge.
5. Report a traceable evidence table: claim, supporting file/run, test type, status, what still cannot be concluded.
6. **STOP** before installing Unreal Engine, running prolonged builds, interacting with devices/accounts, incurring billable compute or handling secrets. Request an explicit per-operation approval if needed.

Acceptance criteria for this first task: all relevant source-only checks are reproducible, any fixes have new unit tests, no private data leaked, no original asset mutated, and Android/UE runtime claims remain unverified until genuinely tested.

## Next specialized tasks
- **Unreal:** validate the exact historical TestMap blob and create/reload a new map only in an approved existing UE5.8 sandbox; preserve known-bad original. Cook only when build environment and budget are authorized.
- **Android QA:** test the M138 snapshot on a tester-owned external computer/device with informed permission; time-match crash logs privately; disclose only redacted class counts and confirmed `versionCode`.
- **Release reviewer:** require a successfully booting and independently tested native Unreal package with unused versionCode >218; internal testing only after explicit approval.
- **Coordinator:** summarize blockers once a day without claiming unperformed tests. Keep confidential β-research OUT of this public repository.

## Why cloud setup needs account action

A Codex Cloud environment must be created/published from Codex on web or desktop with the right repository. The connected ChatGPT GitHub integration alone does **not** create or publish a Codex Cloud environment. After publication it can be used to start tasks from the mobile app. This document prepares the coding task; it does not itself start a Codex agent.
