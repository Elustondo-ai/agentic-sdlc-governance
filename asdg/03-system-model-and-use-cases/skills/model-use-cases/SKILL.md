---
name: asdg-model-use-cases
description: "System Model and Use Cases Agent: define an overall UML use-case model with linked illustrated scenarios, with project-documentation authoring."
---

# Model Use Cases

Owner: `ASDG-03`; [entry point](../../AGENTS.md); [contract](../../types/contract.md).
Evaluation and documentation procedure. It does not activate a role or grant application execution authority.
Read the owner's contract and shared runtime rules before applying this procedure.
A non-owning caller may inspect the method, but must not use it to bypass role boundaries.

## Procedure

1. Identify actors, system boundaries and domain concepts from supplied context and intent.
2. Describe the overall system in one document using a UML use-case diagram; retain a readable diagram and editable source, such as PlantUML.
3. Select a few representative scenarios and describe each in a separate document linked to its use case or flow. Follow the owner's deliverable contract; do not impose a fixed scenario count.
4. Illustrate each scenario with a picture or short storyboard that explains the interaction. When image generation is authorized, use the available image-generation workflow; create UML diagrams with deterministic diagram tools and retain their source.
5. Check actors, boundaries, scenario terms and UML relationship meanings against one another. Distinguish desired behavior from evidenced capabilities and selected next work; surface ambiguities without prescribing implementation architecture.
6. For authorized saved artifacts, embed the pictures, link the overall model and scenarios in both directions, and inspect rendered readability and image accuracy. If a picture cannot be produced, report the gap rather than describing it as delivered.
7. Return the linked overall model and scenario package, or its conversation proposal within the active permissions. The required output format does not grant file writes, external actions or lifecycle acceptance.

## Output and checks

Use the owner's output contract and identify facts, assumptions and unavailable evidence.
Do not claim tests, review, routing or implementation happened unless observed.
Save substantive documentation within the role's owned directory and return its links; no application execution or external actions follow from authoring.
Out-of-scope work returns to the coordinator; missing prerequisites are reported as blocked.
This YAML-first file records AI modification, not whole-file human approval.

Before declaring a substantive Markdown deliverable complete, identify its embedded explanatory visual, the idea it conveys and the rendering check performed; missing or uninspected visuals must be reported as a documentation gap.
An ordinary criteria table, status table or decorative image does not replace a diagram of behavior, relationships or evidence; navigation-only pages and immutable source archives retain the shared exceptions.

Apply [central ownership and pre-write checks](../../../00-governance/docs/write-controls.md) before saving; propose or hand off changes to another owner.
