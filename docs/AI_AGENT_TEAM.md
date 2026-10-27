# CROWNFALL AI agent team — working plan (2026-10-27)

**Status:** Team instructions staged for review, not a claim that autonomous independent agents or Unreal builds are running. Authoritative blocker: issue #3.

## Workstreams and deliverables
| Workstream | First input | Deliverable | Requires |
|---|---|---|---|
| Coordinator | issue #3, current branch, CI | prioritized evidence queue | repo access |
| Codex / source audit | source tree and historical CI | diff/PR with narrow corrections | isolated branch |
| Unreal map recovery | failing historical `TestMap.umap` SHA + M84/M106 provenance | UE Editor load + genuine Cook logs | licensed Unreal sandbox and authentic map |
| Android forensics | exact installed versionCode + real device logs | first fatal exception/stack + reproduction | authorized device/test environment |
| QA / independent review | genuine build and device logs | pass/fail matrix with linked artifacts | no mocks as substitutes |
| Release | tested package >218 | internal-track review checklist | successful device launch + user approval |

## First coordinated investigation
1. Inspect repo and issue #3. Keep diagnosis distinct from tentative hypotheses.
2. Determine whether actual UE project assets/build sources are present; identify missing inputs exactly.
3. Gather existing historical CI artifacts where available, compare SHA fingerprints without touching originals.
4. Draft scripts or checklists to collect authorized, redacted Android logs and installed versionCode. Never request passwords or a private JKS.
5. Implement reversible improvements on a separate branch and record what each test **does not** establish.
6. Report blockers openly. Do not perform production deployment, publish to Google Play or merge to main automatically.

## Progress report format
- **Evidence:** reproducible links and artifact names.
- **Status:** not verified / static-only / real UE build / Android runtime proven.
- **Next smallest test:** input needed, estimated environment, acceptance result.
- **Safety:** no leaked secrets, no main mutations, no unapproved cloud spending.

This plan deliberately does not discuss unrelated confidential physics research in the public repository.
