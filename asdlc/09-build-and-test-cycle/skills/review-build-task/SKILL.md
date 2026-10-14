---
name: asdlc-review-build-task
description: "Build and Test Agent: review build task, in read-only evaluation."
---
AI-MODIFIED - 2026-10-14T16:22:04Z

# Review Build Task

Owner: `ASDLC-09`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure
1. Inspect the named task, scope, governing design and available approval evidence.
2. Explain intended code changes and tests without executing writes in this evaluation.
3. Flag missing design or authorization and any work outside the named component.
4. Return a proposed implementation approach, not a claim that coding or tests happened.

## Output and checks
Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
