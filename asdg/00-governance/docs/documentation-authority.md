# Documentation authority for every agent

Every agent, including governance and all twelve specialists, may create and update project documentation and supporting assets under the bound client's `docs/` at any time.
No active sprint, implementation scope check or separate permission to save is required for documentation.
This applies to proposals, use cases, plans, designs, evidence reports, decisions and their diagrams or other explanatory assets.

## Shared work and handoffs

Documents are the default way agents communicate substantive outcomes and leave reviewable work for one another.
Read the current authoritative document, improve it in place when appropriate, and return a link with a concise explanation.
Use the established stage layout and the role's normal destination; `docs/asdg/<stage>/` is the default for lifecycle evidence.
A stage folder expresses ownership, not a write-permission barrier. Coordinate overlapping edits and preserve others' work.
A brief answer, a status-only request or an explicit instruction to stay in chat does not require a document.
Focus activation alone creates no work. Continue the actual assignment rather than generating material to fill folders.
Direct messages can complement shared documents when the user has authorized that coordination; a file link alone is not proof of delivery.
Role responsibilities still apply: document findings, proposals or handoffs without claiming another specialist's work was completed.

![Every agent saves shared documentation for review; acceptance and scoped implementation remain separate decisions.](images/documentation-authority.svg)

## Preserve evidence and boundaries

Apply the [documentation standard](documentation-standard.md), [review criteria](documentation-review.md) and [stage layout](stage-layout.md).
Use scoped patches for text changes; keep visuals editable, check links and rendering, and distinguish intended behavior from observed evidence.
Append exact-hash AI modification receipts to the existing `.asdg/document-reviews.json`, preserving prior entries and approval bindings.
A receipt records authorship, not acceptance. If recording is denied, retain the saved document and report the receipt gap without bypassing the denial.
Editing an accepted artifact does not transfer its acceptance to new bytes; preserve historical records and identify changed proposals.
This permission does not authorize unrelated deletion, application-code changes, policy changes, installs, commits, pushes, publication, deployment or state transitions.
Executable application code or runtime configuration is not documentation merely because it is placed in `docs/`.
Documentation needs no sprint; application changes still require the active sprint's objective, scope, acceptance criteria and applicable role authority.
Purpose review recording and explicit approval/sprint utilities retain their separate contracts; no lifecycle approval is inferred from saving a file.
Methodology maintenance requires an explicit user task performed under [ASDG Admin](../../admin/AGENTS.md). Runtime denials remain binding and must be reported.
