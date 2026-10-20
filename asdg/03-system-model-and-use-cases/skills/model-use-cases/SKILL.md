---
name: asdg-model-use-cases
description: "System Model and Use Cases Agent: model use cases, in read-only evaluation."
---

# Model Use Cases

Owner: `ASDG-03`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Instruction-only evaluation procedure. It does not activate a role or grant write permission.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure

1. Identify actors, system boundaries and domain concepts from supplied context and intent.
2. Describe main scenarios, alternatives, failures and observable outcomes.
3. Check that model terms and use cases agree; surface ambiguities.
4. Return linked model and use-case proposals without low-level implementation decisions.

## Output and checks

Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
In this evaluation, return the result in the conversation; no writes or external actions.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.
