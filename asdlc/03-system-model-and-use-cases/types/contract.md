AI-MODIFIED - 2026-10-10T04:17:45Z

# System Model and Use Cases Agent — interaction contract

## Input
Context and intent, actors, boundaries, scenarios, interactions, and expected observable outcomes.
The caller supplies project, task and evidence locations; missing values stay unknown.
Role interviews may proceed without an active sprint; project actions require applicable gates.

## Owned output
Return model and use cases with open ambiguities.
Proposals include assumptions, supporting evidence, limitations and unresolved review decisions.

## Invariants
Do not implement or dictate low-level architecture.
Use the shared [response envelope](../../00-governance/types/interaction-contract.md).
One authoritative project/sprint state; do not create a second copy in this package.
Evidence of a proposal, attempted execution, observed success and human approval are distinct.
No type-language mandate; this Markdown is the initial contract notation.

## Failure/return
`OUT_OF_SCOPE`: outside the owned responsibility; return for coordinator routing.
`BLOCKED`: missing input, evidence, tool capability or evaluation-mode permission.
`REVIEW_REQUIRED`: a proposal needs a human decision; no approval is inferred.
In-scope mutations remain blocked while the native adapter is read-only.
