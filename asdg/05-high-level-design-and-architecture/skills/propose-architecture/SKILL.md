---
name: asdg-propose-architecture
description: "High-Level Architecture Agent: analyze architecture and document material decisions as short visual packages."
---

# Propose Architecture

Owner: `ASDG-05`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Read [decision foundations](../../docs/architectural-decisions.md) and the shared runtime rules.
This method does not activate a role, authorize implementation, or widen the caller's contract.

## Procedure

1. Reuse the discussion, desired outcomes, actual implementation, evidence, constraints and explicit human choices.
2. Explain the purpose of candidate boundaries, dependency directions, interfaces, ownership and failure behavior before implementation mechanisms.
3. Apply [ASDG Decision](../../../skills/asdg-decision/SKILL.md) to material choices; compare responsibilities fairly and include the current approach when relevant.
4. For assigned documentation, save each material decision using its named folder, short introductions, meaningful option notes and explanatory visuals.
5. Capture scope, consequences, uncertainties, sources and concrete revisit triggers; preserve recommendations separately from selected directions.
6. For analysis-only requests, provide the useful comparison without creating files or a new approval flow.

## Output and checks

Use the owner's output contract and its bounded documentation allowance; no application-code changes.
Cover deployment, data, ownership, reliability and interaction patterns as well as products.
Adapt the [worked example](../../../skills/asdg-decision/example.md); never inherit its provider, option count or client-specific requirements.
Validate links and source size; inspect every new/changed visual embedded at document width and representative complete pages.
Record exact hashes and visual-review evidence under the shared documentation standard; report missing checks specifically.
Do not claim tests, handoffs, implementation or formal acceptance without evidence.
