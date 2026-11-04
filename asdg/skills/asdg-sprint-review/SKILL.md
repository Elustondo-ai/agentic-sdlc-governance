---
name: asdg-sprint-review
description: Review an ASDG sprint against its objective, scope and acceptance criteria using current evidence. Reports completed, failed and unverified work without closing the sprint or recording acceptance.
---

# Review an ASDG sprint

Give the user an evidence-based account of what the sprint achieved and what remains.
Read client instructions, [session policy](../asdg-focus/session-policy.md) and [the sprint state contract](../../00-governance/docs/sprint-state.md).
Resolve the client root as `../../..` from this canonical skill directory; preserve Focus and authoritative state.
This is a read-only review. It neither assigns a new specialist nor authorizes fixes, approvals or closure.

## Bind the review

Run `python3 asdg/scripts/cli.py status --json` and `python3 asdg/scripts/cli.py sprint status --json`; inspect `git status --short`.
Review the active sprint unless the user identifies a historical one. If none is active, say so; do not create a sprint.
For historical review, use the explicitly identified snapshot or [closeout record](../asdg-sprint-close/recording.md); never guess a past objective from current files.
Retain the exact sprint definition and its SHA-256, observation time, inspected revision and relevant working-tree changes.
Inspect the scoped implementation, companions, tests and available execution evidence needed to assess its criteria.
Use an observed start revision when available. Without one, disclose that Git differences alone cannot identify which changes belong to this sprint.
Existing uncommitted work does not by itself prevent review; do not attribute authorship from filenames.
Preserve the user's deferrals and benchmark references. Missing unrelated lifecycle stages do not automatically fail this sprint.

## Assess the evidence

For each acceptance criterion return `PASS`, `FAIL` or `UNVERIFIED`, the supporting evidence and any gap.
A source inspection supports implementation claims; runtime behavior requires observed execution evidence appropriate to the claim.
Distinguish reproducible commands, attempted runs, passing tests, human acceptance and delivered user benefit.
Reuse valid test evidence; inspect its revision and environment. Do not call stale or simulated results current production evidence.
Do not execute tests, make API calls or modify files merely because this review skill was invoked; retain separately authorized execution boundaries.
Report scope deviations, regressions, missing documentation and operational limitations only where supported by evidence.
Keep ordinary unfinished work separate from technical debt, and name any missing owner or decision without inventing one.
Disclose shared authorship; a new role label or chat does not establish an independent review.

## Return a closure recommendation

Lead with the objective, achieved behavior and important gaps; include a compact criterion/evidence/result table.
All criteria passing supports a recommendation to close as completed; any failure or unknown supports an unfinished outcome.
An explicit human decision may still end an unfinished sprint. A closure recommendation never performs that transition.
List bounded carry-forward items and any explicit human acceptance separately; do not create another sprint or competing plan.
Return the review in the conversation. Only an explicitly requested close uses the close skill's durable receipt.
If the sprint definition changes during review, refresh the affected assessment rather than applying results to a different scope.
Report missing evidence or denied reads precisely. Keep the current sprint active and its files unchanged.
