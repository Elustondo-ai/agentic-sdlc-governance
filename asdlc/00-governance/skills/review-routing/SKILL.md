---
name: asdlc-review-routing
description: ASDLC Coordinator: review routing and approval prerequisites, in read-only evaluation.
---
AI-MODIFIED - 2026-10-10T04:17:45Z

# Review Routing

Owner: `ASDLC-COORDINATOR`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure
1. Read the request and identify whether it is a role interview or a proposed project action.
2. Consult the agent catalogue; only the coordinator chooses the relevant specialist.
3. Read supplied sprint-state and approval evidence; mark missing information, never invent it.
4. Return the routing proposal, bounded assignment, missing prerequisites and human decision points.

## Output and checks
Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
