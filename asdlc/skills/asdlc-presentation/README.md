AI-MODIFIED - 2026-10-08T23:34Z

# Presentation capability — v0.2

Create and maintain source-first presentations, and build viewable PowerPoint exports in place.

| Location | Responsibility |
| --- | --- |
| `SKILL.md` | Agent procedure, scope, and reporting requirements. |
| `docs/presentation-standard.md` | The output contract shared by humans and agents. |
| `docs/building.md` | Setup, commands, supported formats, and reproducibility limits. |
| `types/contracts.py` | Typed slide input, build result, and validation error. |
| `src/sources.py` | Validate visuals and ordered note parts; separate narration from metadata. |
| `src/export.py` | Render sources; assemble and verify PPTX; write local outputs. |
| `src/build.py` | Command-line entry point. |
| `tests/test_build.py` | Baseline source and output contract tests. |
| `tests/test_narration.py` | Ordered segments, profiles, and preservation tests. |

An intro uses one notes file; a detailed version adds a walkthrough and optional explanation.
Type notation is a component choice, not an ASDLC-wide Python requirement; Markdown and other suitable languages are allowed.

This component has the agreed `docs/`, `types/`, `src/`, and `tests/` structure.
There are no independent subcomponents in this first version; the table locates its internal modules.
The small `.agents/skills/asdlc-presentation/SKILL.md` entry is a regular-file adapter for Drive synchronization.
It references this canonical package; no symlink or second editable standard is required.
Native Codex discovery has not been exercised in this execution environment.

## Review and limitations

This package is an AI-authored implementation for human review, not a mature approved methodology.
The SKILL files retain required YAML front matter. Their whole-file approval remains unrecorded while the status-surface conflict is unresolved.
SVG is implemented and tested. PlantUML/Mermaid adapters and PDF export are future capabilities.
Rendering and structure checks do not establish semantic correctness or human understanding.
