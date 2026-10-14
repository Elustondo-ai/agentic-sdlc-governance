AI-MODIFIED - 2026-10-14T19:27:16Z

# ASDLC Baseline Capture — Correction Report R01

Historical R01 report: R02 required further fixes; see the [current R02 correction report](baseline-correction-report-r02.md).
Branch `main`; original checkpoint and unchanged HEAD: `e40152c7f9e9c196fbcfa2f2e6f296ecee118eae`.
Starting tree was clean and its diff against that checkpoint was empty. All corrections remain uncommitted.

## Required corrections
| Finding | Disposition and verified correction |
| --- | --- |
| P1-A | Fixed: canonical README, stale 10–12 adapters, flat 11/12 migration and overlong installer guide. Full suite passes. |
| P1-B | Fixed: complete 11/12 packages, separate responsibilities, specialized shared-skill references, contracts and acceptance cases. |
| P1-B metadata | Quoted invalid role-skill YAML descriptions; validator rejects reserved unquoted syntax and duplicate metadata. |
| P1-C | Fixed: explicit child/tool environment whitelists; 12 synthetic secret/injection variables excluded. Persisted login retained. |
| P1-D | Plan prepared: consumer is now committed post-trial; propose a pinned method worktree plus fresh consumer, preserving all evidence. |
| P2-A | R01 checks passed; R02 found unsupported citation forms bypassed validation. Superseded by the linked R02 correction. |
| P2-B | Fixed: logs/receipts distinguish role-loaded Codex processes, emitted sessions, ownership and self-reports; no native activation claim. |
| P2-C | Fixed documentation: text-only reader excludes binary images/VCS history. New ingestion/history subsystems explicitly deferred. |

## Fresh verification
| Check | Exit | Observed result |
| --- | --- | --- |
| Focused baseline suite (Python 3.15) | 0 | 28 passed; 0 failed/errored/skipped |
| Entire governance suite (Python 3.11) | 0 | 151 run: 148 passed, 3 opt-in native skips; 0 failed/errored |
| Agent package suite | 0 | 17 passed; all 13 actual packages load |
| Package structural validator | 0 | 13 roles/adapters valid; zero reported issues |
| In-memory compilation / 3.9 grammar | 0 | 26 governance Python files checked |
| CLI help / baseline help / diff check | 0 | Each passed; counts not applicable |
| Consumer verify / dry-run / sprint status | 0 | Structure valid; 22 files, one .git exclusion, 12 available stages; inactive sprint |
| Consumer implementation guard, app.py | 1 | Expected IMPLEMENTATION BLOCKED / No active ASDLC sprint is defined. |
| Persisted Codex login under restricted env | 0 | ChatGPT login available; nonfatal PATH-alias permission warning; no model invoked |

[Exact commands, counts and outcome files](../../../docs/reviews/asdlc-baseline-correction-r01/verification.json).
[Complete changed-file list and diff summary](../../../docs/reviews/asdlc-baseline-correction-r01/changed-files.json).
[All feature/package changes versus checkpoint](../../../docs/reviews/asdlc-baseline-correction-r01/corrections.patch).
The initial suite reproduced 13 errors; current green results are fresh executions, not historical claims.
Focused tests include real child-environment probes, positive provenance formats and negative promotion/ownership/path checks.
All baseline orchestration tests in this pass use offline doubles. No new live specialists or baseline capture ran.

## Preservation, checkpoint and limits
Consumer: clean main at `a7411af03bfe87c417d631224f8d9737a7777fbc`, 52 tracked, zero untracked; one local commit.
Both earlier run receipts, seven invocation logs and specialist/Coordinator artifacts remain unchanged.
[Integrity evidence](../../../docs/reviews/asdlc-baseline-correction-r01/integrity.json) verifies complete consumer/legacy byte/link inventories before versus after, including protected sprint files.
[Proposed checkpoint commands](baseline-checkpoint-plan-r01.md) require approval and have not run; no current repository commit/push/deploy was performed.
[Environment/provenance/execution limits](baseline-validation-r01.md); [text-reader scope](baseline-source-scope.md).
Environment-only API/token authentication is unsupported; native discovery/behavior and a final live run remain unverified in R01.
Path existence is verified; factual truth, passage anchors, diagram meaning and the 45/75 versus 25/35 discrepancy require review.
Implementation gate, inactive consumer sprint, hook trust and historical evidence remain intact. No PME approval was added.
STOPPED for R02 review; no checkpoint Git operations or further baseline experiment are authorized by this report.
