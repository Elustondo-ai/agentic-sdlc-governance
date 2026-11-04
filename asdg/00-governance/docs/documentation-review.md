# When documentation is ready for its readers

These criteria apply to every project using this ASDG distribution and to ASDG's own maintained documentation.
Authors check their work; reviewers report remaining gaps before recommending documentation readiness.
Use the [documentation standard](documentation-standard.md) and [source companion contract](code-companions.md) as the authoritative requirements.

| Reader needs | Required evidence |
| --- | --- |
| Understand the subject | Project-specific purpose, responsibilities, decisions and boundaries in clear technical prose. |
| See the main idea | A useful embedded visual in each substantive explanation, with readable labels and accurate relationships. |
| Picture a graphical interface | A plain-language opening and a captioned screenshot or labelled mockup before technical detail, kept current, under the [GUI visual rule](gui-visuals.md). |
| Use the interface | A Markdown companion for each maintained source file, covering public types, functions, inputs, outputs, effects and errors. |
| Understand collaboration | Named collaborators, their responsibilities and links to relevant interfaces; use CRC thinking without inventing classes. |
| Trust the explanation | Compare descriptions with current implementation and relevant callers; distinguish facts, intentions and unknowns. |
| Find the detail | Working links, small coherent documents, readable formatting and realistic examples where applicable. |

## Author and reviewer responsibilities

Treat all human-readable artifacts under `docs/asdg/` as explanations for people, including technical designs and evaluations.
Keep machine records and implementation evidence available without making readers decode logs to understand the project.
Inspect rendered visuals and Markdown; a decorative image or a list of signatures does not satisfy the explanation requirement.
Navigation-only indexes, brief change notes and reference appendices may link to the substantive visual rather than duplicate it.
Check maintained application code, methodology tooling, scripts and tests in every language, including Python, TypeScript and JavaScript.
Generated code and third-party dependencies follow the exclusions in the companion contract; document their maintained integration boundaries.
Update companions in the same change as their source contracts; reconcile renamed files and incoming links.
For an existing project, report missing companions and stale explanations explicitly; never infer coverage from initialization or folder structure.
Do not mark documentation complete while required material is missing or materially inaccurate within the reviewed scope.
State the reviewed scope and remaining gaps; do not claim a repository-wide audit from a sample.
Preserve dated historical captures and exact-state review records; record corrections in living documentation.
These criteria govern review quality, not write permission, human acceptance, sprint authorization or release approval.

## Required visual check for each deliverable

Before declaring documentation complete, list each authored substantive Markdown file, its embedded visual, the idea it explains and the rendering inspection result in the delivery evidence.
Inspect every new or materially changed visual at a realistic document-pane width; reuse a suitable existing visual when it remains accurate.
Check the embedded result when preview is available, not only the full-size asset; report asset-only checks honestly.
A visual only in the README does not satisfy substantive sibling documents. An ordinary criteria/status table or decorative image is insufficient; use a diagram, meaningful dashboard or actual CRC relationship view.
If a visual is missing, broken or not inspected, report that specific documentation gap rather than claiming the visual check passed.
Preserved source archives keep their original bytes; the living explanation supplies the visual. Navigation-only pages and brief references may link to a substantive visual.

## Portable adoption

The client instruction bridge loads `asdg/AGENTS.md`; every specialist also reads the shared runtime contract.
Both point to these shared requirements, so every new project uses the same standard without borrowing a previous project's facts, thresholds or approvals.
Structural validation checks only its implemented rules; human readability and semantic accuracy still require actual review.
