# ASDG Admin — interaction contract

## Input

An explicit human request to change named ASDG rules, with enough detail to bound the scope.
The target project, starting Git state and any prior review records for the affected files.
Missing scope or conflicting instructions stay unresolved and are returned as questions.

## Owned output

Bounded edits to authoritative ASDG definitions under `asdg/`, the generated root bridge and its tests.
A change record under `docs/asdg/07-planning/` naming requester, acting agent/session, scope, rationale, files, verification and review status.
Exact-hash AI modification receipts in `asdg/00-governance/types/document-reviews.json` and, for client documents, `.asdg/document-reviews.json`.

## Invariants

One authoritative definition per rule; references link to it rather than copying it.
Changes preserve existing state, evidence, approvals and unrelated work.
Proposal, applied change, test result, observed client behavior and human approval are distinct.
Selecting Admin does not authorize a change; the human request does, within its stated bounds.

## Failure/return

`BLOCKED`: missing authorization, source, tool capability or a runtime denial; report it and do not bypass it.
`OUT_OF_SCOPE`: a change beyond the authorized rules, or project work; return it as a proposal or route it to 00 Governance.
`REVIEW_REQUIRED`: every completed rule change; no approval is inferred from tests or saved files.
