---
name: asdg-specify-design
description: "Low-Level Design Agent: specify design, with project-documentation authoring."
---

# Specify Design

Owner: `ASDG-08`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Evaluation and documentation procedure. It does not activate a role or grant application execution authority.
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
Save substantive documentation within the role's owned directory and return its links; no application execution or external actions follow from authoring.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.

Before declaring a substantive Markdown deliverable complete, identify its embedded explanatory visual, the idea it conveys and the rendering check performed; missing or uninspected visuals must be reported as a documentation gap.
An ordinary criteria table, status table or decorative image does not replace a diagram of behavior, relationships or evidence; navigation-only pages and immutable source archives retain the shared exceptions.

Apply [central ownership and pre-write checks](../../../00-governance/docs/write-controls.md) before saving; propose or hand off changes to another owner.
