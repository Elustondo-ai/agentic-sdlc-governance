---
name: asdlc-evaluate-alternatives
description: "Benchmark and Test Strategy Agent: evaluate alternatives, in read-only evaluation."
---
AI-MODIFIED - 2026-10-14T16:22:04Z

# Evaluate Alternatives

Owner: `ASDLC-04`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure
1. Identify existing products, integrations, custom options and human-supplied alternatives.
2. Define comparable input material, quality thresholds, cost and execution measures.
3. Separate system alternatives from component-level comparisons and untested predictions.
4. Return an evaluation protocol and evidence-based comparison; building is not the assumed winner.

## Output and checks
Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
