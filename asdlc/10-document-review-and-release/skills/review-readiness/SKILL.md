---
name: asdlc-review-readiness
description: Document, Review and Release Agent: review readiness, in read-only evaluation.
---
AI-MODIFIED - 2026-10-10T04:17:45Z

# Review Readiness

Owner: `ASDLC-10`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure
1. Identify candidate revision, scope, evidence and whether the reviewer also authored the change.
2. Compare intent and acceptance criteria with implementation claims and observed results.
3. Assess documentation, traceability, reproducibility and remaining human-understanding questions.
4. Return findings and readiness recommendations; do not repair the reviewed code or grant approval.

## Output and checks
Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
