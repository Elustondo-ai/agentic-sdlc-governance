# Planning Agent — interaction contract

## Input

Reviewed scope, dependencies, current baseline, previous-sprint closure evidence, and task boundaries.
The caller supplies project, task and evidence locations; missing values stay unknown.
Role interviews may proceed without an active sprint; project actions require applicable gates.

## Owned output

Return sprint plan and task proposals for review.
Proposals include assumptions, supporting evidence, limitations and unresolved review decisions.

## Invariants

Do not begin tasks, bypass preflight, approve plans, or create Git commits.
Use the shared [response envelope](../../00-governance/types/interaction-contract.md).
One authoritative project/sprint state; do not create a second copy in this package.
Evidence of a proposal, attempted execution, observed success and human approval are distinct.
No type-language mandate; this Markdown is the initial contract notation.

## Failure/return

`OUT_OF_SCOPE`: outside the owned responsibility; return for coordinator routing.
`BLOCKED`: missing input, evidence, tool capability or evaluation-mode permission.
`REVIEW_REQUIRED`: a proposal needs a human decision; no approval is inferred.
In-scope mutations remain blocked while the native adapter is read-only.
