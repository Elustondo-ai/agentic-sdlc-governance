# Read broadly. Write within your responsibility.

Governance and all twelve specialists may consult documentation throughout the bound project.
Ordinary documentation needs no active sprint or separate save approval, but each role writes only its owned directory and the narrow exceptions below.
This is best-effort agent governance, not an adversarial security boundary; developers retain unrestricted control of their repositories.

## Ownership and handoffs

The [canonical catalogue](../types/agent-catalog.json) defines every role's exact folder.
For each project role, replace the catalogue folder's leading `asdg/` with `docs/asdg/`: Governance owns `docs/asdg/00-governance/`; all twelve specialists own their corresponding stage.
For example, Purpose owns `docs/asdg/02-purpose/`, Architecture owns `docs/asdg/05-high-level-design-and-architecture/`, and Planning owns `docs/asdg/07-planning/`.
Ownership covers creation, modification, moves, deletion and supporting assets; validate both ends of a move.
Read another stage as evidence; save a proposed correction in your own folder, link the authoritative source and return a handoff. Do not silently edit the other owner's artifact.
Documents are the default way agents communicate substantive outcomes; a proposed patch remains a proposal until the responsible role applies it.
Read access and an active sprint never expand write responsibility. Unknown role identity blocks writes until recovered under the session policy.
A brief answer, status-only request, role activation or explicit chat-only assignment creates no documentation requirement.

![Every role reads shared evidence and writes its owned documents; acceptance and implementation stay separate.](images/documentation-authority.svg)

## Central exceptions

[Write exceptions](write-exceptions.md) enumerate all shared workflows, with their authorization and limits.
[The ownership checker](../../scripts/lib/cli_ownership.md) derives role destinations from the catalogue and implements supported path checks; do not duplicate permission tables in skills.
Specifications retains its resolved OpenSpec store exception. Coding retains sprint-gated application, test and related technical documentation writes. Neither may rewrite another specialist's documents.
Governance maintains its coordination artifacts and explicitly assigned shared records; Admin maintains methodology only under explicit selection and bounded human scope.

## Before writing

Follow [the pre-write procedure and client limits](write-controls.md), using the actual conversation role; a title is never role evidence.
Apply the [documentation standard](documentation-standard.md), [review criteria](documentation-review.md) and [stage layout](stage-layout.md).
Append exact-hash AI modification receipts to `.asdg/document-reviews.json`, preserving history and old approval bindings; a receipt never grants acceptance.
If recording is denied, retain the saved document and report the receipt gap; do not bypass runtime denials.
Ownership permits no unrelated deletion, install, commit, push, publication, deployment, approval or lifecycle transition.
Executable code and runtime configuration remain application changes even under `docs/`; apply the sprint and implementation gates separately.
