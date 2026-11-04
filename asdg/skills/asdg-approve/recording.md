# Recording documentation acceptance

An explicit human invocation of ASDG Approve permits only target-stage artifact registration and append-only readiness/acceptance events in the existing `.asdg/lifecycle.json`.
This is a shared human-directed recording workflow, not general write authority for the selected role. It needs no application sprint and grants no other lifecycle transition.
Creating or installing the skill records no approval; a User decision must name or unambiguously refer to the exact presented bundle.

## Existing state and stage contracts

Read the current lifecycle index, canonical catalogue and owning stage contract. Preserve all existing stages, metadata and review history.
Use the target's canonical two-digit stage key. Register only the named client artifacts being accepted; do not register methodology files as client evidence.
Stage 02 keeps [Purpose's completion contract](../../02-purpose/types/completion.md) and the unchanged `purpose_review` helper.
Other stages use the read-only `stage_review` helper in `asdg/scripts/lib/`; actor labels record provenance rather than authenticate the human.
These records accept documentation baselines; they do not close releases, authorize implementation or prove product behavior.
If a requested approval has other semantics or no applicable stage contract, report that boundary instead of mapping it to a documentation acceptance.

## Exact bundle and events

For Stage 02 call `purpose_review.bundle_hashes(root, artifacts)` and its `validate_reviews` and `completion_status` functions.
For other stages call `stage_review.bundle_hashes(root, artifacts, prefix)`, where `prefix` is the target's canonical `docs/asdg/<stage>` path.
The latter hashes registered files, the stage README and transitively linked local stage files, including images, SVG and PlantUML source. Outgoing source links must resolve but do not approve another stage.
Use relative inline Markdown links for discoverable dependencies. Explicitly include dependencies in the artifact list when the helper cannot discover their markup; unavailable or remote image bytes cannot be approved as a local exact bundle.
Every review event has `decision`, `actor`, `recorded_at` and `artifacts` containing repository-relative paths mapped to SHA-256 hashes.
A `READY_FOR_ACCEPTANCE` event uses the owning `ASDG-NN` actor and a `criteria` map with nonempty, actual assessment evidence for each criterion required by that stage's contract.
An `ACCEPTED` event uses `actor: User`, the same hash map as a prior readiness event and a nonempty `statement` retaining the human's actual approval wording or explicit invocation.
Record readiness separately from acceptance; a recorder cannot invent an owning-role assessment or human approval.

## Scoped update and verification

Read the exact current state again before applying a scoped patch; if it or the target bundle changed during preparation, reconcile and recheck instead of overwriting concurrent work.
Add target-stage references and append events only. Never replace past events or change unrelated state, files, stages, sprint settings or hooks.
Validate proposed history with `purpose_review.validate_reviews(reviews)` for Stage 02, or `stage_review.validate_reviews(reviews, number, prefix)` for other stages.
Recompute the bundle and require equality with the presented snapshot before recording acceptance. Do not transfer an old decision to revised bytes.
Use `python3 asdg/scripts/cli.py status --json` after saving; require target `completion.status: ACCEPTED`, `user_accepted: true` and `review_stale: false` before reporting persisted acceptance.
Later document, navigation, diagram-source or image changes make the old review stale; retain history and repeat readiness and explicit acceptance for the new version.
If saving is denied or validation fails, leave prior records intact and distinguish the conversational decision from a persisted result.
