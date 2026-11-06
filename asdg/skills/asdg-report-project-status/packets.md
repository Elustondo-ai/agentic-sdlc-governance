# One specialist, three slides

Write for the project's stakeholders. Use the actual project's name and stage label in the header. Use the project's presentation branding throughout. A slide should communicate one conclusion at normal presentation size. The report owner turns the worker’s visual and narration into reviewable slide sources before export.

| Slide | Question to answer | Required content |
| --- | --- | --- |
| Current definition | What has this project defined in my specialty? | State the current position, scope and one material boundary or decision. Identify draft or accepted status using exact-state evidence. A role description alone does not answer this question. |
| Current status | What has happened, and how do we know? | Present completed or verified work, work in progress and the most consequential gap or blocker. Distinguish documented intent from implementation and runtime evidence. |
| Next plan | What should happen next in this specialty? | Give the next one to three actions, an accountable role or unassigned owner, dependency/decision and an observable success criterion. Label proposed versus committed work; include dates only when sourced. |

## Worker assignment and return

The parent assigns one stage, the same snapshot and a read-only scope. The worker reads current stage records and relevant supporting evidence, then returns the actual section content. Use this compact field contract; the transport may be the host's structured return or validated JSON in its response.

- Logical envelope: run ID, project ID/binding, revision plus relevant working-tree state, as-of time, stage, role ID, role sources loaded, and coverage limitations.
- Slides: exactly three, with kinds `definition`, `status`, `plan` in order. Each has a headline, up to three visible points, a concrete visual brief naming what to show, natural spoken Markdown notes, and claim-level references to source paths and sections, tests or decisions where available.
- Mark evidence as current, draft, stale, contradictory or unavailable where significant. If a stage has no evidence, say what was checked and what would resolve the gap. Never invent a milestone or silently treat a proposal as accepted.
- Parent receipt: expected roles and one outcome each, actual worker/attempt IDs when exposed, dispatch/return/release times or status, packet reference/hash, final slide numbers, coverage and build outcome. Keep explicit nulls for unobserved events.
- If evidence changes during the run, re-read affected inputs and re-run only affected sections, or mark them stale with their actual baseline. Preserve disagreements across stages and link both sources.

## Illustrative Purpose section

For a hypothetical rehearsal app, a definition slide could say “Help speakers notice when an answer has run long.” A status slide could distinguish a documented cue from an unmeasured effect on rehearsal. A next-plan slide could propose observing the next rehearsal and recording whether the speaker acted on the cue. Use project evidence when producing a real report.

The executable field names and an example run are in [packet checking](report_packets.md). The full parent receipt may retain additional audit fields. The checker validates structure and bindings; the parent verifies the evidence and native origin.
