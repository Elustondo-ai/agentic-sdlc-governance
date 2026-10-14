---
name: asdlc-analyze-context
description: Context and Domain Agent: analyze context, in read-only evaluation.
---
AI-MODIFIED - 2026-10-10T04:17:45Z

# Analyze Context

Owner: `ASDLC-01`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure
1. Inventory stakeholder statements, terms, boundaries, environment and constraints.
2. Separate observed facts, source claims, assumptions and unresolved questions.
3. Map terminology and conflicting statements without silently choosing a preferred interpretation.
4. Return a concise context proposal with sources and questions for review.

## Output and checks
Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
