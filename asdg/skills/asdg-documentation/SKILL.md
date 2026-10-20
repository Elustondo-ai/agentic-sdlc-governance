---
name: asdg-documentation
description: Write readable ASDG project documentation with evidence, compact topics and useful visuals; validate source structure and rendered readability.
---

# ASDG documentation

Write for the person who needs to understand the project, its evidence and its open decisions.
Follow the [shared documentation standard](../../00-governance/docs/documentation-standard.md).

## Workflow

1. Read the existing topic and evidence. Preserve meaning, uncertainty and proposal status.
2. Open with a meaningful title and explanation. Use paragraphs, headings and well-spaced lists.
3. Keep units within 50 nonblank source lines; blank and whitespace-only lines do not count.
4. Use the shared Python counter; never remove useful spacing or compress paragraphs to evade the limit.
5. Split oversized units by topic and preserve navigation. Start with existing artifacts.
6. Distinguish observed behavior, documented claims and inference in normal prose.
7. Retain evidence links, baseline dates, limitations, open decisions and commitment status.
8. Preserve review events against old hashes before marker removal; record edited bytes separately.
9. Inspect representative source and rendered documents. Report actual checks and their limits.

## Visuals and sources

Use a visual when it explains a relationship or concrete context.
An established visual-and-notes topic keeps its original source structure and filenames.
Choose domain-appropriate notation; do not add a visual merely to satisfy a template.
Keep editable sources in topic folders and derived exports in `build/`.
[Presentations](../asdg-presentation/SKILL.md) may derive slides; they do not replace source documents.
See the [readable assessment example](example.md).

## Evidence and review

Use Intended / Actual / Planned in substantive assessments of the explicit target project.
Technical provenance belongs in the standard's JSON records, not repeated labels in the prose.
Do not invent measurements, tests, approval, deployment or user acceptance.
Keep historical execution evidence intact rather than rewriting it as new observations.
Preserve YAML-first syntax; human approval requires an explicit exact-state decision.
