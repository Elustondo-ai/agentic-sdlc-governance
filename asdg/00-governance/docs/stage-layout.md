# Stage documents: read the files in order

In every consuming project's stages 01–12, keep main perspective documents directly in the stage folder; named decision packages are the exception below.
The filename communicates both reading order and perspective; no perspective subfolder is needed.

| File family | Reader's question | Example |
| --- | --- | --- |
| `01` Intended | What do we want and why? | `01-purpose.md`, `01.1-outcomes-and-boundaries.md` |
| `02` Current | What exists and what evidence supports it? | `02-current-capabilities.md`, `02.1-known-limitations.md` |
| `03` Planned | What might or will change next? | `03-planned-improvements.md`, `03.1-release-plan.md`, `03.2-sprint-plan.md` |

Use descriptive names appropriate to each stage; the three families apply to all twelve specialists.
Keep a useful main document, then split distinct topics using `.1`, `.2` and so on when needed.
Each Markdown unit retains the 50-nonblank-line limit; do not create filler to populate a family.
Keep README navigation at the root and supporting assets in folders such as `images/` and `sources/`.
Do not create `intended/`, `current/`, `planned/`, `planned-release/` or `planned-sprint/` for new living documents.

## Decision packages

Material decisions may use `decisions/<Decision name>/` within the responsible stage, following [ASDG Decision](../../skills/asdg-decision/record-format.md).
Keep one or two introductions, meaningful option notes and editable visuals; numbering inside a decision folder expresses reading order, not stage perspective.
Link packages from relevant stage navigation within the assigned scope; do not duplicate authoritative state or infer approval.

## Plans and completed work

Use release or sprint in a plan's descriptive filename when its horizon is known.
Inside each plan, state whether it is proposed or selected, and its cycle reference when known.
Link selected work to the integrated Stage 07 plan and authoritative cycle state; filenames do not authorize work.
After a cycle actually finishes, consolidate verified results and limitations into `02` Current documents.
Update enduring intent only when an explicit decision changes it; retain unresolved work with its decision status.
Remove only the completed cycle's temporary plans after preserving decisions, evidence and review history.
Do not remove active or future plans, accepted evidence or durable review events as cleanup.

## Existing projects and history

Move living documents deliberately; update navigation, relative links and current registered artifact paths.
Keep old review events and their hashes intact; relocation never transfers acceptance to a new bundle.
Dated reports, receipts and source captures may remain in their existing archive folders to preserve provenance.
This archive exception does not authorize new perspective folders; new living summaries use numbered root files.
ASDG's reusable definitions supply this blueprint without duplicating themselves across all three perspectives.
Initialization preserves existing project documents; migration is a separate explicit task.
Apply [role ownership](documentation-authority.md) to edits, moves, cleanup and navigation; hand off changes to another owner.
The layout does not start a sprint, grant implementation permission or approve a release.
