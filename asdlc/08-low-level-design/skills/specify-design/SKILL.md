---
name: asdlc-specify-design
description: Low-Level Design Agent: specify design, in read-only evaluation.
---
AI-MODIFIED - 2026-10-10T04:17:45Z

# Specify Design

Owner: `ASDLC-08`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure
1. Read governing architecture and the affected component responsibilities.
2. Specify inputs, outputs, invariants, error cases and collaborator expectations.
3. Use a fitting notation, including Markdown; do not mandate a programming language.
4. Return low-level design proposals and review questions without changing production code.

## Output and checks
Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
