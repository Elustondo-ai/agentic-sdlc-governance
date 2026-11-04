---
name: asdg-documentation
description: Write readable ASDG project documentation with evidence, compact topics and useful visuals; validate source structure and rendered readability.
---

# ASDG documentation

Write for the person who needs to understand the project, its evidence and its open decisions.
All reader-facing `docs/asdg/` artifacts follow this rule; authoring instructions belong in the methodology.
Follow the [shared documentation standard](../../00-governance/docs/documentation-standard.md).

## Workflow

1. Read the existing topic and supplied sources. Preserve their useful narrative, meaning, uncertainty and proposal status; keep source archives intact.
2. Open with a meaningful title and explanation. Use paragraphs, headings and well-spaced lists.
3. Keep units within 50 nonblank source lines; blank and whitespace-only lines do not count.
4. Use the shared Python counter; never remove useful spacing or compress paragraphs to evade the limit.
5. Split oversized units by coherent topic and preserve navigation. Put the overall approach before detailed protocols; do not fragment a clear source into harder-to-read summaries.
6. Distinguish observed behavior, documented claims and inference in normal prose.
7. Retain evidence links, baseline dates, limitations, open decisions and commitment status.
8. Preserve review events against old hashes before marker removal; record edited bytes separately.
9. Inspect representative source and rendered documents. Report actual checks and their limits.

## Visuals and sources

Include an embedded visual in each substantive explanation so a reader can grasp the main idea before the prose.
Use the prose as technical speaker notes; navigation indexes and brief appendices may link to an existing visual.
An established visual-and-notes topic keeps its original source structure and filenames.
Choose a diagram, dashboard, scenario picture or CRC table that conveys a relationship; avoid decoration.
For a graphical interface, follow the [GUI visual rule](../../00-governance/docs/gui-visuals.md): who uses it, then a captioned screenshot or labelled mockup.
Keep editable diagram sources with supporting assets such as `images/`; use `build/` when a separate export workflow requires it.
Optional presentation tools may derive slides; they are not included in this core.
See the [readable assessment example](example.md).

## Source companions

For every maintained programming file, follow the [CRC-inspired companion standard](../../00-governance/docs/code-companions.md).
Read the implementation and its callers; explain purpose, responsibilities, types, functions, collaborators and effects.
Cover scripts and tests as well as application/library code; update the companion with interface or behavior changes.

## Evidence and review

Use Intended / Actual / Planned in substantive assessments of the explicit target project.
Follow the [stage layout](../../00-governance/docs/stage-layout.md): flat perspective files, with its named decision-folder exception.
For material decisions, use [ASDG Decision](../asdg-decision/SKILL.md) in the current specialist context and existing authority.
At cycle closeout, consolidate verified outcomes into Current before removing only that completed cycle's plans.
Technical provenance belongs in the standard's JSON records, not repeated labels in the prose.
Do not invent measurements, tests, approval, deployment or user acceptance.
Keep historical execution evidence intact rather than rewriting it as new observations.
Preserve YAML-first syntax; human approval requires an explicit exact-state decision.

Before delivery, check each substantive Markdown file against the shared visual review criteria: embedded visual, explanatory purpose and actual rendering inspection. Report gaps per file; a visual in the README alone is insufficient.
