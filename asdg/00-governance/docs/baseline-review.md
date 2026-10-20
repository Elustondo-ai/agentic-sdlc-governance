AI-MODIFIED - 2026-10-14T16:14:00Z

# Baseline capture v0.1.4 — next-agent handoff
Historical pre-R01 handoff; current corrections/results are in [Correction Report R01](baseline-correction-report-r01.md).

Status: **Partially ready; bounded live trial passed; ready for review.** No human approval granted.
Read root AGENTS.md, [contract](baseline-capture.md), [safety](baseline-safety.md) and [tests](baseline-verification.md).
Applied `~/Downloads/asdg-baseline-capture-v0.1.4.patch` after `git apply --check`; never reapplied.
Branch `main`, HEAD `e3f150453976d602123b0032748b958d9b343173`; existing untracked work preserved.
The methodology's pre-existing untracked tree makes ordinary `git diff` incomplete.
Prepatch copies, raw patched copies, exact final diffs and hashes: `/private/tmp/asdg-baseline-review/`.

## Feature files created or modified
- `asdlc/00-governance/src/{cli.py,cli_model.py,cli_baseline.py,cli_baseline_safety.py}`.
- `asdlc/00-governance/tests/test_baseline.py` and `asdlc/skills/asdlc-documentation/SKILL.md`.
- `asdlc/00-governance/docs/baseline-{capture,safety,review,verification}.md`.
- Consumer: AGENTS.md bridge migration, its backup and new `.asdlc/lifecycle.json`, only as required by init.
- Consumer: both runs' baseline docs/logs/receipts plus the successful run's separate source-audit JSON.

## Actual capped trial
Successful run: `20261014T141117Z-e05018921d`; 16 files, eight visual/notes pairs.
Coordinator planned `[1,2,3,4,5,8,10]`; explicit `--max-agents 2` ran `[1,2]` only.
All four separately invoked sessions below completed OK; none is an offline test double.

| Phase | Actual Codex session | Artifact files |
| --- | --- | --- |
| 00-routing | 01a13ac0-d331-71c2-be7d-7a123084f44e | 0 |
| 01 Context | 01a13ac1-b51f-7a63-96d3-ff59bf669010 | 6 |
| 02 Intent | 01a13ac3-8b32-7063-9dc5-3dc2fe81d87e | 4 |
| 00-summary | 01a13ac4-e1f9-7983-9a27-411239d9415b | 6 |

Receipt: [actual invocations, log paths and owner/hash mappings](../../../../agentic-speaker-coach/docs/asdlc/00-governance/logs/20261014T141117Z-e05018921d__baseline-run.json).
Logs: consumer `docs/asdlc/<stage>/logs/<run-id>__baseline-capture__<phase>.md` (15 lines each).
Specialist bytes were promoted unchanged; Coordinator synthesis owns governance documents only.
Earlier failed run `20261014T135454Z-470a8194cc` remains intact; Intent's invalid visual was rejected.
Its receipt/logs preserve all three real sessions and the four valid Context files already published.

## Integrity and review limits
[Separate audit](../../../../agentic-speaker-coach/docs/asdlc/00-governance/logs/20261014T141117Z-e05018921d__source-audit.json): all original 98 legacy files/links unchanged; 22 eligible files/21,170 bytes.
Sprint remains inactive; binding, sprint and hook/config hashes match before preparation.
No application-code import/write, sprint start, hook trust change, Registry edit, approval or Git mutation.
Final SVG/empty-folder checks, root/interaction materials and expanded receipt context were added after the live run.
Published artifacts pass the final validator; those final changes have unit/CLI evidence, not a fresh model trial.
Do not reinterpret synthesis's mid-run RUNNING/null snapshot as the finalized runner receipt.
Visual meaning, calibration claims and 25/35 versus documented 45/75 seconds require human review.
Stages 11/12 lack actual role packages; full twelve-specialist execution was never attempted.
Full suite has 13 pre-existing missing-README errors; see verification. Nothing is self-approved.
Use installed `asdg`: a different Python interpreter makes the existing hook verifier report a mismatch.
Next reviewer command, from methodology root: `python3 -B -m unittest discover -s asdlc/00-governance/tests -p test_baseline.py -v`.
