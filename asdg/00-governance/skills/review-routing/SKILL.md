---
name: asdg-review-routing
description: "ASDG Coordinator: review routing and approval prerequisites, with project-documentation authoring."
---

# Review Routing

Owner: `ASDG-COORDINATOR`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Evaluation and documentation procedure. It does not activate a role or grant application execution authority.
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
Save substantive documentation under the client's `docs/` and return its links; no application execution or external actions follow from authoring.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.

Before declaring a substantive Markdown deliverable complete, identify its embedded explanatory visual, the idea it conveys and the rendering check performed; missing or uninspected visuals must be reported as a documentation gap.
An ordinary criteria table, status table or decorative image does not replace a diagram of behavior, relationships or evidence; navigation-only pages and immutable source archives retain the shared exceptions.
