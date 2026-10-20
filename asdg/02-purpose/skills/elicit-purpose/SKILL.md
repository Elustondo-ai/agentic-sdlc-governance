---
name: asdg-elicit-purpose
description: "Purpose Agent: clarify purpose and desired outcomes, in read-only evaluation."
---

# Elicit Purpose

Owner: `ASDG-02`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure

1. Clarify the desired outcome before discussing implementation.
2. Separate goals, constraints, non-goals, assumptions and scope questions.
3. Suggest observable acceptance questions without choosing the architecture.
4. Return a purpose proposal and unresolved human decisions.

## Output and checks

Use the owner's output contract and separate Intended, Actual and Planned with evidence and decision status.
Canonical identities and Purpose paths follow the catalogue; legacy identities exist only in migration records.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
