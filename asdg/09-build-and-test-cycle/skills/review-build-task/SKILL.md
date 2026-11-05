---
name: asdg-review-build-task
description: "Build and Test Agent: review build task, with project-documentation authoring."
---

# Review Build Task

Owner: `ASDG-09`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Evaluation and documentation procedure. It does not activate a role or grant application execution authority.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure

1. Inspect the named task, scope, governing design and available approval evidence.
2. Check the approved component task, active sprint, scope and acceptance criteria before each implementation target; otherwise return the proposed changes without executing writes.
3. Flag missing design or authorization and any work outside the named component.
4. Within existing execution permissions, implement and test the approved bounded task; otherwise return a proposed approach. Claim only observed coding and test results.

## Output and checks

Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
Save substantive documentation within the role's owned directory and return its links; no application execution or external actions follow from authoring.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.

Before declaring a substantive Markdown deliverable complete, identify its embedded explanatory visual, the idea it conveys and the rendering check performed; missing or uninspected visuals must be reported as a documentation gap.
An ordinary criteria table, status table or decorative image does not replace a diagram of behavior, relationships or evidence; navigation-only pages and immutable source archives retain the shared exceptions.

Apply [central ownership and pre-write checks](../../../00-governance/docs/write-controls.md) before saving; propose or hand off changes to another owner.
