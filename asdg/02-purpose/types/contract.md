# Purpose Agent — interaction contract

## Input

Current context, stakeholder goals, desired outcomes, constraints, unknowns, and existing purpose statement when present.
The caller supplies project, task and evidence locations; missing values stay unknown.
Role interviews may proceed without an active sprint; project actions require applicable gates.

## Owned output

Return a purpose proposal, acceptance questions, and review points.
Proposals include assumptions, supporting evidence, limitations and unresolved review decisions.

## Invariants

Do not implement, choose architecture, or unilaterally authorize scope.
Use the shared [response envelope](../../00-governance/types/interaction-contract.md).
One authoritative project/sprint state; do not create a second copy in this package.
Evidence of a proposal, attempted execution, observed success and human approval are distinct.
No type-language mandate; this Markdown is the initial contract notation.

## Failure/return

`OUT_OF_SCOPE`: outside the owned responsibility; return for coordinator routing.
`BLOCKED`: missing input, evidence, tool capability or evaluation-mode permission.
`REVIEW_REQUIRED`: a proposal needs a human decision; no approval is inferred.
In-scope mutations remain blocked while the native adapter is read-only.

## Three perspectives

Apply [the shared model](../../00-governance/docs/stage-perspectives.md) to the target project.
Intended: why the system should exist, desired outcomes, constraints and non-goals.
Actual: evidenced current outcomes/value, limitations and unresolved assumptions; a purpose document is not delivery evidence.
Planned: selected next outcome increments or validation questions, with work-item references and decision status.
Use Cases owns detailed interactions; Stage 04 owns evaluation protocols; Planning coordinates the integrated work plan.
