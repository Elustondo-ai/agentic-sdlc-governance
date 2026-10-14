---
name: asdlc-presentation
description: Create, maintain, validate, and build ASDLC source-first presentations with numbered slide folders, one editable visual and one to three ordered Markdown narration files per slide, and a presentation-local build directory.
---
AI-MODIFIED - 2026-10-08T23:34Z

# ASDLC presentation

This is the canonical workflow; the `.agents` entry is only a discovery adapter.
Review state: AI-authored draft; no whole-file human approval is recorded.
YAML must remain first. The Registry's Markdown-status conflict remains unresolved; fail closed on approval.

## When to use
Use for creating, editing, reviewing, packaging, or rebuilding presentations in an ASDLC project.

## Procedure
1. Read [the standard](docs/presentation-standard.md), the selected presentation README, and the requested source material.
2. Confirm the requested operation and scope. Preserve the source's meaning, slide order, original IDs, and review state.
3. For authored changes, prepare one numbered folder per slide: one visual source and an introduction, with optional walkthrough and details files.
4. For a detailed version, explain every meaningful visual element and relationship, not only the main idea. Keep existing source names during maintenance. Do not recreate existing visuals or invent missing source content.
5. Follow [build instructions](docs/building.md). Select `intro` or `detailed` explicitly; validate and build in the presentation's own `build/`.
6. Inspect the generated visual preview and PPTX. Check notes, slide order, preserved proportions, and the build manifest.
7. Report actual changes, validation results, raster-backed visuals, unsupported formats, and remaining human review.

## Execution
From the methodology repository root:
```sh
python3 asdlc/skills/asdlc-presentation/src/build.py --all --check
python3 asdlc/skills/asdlc-presentation/src/build.py --all
python3 -m unittest discover -s asdlc/skills/asdlc-presentation/tests -v
```
Use `--presentation <folder>` instead of `--all` for a single presentation.
Add `--narration detailed` to build the longer version without replacing the introductory PPTX.
Read [narration coverage](docs/narration-coverage.md) before writing additional notes.
In a consuming project, resolve this skill's actual installed path; never invent the methodology root.

## Boundaries
Building creates derived files, not approval, staging, a commit, a push, or publication.
Do not alter source meaning to fix a build failure. Surface the failure or ask for a separately reviewed correction.
Versioned sources stay outside `build/`; generated PPTX, previews, and manifests stay inside it.
The v0.2 builder supports SVG and ordered narration profiles. PlantUML/Mermaid rendering is explicitly pending, not silently substituted.
See [component responsibilities](README.md) and [typed contracts](types/contracts.py).
