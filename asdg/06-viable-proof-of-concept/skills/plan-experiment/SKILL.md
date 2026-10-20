---
name: asdg-plan-experiment
description: "Viable POC Agent: plan experiment, in read-only evaluation."
---

# Plan Experiment

Owner: `ASDG-06`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure

1. Name the uncertainty that the experiment should resolve.
2. Define a bounded procedure, inputs, expected observations and stop conditions.
3. Identify execution, installation, service-cost and environment permissions that would be required.
4. In this read-only evaluation return the plan only; distinguish prior measurements from proposed tests.

## Output and checks

Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
