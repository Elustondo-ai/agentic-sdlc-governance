AI-MODIFIED - 2026-10-14T19:28:22Z

# ASDLC Baseline Capture — Correction Report R02

Recommendation: **READY FOR INDEPENDENT RE-REVIEW**, pending acceptance before checkpointing.
Branch `main`; unchanged HEAD: `e40152c7f9e9c196fbcfa2f2e6f296ecee118eae`. All corrections remain unstaged/uncommitted.
R01 evidence remains historical; its manifests describe the R01 state, not these additional changes.

## Corrections
- P2 provenance: reject Markdown reference definitions and full/collapsed references, including escaped/multiline labels and container forms.
- URI/email autolinks outside `Narrative citations:` now fail; explicit narrative citations remain unverified and cannot replace `Sources:`.
- The conservative restriction includes literal examples; the prompt requests inline links and the contract specifies the supported grammar.
- Seventeen negative forms each exercise complete artifact validation and offline child-output promotion; rejected pairs produce no promoted notes or visual.
- P2 acceptance: stages 11 and 12 now expect their own canonical `AGENTS.md`; both remain **NOT RUN** for native evaluation.
- [Lifecycle authority](../../../docs/status/lifecycle-baseline.md) now explicitly identifies this repository's preserved twelve-stage baseline.
- External SDLC2 drift is recorded as reported by R02, unresolved; no external re-evaluation or stage renumbering occurred.

## Fresh verification
| Check | Exit | Observed result |
| --- | --- | --- |
| Focused baseline suite, Python 3.15 | 0 | 31 passed; no failures/errors/skips |
| Complete governance suite, Python 3.11 | 0 | 154 run: 151 passed, 3 opt-in native skips; no failures/errors |
| Package suite | 0 | 17 passed |
| Package structural validator | 0 | All 13 packages/adapters valid |
| In-memory compilation / Python 3.9 grammar | 0 | 26 governance Python files; no claim of a native 3.9 runtime run |
| CLI help / baseline help / diff check | 0 | Each passed |
| Consumer verify / dry-run / sprint status | 0 | 22 eligible files; .git excluded; 12 stages available; inactive sprint |
| Consumer implementation guard, app.py | 1 | Expected IMPLEMENTATION BLOCKED / No active ASDLC sprint is defined. |

[Exact commands, times, counts and outcome files](../../../docs/reviews/asdlc-baseline-correction-r02/verification.json).
[Changed-file hashes and current checkpoint inventory](../../../docs/reviews/asdlc-baseline-correction-r02/changed-files.json).
[Bounded source/documentation diff from the reviewed R01 state](../../../docs/reviews/asdlc-baseline-correction-r02/corrections.patch).
The patch includes prior untracked files as modifications to R01; it is for review, not reapplication to this tree.

## Preservation and remaining boundaries
[Integrity evidence](../../../docs/reviews/asdlc-baseline-correction-r02/integrity.json): all 174 consumer and 98 legacy file/link entries still match R01.
Consumer remains clean at `a7411af03bfe87c417d631224f8d9737a7777fbc`; prior trial artifacts, receipts and logs are preserved.
Retain the [fresh-consumer/pinned-method checkpoint plan](baseline-checkpoint-plan-r01.md); the existing consumer is a post-trial baseline.
Staging review and commit approval remain separate future steps; no staging, checkpoint, commit, push or deployment occurred.
All capture tests used offline doubles; no live capture/model invocation or authentication recheck occurred.
Native discovery, live stages 11/12 and actual revised tool-environment enforcement remain unverified.
[Contract](baseline-validation-r01.md): constrained citation grammar, not comprehensive Markdown/HTML parsing or arbitrary prose-path validation.
File existence does not prove factual truth, passage anchors or visual meaning; external narrative citations remain human-review material.
STOPPED for independent re-review before checkpointing or any new baseline experiment.
