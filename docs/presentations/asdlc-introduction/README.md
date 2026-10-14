AI-MODIFIED - 2026-10-08T23:34Z

# ASDLC introduction

The original presentation source content is preserved. Folder numbers express presentation order.
Status: existing introduction baseline selected by Pablo; no new whole-file approval recorded.

[Open the generated PowerPoint](build/asdlc-introduction.pptx) · [Preview](build/preview.png) · [Build evidence](build/build-manifest.json)
Generated links work in the local/Drive working copy after building; these artifacts are deliberately absent from Git.

[Open version 2 — detailed PPTX](build/asdlc-introduction-detailed.pptx) · [Complete detailed narration](build/asdlc-introduction-detailed-notes.md)
Version 2 keeps all visuals and introductory notes unchanged, adding a walkthrough and examples for every slide.
The numbered narration files are read in this order: introduction → walkthrough → details.
The detailed version is an AI-authored review draft, not yet human-approved and not a regenerated Google Vids video.
[Coverage and verification](narration-review.md) · Full narration is approximately 57–66 minutes at 150–130 words/minute.

## Slides

| # | Slide source | Introduction | Walkthrough | Details |
| --- | --- | --- | --- | --- |
| 01 | [Slide 1 — SDLC as Code](01-sdlc-as-code/01-SDLC-as-Code.svg) | [Read](01-sdlc-as-code/speaker-text.md) | [Read](01-sdlc-as-code/speaker-notes-02-walkthrough.md) | [Read](01-sdlc-as-code/speaker-notes-03-details.md) |
| 02 | [Slide 2 — Human–Agent Peer Programming](02-human-agent-peer-programming/02-Human-Agent-Peer-Programming.svg) | [Read](02-human-agent-peer-programming/speaker-text.md) | [Read](02-human-agent-peer-programming/speaker-notes-02-walkthrough.md) | [Read](02-human-agent-peer-programming/speaker-notes-03-details.md) |
| 03 | [Slide 3 — Why Specs Now?](03-why-specs-now/03-Why-Specs-Now.svg) | [Read](03-why-specs-now/speaker-text.md) | [Read](03-why-specs-now/speaker-notes-02-walkthrough.md) | [Read](03-why-specs-now/speaker-notes-03-details.md) |
| 04 | [Slide 4 — AI Changed the Economics of Specifications](04-economics-of-specifications/04-Economics-of-Specifications.svg) | [Read](04-economics-of-specifications/speaker-text.md) | [Read](04-economics-of-specifications/speaker-notes-02-walkthrough.md) | [Read](04-economics-of-specifications/speaker-notes-03-details.md) |
| 05 | [Slide 5 — Agents Cannot Read Our Minds](05-agents-need-context/05-Agents-Need-Context.svg) | [Read](05-agents-need-context/speaker-text.md) | [Read](05-agents-need-context/speaker-notes-02-walkthrough.md) | [Read](05-agents-need-context/speaker-notes-03-details.md) |
| 06 | [Slide 6 — Human Review at Agent Speed](06-human-review/06-Human-Review.svg) | [Read](06-human-review/speaker-text.md) | [Read](06-human-review/speaker-notes-02-walkthrough.md) | [Read](06-human-review/speaker-notes-03-details.md) |
| 07 | [Slide 7 — Code Needs a Dashboard](07-code-needs-a-dashboard/07-Code-Needs-a-Dashboard.svg) | [Read](07-code-needs-a-dashboard/speaker-text.md) | [Read](07-code-needs-a-dashboard/speaker-notes-02-walkthrough.md) | [Read](07-code-needs-a-dashboard/speaker-notes-03-details.md) |
| 08 | [Slide 8 — From Code-Centric to Structured Knowledge](08-structured-knowledge/08-Structured-Knowledge.svg) | [Read](08-structured-knowledge/speaker-text.md) | [Read](08-structured-knowledge/speaker-notes-02-walkthrough.md) | [Read](08-structured-knowledge/speaker-notes-03-details.md) |
| 09 | [Slide 9 — Project Memory Connects the Work](09-project-memory/09-Project-Memory.svg) | [Read](09-project-memory/speaker-text.md) | [Read](09-project-memory/speaker-notes-02-walkthrough.md) | [Read](09-project-memory/speaker-notes-03-details.md) |
| 10 | [Slide 10 — Two Cycles, One Product Roadmap](10-two-cycles-and-product-roadmap/10-Two-Cycles-and-Product-Roadmap.svg) | [Read](10-two-cycles-and-product-roadmap/speaker-text.md) | [Read](10-two-cycles-and-product-roadmap/speaker-notes-02-walkthrough.md) | [Read](10-two-cycles-and-product-roadmap/speaker-notes-03-details.md) |
| 11 | [Slide 11 — AI Works Best Inside the Loop](11-agents-inside-the-loop/11-Agents-Inside-the-Loop.svg) | [Read](11-agents-inside-the-loop/speaker-text.md) | [Read](11-agents-inside-the-loop/speaker-notes-02-walkthrough.md) | [Read](11-agents-inside-the-loop/speaker-notes-03-details.md) |
| 12 | [Slide 12 — Vibe, POC, and Production](12-vibe-poc-and-production/12-Vibe-POC-and-Production.svg) | [Read](12-vibe-poc-and-production/speaker-text.md) | [Read](12-vibe-poc-and-production/speaker-notes-02-walkthrough.md) | [Read](12-vibe-poc-and-production/speaker-notes-03-details.md) |
| 13 | [Annex R01 — Design Docs Are All You Need](13-r01-design-docs-are-all-you-need/R01-Design-Docs-Are-All-You-Need.svg) | [Read](13-r01-design-docs-are-all-you-need/speaker-text.md) | [Read](13-r01-design-docs-are-all-you-need/speaker-notes-02-walkthrough.md) | [Read](13-r01-design-docs-are-all-you-need/speaker-notes-03-details.md) |

## Build

From the repository root:
```sh
python3 asdlc/skills/asdlc-presentation/src/build.py --presentation docs/presentations/asdlc-introduction
python3 asdlc/skills/asdlc-presentation/src/build.py --presentation docs/presentations/asdlc-introduction --narration detailed
```

[Shared standard](../../../asdlc/skills/asdlc-presentation/docs/presentation-standard.md) · [Back to collection](../README.md)
The build preserves proportions, embeds narration, and does not edit source files.
Slides 01–04 are inherited raster-backed SVGs; converting them needs separate source review.
