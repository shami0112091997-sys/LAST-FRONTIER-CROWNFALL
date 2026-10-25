# M129 — Kimi × ChatGPT: Independent Read-Only Review Handoff

**Created:** 2026-10-25  
**Branch:** `m129-kimi-readonly-review-handoff` (branched from `m128-googlepad-delivery-candidate-only`)  
**Status:** Review instructions prepared ONLY; Kimi not connected or authorized; zero runtime tests; no AAB/VM/logcat access verified.

## 1. Purpose and strict scope

Independently review **CROWNFALL: Stronghold**, Unreal Engine 5.8.x, Android app `com.crownfall.stronghold`, focusing on the exit immediately after the Unreal splash screen that was reported for Google Play internal-test release `versionCode=218` (`versionName=2.2.0`).

**This is NOT a request to implement, build, cook, stage, sign, upload, publish, execute GitHub Actions, change Play Console, operate a user's phone, access a VM, or change any permission.**

Protected: `main`, `m66-smart-recovery`, all M106/M63/M84 release environments, JKS/signing credentials, existing Play releases, and M128 source candidate. Do not modify any of them. Do not open a PR targeting main.

If the private GitHub repository is inaccessible, do **not** imply it was reviewed. Request user-approved access to a minimal sanitized source copy instead. Never ask user to paste passwords, tokens, signing keys, or unredacted logs into a chat. A GitHub link alone does not grant Kimi access.

## 2. Known evidence and distinctions

- Previous project records M118/M119 say an AAB was built/signed/validated; they **do not** prove that the Unreal game launches on Android.
- User's observed symptom: an app installed via Play reaches the Unreal splash, then quits in about a second. The **exact installed versionCode must be confirmed** separately if not displayed by device or track details.
- User-provided Play Console screenshots of AAB 218 show `obbassets` with delivery mode **Install time**. This confirms the Play distribution configuration, not that UE successfully locates/mounts/reads the OBB on the device.
- The Play Console Crashes/ANRs screens shown for the 28-day window showed "no results" with their active filters. Pre-launch report screen showed no report to inspect. Neither absence proves successful runtime.
- There was no direct access to the actual 218 AAB bytes, its merged manifest/DEX/native binaries, M106 VM source/config, Android logcat, or Android vitals stack trace in the preceding analyses. Do not silently substitute GitHub source for any of these.
- The GitHub M128 **candidate only** explicitly enables `GooglePAD` in `LastFrontier.uproject`, sets `bPackageDataInsideApk=False`, and adds `[/Script/GooglePADEditor.GooglePADRuntimeSettings] bEnablePlugin=True`. It has **not been compiled, cooked, packaged, installed, or proved effective**.
- M128 vs `m127-jni-forensic-audit-fixes` changes only `Config/DefaultEngine.ini`, `LastFrontier.uproject`, and its M128 report. This is a diff fact, not evidence of runtime cause.
- The repository's `DefaultEngine.ini` says `StoreVersion=215` while the investigated Play bundle is 218, hence repository settings cannot automatically be claimed to be identical to the actual 218 build.
- Older M60 editor/map issues and synthetic M126/M127 analyzer regression tests are **not proof** of the reason for the 218 exit.
- `CROWNFALL_Stronghold_Android/` is a separate Android/WebView code path; do not confuse it with the Unreal `LastFrontier_Build_001/` app.

## 3. Scope of code inspection

Read these exact paths on the authorized, frozen branch only:

- `LastFrontier_Build_001/Docs/M121_CRASH_RECOVERY_RESEARCH_2026-10-19_AR.md`
- `LastFrontier_Build_001/Docs/M122_DEEP_ROOT_CAUSE_FIELD_GUIDE_AR.md`
- `LastFrontier_Build_001/Docs/M123_CRASH_FORENSICS_2026-10-19_AR.md`
- `LastFrontier_Build_001/Docs/M124_DEEP_CAUSAL_AUDIT_2026-10-20_AR.md`
- `LastFrontier_Build_001/Docs/M125_CROWNFALL_218_FIELD_GUIDE_AR.md`
- `LastFrontier_Build_001/Docs/M126_DEX_METHOD_FORENSICS_2026-10-20_AR.md`
- `LastFrontier_Build_001/Docs/M127_JNI_FORENSIC_HARDENING_2026-10-21_AR.md`
- `LastFrontier_Build_001/Docs/M128_GOOGLEPAD_ASSET_DELIVERY_CANDIDATE_AR.md`
- `LastFrontier_Build_001/Config/DefaultEngine.ini`
- `LastFrontier_Build_001/Config/DefaultGame.ini`
- `LastFrontier_Build_001/LastFrontier.uproject`
- `LastFrontier_Build_001/Source/LastFrontier/**`
- `LastFrontier_Build_001/Scripts/M125_CROWNFALL_218_ReadOnly_Diagnostic.py`
- `LastFrontier_Build_001/Scripts/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py`

Keep all findings tied to specific file names, line locations and refs. Do not execute the diagnostic scripts without a separately scoped user instruction and access to the actual AAB.

## 4. Core independent questions

1. Are M128's GooglePAD enablement and packaging choices internally consistent with Epic's **current Unreal 5.8** guidance? Is any apparent misconfiguration demonstrable in source, and which assumptions require inspecting the real M106 build?
2. Does `DisableEnginePluginsByDefault=true` with explicit `GooglePAD` entry imply anything about its generated Java/UPL/runtime state? Explain limits of deduction from source alone.
3. Does **install-time `obbassets`** materially falsify a "fast-follow not yet downloaded" explanation while leaving open mount/read/path/format faults? Distinguish distribution condition from runtime outcome.
4. What evidence would distinguish `NoSuchMethodError` / JNI signature mismatch, missing OBB/Pak or shader, `dlopen failed`, Vulkan/RHI error, `SIGSEGV`, and Android process exit/low memory?
5. Review the reasoning of M125–M127 static DEX-method checks without mistaking synthetic unit tests for live app validation. Identify false positives/false negatives or concrete static improvements that require **no execution**.
6. Inspect config and source for **definite** compile-time or logic mistakes, but don't infer that they caused the specific Play crash.
7. Before any future hypothetical fix, list build/cook/package and test gates, including verifying that the **new** versionCode exceeds 218 and hasn't already been used. Do not start those gates.

## 5. Delivery format back to the owner

Produce one Markdown report with:

- `VERIFIED_FROM_SOURCE`: exact file path and relevant lines or commit/diff, impact, confidence.
- `VERIFIED_FROM_PLAY_SCREENSHOTS`: only the facts explicitly described above (unless you actually receive screenshots).
- `UNVERIFIED_HYPOTHESES`: competing root causes and what evidence would verify/falsify each. Do not invent probabilities.
- `NEW_FINDINGS_VS_M121_M128`: concrete, reproducible new facts vs existing reports; if none, say "none".
- `NEXT_SAFEST_CHECK`: ONE prioritized action requiring no user phone or production permissions, with official docs where appropriate.
- `CANNOT_DETERMINE_WITHOUT`: missing evidence, including original AAB and real first-failure log/stack trace.
- `NO_ACTIONS_PERFORMED`: confirm there were no edits, builds, Actions, publication, signing, or access changes (or disclose any action honestly).

Return this report to the user in the Kimi interface. It can then be pasted into ChatGPT for second-pass cross-check; that handoff is not an automatic link.

## 6. Kimi-specific protective setup

- In Kimi Code CLI/Desktop, choose **Always Ask**; do not use `/yolo` or `/auto`. Request read-only review using the built-in `explore` sub-agent when available. Always Ask is not equivalent to OS-level sandboxing.
- Grant no write permission to the private GitHub repo; safest initial handoff is a sanitized user-provided local source snapshot. If repository authentication is absolutely needed, the owner must configure it themselves with least-privilege, time-limited read-only access using Kimi's official flow. **Do not share any token through ChatGPT or the review report**.
- Do not enable repo automations, self-modifying loops, remote execution, or cloud deployments.
- Do not expose private code to a third party without user authorization.

## 7. Official technical sources

- Epic UE Google Play Asset Delivery: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Epic plugin architecture: https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine
- Google Android Play Asset Delivery: https://developer.android.com/guide/playcore/asset-delivery
- Google Play pre-launch reports: https://support.google.com/googleplay/android-developer/answer/9842757
- Google Play vitals/crashes: https://support.google.com/googleplay/android-developer/answer/9859174
- Android logcat: https://developer.android.com/tools/logcat
- Kimi Code approval modes: https://www.kimi.com/code/docs/en/guides/interaction
- Kimi Code read-only explore agent: https://moonshotai.github.io/kimi-code/en/customization/agents

**Status at creation: Collaboration brief only. Not proof of a Kimi link, a successful build, or an app repair.**
