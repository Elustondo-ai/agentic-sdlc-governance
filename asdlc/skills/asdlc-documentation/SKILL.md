---
name: asdlc-documentation
description: Author compact visual-first ASDLC knowledge units for specialist-owned stage documentation; PPTX is only an optional derived build.
---
AI-MODIFIED - 2026-10-14T12:45:00Z

# Visual-first ASDLC documentation

Source documentation is **not** PowerPoint. The canonical unit is a small folder:

```text
01-topic/
  visual.puml     # or .mmd, .svg, .png, .jpg, .webp
  speaker-notes.md
```

## General rules
- One meaningful question/idea per folder; one visual and one explanation.
- Keep each Markdown file to **at most 50 physical lines**. Prefer more small units to longer files.
- The notes identify observed facts, documented claims, inference, contradictions and missing evidence.
- Preserve evidence references, author identity, uncertainty and exact review markers.
- The first nonempty line of newly created *ordinary* Markdown is `AI-MODIFIED - <UTC timestamp>`.
- The skill's YAML front matter must stay first for native parsing; approval of this YAML-first file fails closed.
- Do not add or update `PME-APPROVED` without exact file-state human approval.
- Use diagrams first when meaningful: PlantUML, Mermaid or SVG; use images/screenshots for concrete UI or visual context.
- Choose a visual because it answers a question, not to decorate the document.
- Do not invent tests, measurements, rationale, approval, deployments or user acceptance.
- Canonical editable sources live in stage/topic folders; generated images/decks/previews belong only in `build/`.
- `asdlc-presentation` may later assemble documentation units into PPTX; PPTX is **never** the source.

## Specialist tailoring
- Intent: business-legible outcome and scope diagrams; avoid unnecessary UML.
- Use Cases: actors, activity flows, journeys and conceptual system/domain models.
- Benchmark: measurement diagrams, comparison matrices, evidence/target graphs.
- Architecture: C4, UML components, deployment topology, structural trade-offs.
- Low-Level Design: UML sequence, class, state, responsibility/CRC, contracts; UI mockups where appropriate.
- Build/QA: traceability, test/evaluation evidence, decision and change navigation.
- Operations/Observability: runtime topology, telemetry, feedback and learning loops.

A specialist's local `SKILL.md` chooses domain notation and tools, **by reference** to this shared contract, not by copying it. In baseline capture, record the **as-is** system first; recommendations are separate, clearly labelled.
