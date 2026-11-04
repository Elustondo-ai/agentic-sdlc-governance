# Readable project documentation

Documentation helps a person understand a subject, assess its evidence and find useful detail.
This is a mandatory ASDG rule for every adopting project, all twelve specialists, governance and methodology maintenance.
Readability is required in both source Markdown and the rendered document.
Everything in the client's `docs/asdg/` intended for reading has a human audience, including technical material.

## Size and structure

Maximum 50 nonblank source lines per Markdown documentation unit.
Empty lines and whitespace-only lines do not count.
Count source lines containing at least one non-whitespace character, not editor wrapping.
All validators use `documentation.nonblank_source_lines` in the governance Python source.
Preserve paragraph separation, headings, list spacing, code indentation and meaningful formatting.
Do not join paragraphs into giant lines, minify prose or use cryptic fragments to evade the limit.
Split oversized units by coherent topic and preserve navigation.
Derived compilations and technical execution records are not new source documentation units.

## Write for the reader

Open with the project's subject and a useful explanation; avoid agent-role titles and template-filling instructions.
Explain decisions, interfaces, evidence and open questions as engineers would explain them to each other.
Read supplied sources before restructuring; preserve their clear narrative and meaning, keep archives intact and identify added proposals.
Teach the approach first, then link detailed protocols and thresholds; adapt to each project's facts instead of copying another project's assumptions.
Use normal prose to distinguish evidence, documented aspirations, inference and unknowns.
Keep useful evidence links, baseline dates, limitations, open decisions and commitment status.
Keep machine timestamps, run IDs, repeated role labels and tool receipts in technical records.
Use Intended / Actual / Planned in substantive assessments, without labeling every sentence.
Give each substantive explanation a useful embedded visual: a diagram, dashboard, scenario picture or CRC table.
Let the visual convey the main idea at a glance and the prose supply the detail, like speaker notes.
Navigation-only indexes, brief change notes and reference appendices can link to the relevant visual instead.
Keep editable diagram sources and accessible labels; inspect rendering, legibility and technical accuracy.
Review representative rendered documents as well as source. Counting alone cannot certify readability.
Graphical interfaces also require a plain-language opening and a captioned [representative screenshot or labelled mockup](gui-visuals.md).
See the [assessment example](../../skills/asdg-documentation/example.md).
Every maintained programming source file has a [human-readable interface companion](code-companions.md), updated with code changes.
Apply the [documentation review criteria](documentation-review.md); missing or inaccurate explanations remain reported gaps.

## Review history without clutter

This ASDG-scoped exception was authorized on 19 October 2026 and revises the visible-marker preference.
Human prose and hash-bound review events remain separate through the ASDG namespace migration.
It covers ASDG, generated project documentation and the requested Speaker Coach living documents.
It does not change Registry-wide rules or unrelated projects or file formats.
Before removing a marker, record its full declaration and the old document's exact SHA-256 hash.
Record edited bytes as a separate AI modification event, with no inferred human approval.
Use `documentation.review_record` in these technical record areas:

- Provider maintenance: `asdg/00-governance/types/document-reviews.json`.
- Project initialization/living migration: `.asdg/document-reviews.json`.
- Baseline capture: each artifact's `document_review` in the existing baseline-run JSON receipt.
- Coordinator advice: a matching JSON receipt beside the report, retaining the complete runtime result.

Records describe document states; they are neither a competing plan nor a lifecycle state engine.
Legacy approval declarations remain attached only to the recorded old state; they are not reapproved.
New human approval requires an explicit exact-state decision; automated approval fails closed.
Keep historical capture reports, logs, inventories and their review declarations intact.
Preserve YAML-first skill syntax. A source edit, Git commit or filename is not approval.
If an integration cannot retain a receipt, stop marker removal there and report the dependency.
