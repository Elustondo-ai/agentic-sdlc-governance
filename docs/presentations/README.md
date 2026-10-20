# ASDG presentation collection

These source folders are the presentation source of truth in `Elustondo-ai/agentic-sdlc-governance`.
Canonical location, content approval, and publication to GitHub are separate states.

| Read in this order | Slides | State | PowerPoint |
| --- | ---: | --- | --- |
| [ASDG introduction](asdg-introduction/README.md) | 13: 12 + R01 | Selected introduction; inherited content preserved. | [Open PPTX](asdg-introduction/build/asdg-introduction.pptx) · [Detailed v2](asdg-introduction/build/asdg-introduction-detailed.pptx) |
| [Formalization Gradient](formalization-gradient/README.md) | 13: 11 + A1–A2 | Review draft; includes the Codex continuation. | [Open PPTX](formalization-gradient/build/formalization-gradient.pptx) |
| [Codex agents, skills and adapters](codex-agent-skills-and-adapters/README.md) | 13 | Technical draft: Codex implementation, Claude and Copilot mappings. | [Open PPTX](codex-agent-skills-and-adapters/build/codex-agent-skills-and-adapters.pptx) · [Detailed](codex-agent-skills-and-adapters/build/codex-agent-skills-and-adapters-detailed.pptx) |
| [Agentic AI](agentic-ai/README.md) | 7 | Review draft; development-time and runtime agents. | [Open PPTX](agentic-ai/build/agentic-ai.pptx) |
| [Spec-Driven Development deep dive](spec-driven-development-deep-dive/README.md) | 1: R02 | Separate research-reference slide. | [Open PPTX](spec-driven-development-deep-dive/build/spec-driven-development-deep-dive.pptx) |

**PPTX files appear after a build.** The links above open each presentation’s local `build/` output when available. Generated files are not stored in Git, so these links require a built working copy.

## How to navigate

Each presentation README links directly to every original visual and its Markdown narration.
Each numbered slide folder contains one visual and one to three ordered narration files.
The introduction now offers a second, detailed version: original intro → visual walkthrough → examples and explanation.
Existing descriptive SVG filenames and `speaker-text.md`/`speaker-notes.md` names remain unchanged.
The folder number is slide order, not an SDLC stage.
Each presentation owns a local `build/` containing its PowerPoint, preview, and build manifest.
Build output is deliberately excluded from Git; it is recreated from the source files and shared tooling.

## Shared capability

The [presentation skill](../../asdg/skills/asdg-presentation/README.md) is defined in the methodology implementation.
Follow its [standard](../../asdg/skills/asdg-presentation/docs/presentation-standard.md) and [build instructions](../../asdg/skills/asdg-presentation/docs/building.md).
No existing PPTX or PDF is required to rebuild the decks.

## Retained boundaries

Migration preserved the source visuals, narration, references, and existing review markers.
Four introduction SVGs are raster-backed exceptions; their appearance has not been replaced.
Formalization/Codex and runtime-agent examples remain proposals where their source says so.
The source slide vocabulary is not automatically a verified native Codex implementation.
Review the [wrap-up](../status/2026-10-08-wrap-up.md) before adopting further methodology components.
