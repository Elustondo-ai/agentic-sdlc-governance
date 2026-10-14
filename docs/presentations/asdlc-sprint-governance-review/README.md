AI-MODIFIED - 2026-10-10T01:00Z

# ASDLC Sprint Governance — Recovered Workflow for Review

**Status:** AI-authored review draft; not PME-approved, no implementation authority.

## Purpose
Recover and visually review earlier SDLC2 sprint gates, branch rules, artifact sequencing, state transitions and human approval semantics before implementing any automation. Source-grounded rules and open decisions are deliberately distinguished.

## Sources
- [workflow](https://drive.google.com/file/d/1GfV1n2aHRMjlL8mkTa_dy_T5j-oLd_rS/view)
- [branch](https://drive.google.com/file/d/1gqL7mg1MCEKg0-Og2Pph4lTxGBNhoGzh/view)
- [sprint_model](https://drive.google.com/file/d/13CAIltdmYgCRmWydYjuXSZQnb_CbC2Ia/view)
- [plan_template](https://drive.google.com/file/d/1d3ByMS9oaXNV3egK0OOZKJ_xlYNC0YXh/view)

## Organization
Eleven numbered slides, each with one SVG and exactly three ordered Markdown narration files. Number is presentation order, not ASDLC lifecycle stage. `build/` contains derived PowerPoints, previews and build metadata; keep it ignored by Git.

## Review decisions
1. Confirm the preflight and sprint branch rule, including the configured integration branch.
2. Reconcile documentation approval by Git commit with visible PME review markers.
3. Confirm the state machine and human-owned transitions.
4. Locate and review the earlier status-transition script before replacement.
5. Decide whether the richer six-document sprint package should become the baseline or a profile.

## Execution boundary
Produce presentation and video artifacts for review only. No agent, branch, commit, push, merge or release authorization is implied. A locally produced Piper MP4 requires executing the installed component in the Mac repository after sources are synchronized.
