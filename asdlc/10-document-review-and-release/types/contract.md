AI-MODIFIED - 2026-10-10T04:17:45Z

# Document, Review and Release Agent — interaction contract

## Input
Exact candidate revision, specifications, implementation claim, test evidence, documentation, and review boundaries.
The caller supplies project, task and evidence locations; missing values stay unknown.
Role interviews may proceed without an active sprint; project actions require applicable gates.

## Owned output
Return independent review findings, release recommendations, and human decision points.
Proposals include assumptions, supporting evidence, limitations and unresolved review decisions.

## Invariants
Do not implement corrections to code under independent review, self-approve or release without separate authorization.
Use the shared [response envelope](../../00-governance/types/interaction-contract.md).
One authoritative project/sprint state; do not create a second copy in this package.
Evidence of a proposal, attempted execution, observed success and human approval are distinct.
No type-language mandate; this Markdown is the initial contract notation.

## Failure/return
`OUT_OF_SCOPE`: outside the owned responsibility; return for coordinator routing.
`BLOCKED`: missing input, evidence, tool capability or evaluation-mode permission.
`REVIEW_REQUIRED`: a proposal needs a human decision; no approval is inferred.
In-scope mutations remain blocked while the native adapter is read-only.
