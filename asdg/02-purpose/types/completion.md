# Purpose completion: agent readiness and User acceptance

Purpose is done for the reviewed baseline when two separate decisions have been recorded.

| Gate | Owner | Result |
| --- | --- | --- |
| Criteria assessment | ASDG-02 | `READY_FOR_ACCEPTANCE` |
| Explicit acceptance of the reviewed version | User | `ACCEPTED` — done for now |

## Agent criteria

Record evidence for all eight criteria in the readiness event; file presence alone is insufficient.

- `purpose`: the User's problem and reason for the product are clear.
- `outcomes`: desired benefits are explicit and understandable.
- `boundaries`: constraints, non-goals and assumptions are distinguished.
- `current_evidence`: current capabilities identify sources and verification limits.
- `next_improvement`: the selected next outcome is distinct from later possibilities and implementation commitments.
- `acceptance_questions`: observable questions and unresolved decisions are documented.
- `visual`: the embedded local illustration and available rendered preview were inspected; the caption distinguishes vision from current behavior.
- `documentation`: ordered files, navigation, links, source-line limits and generic User terminology were checked.

Unresolved feasibility or design choices can remain documented; they do not prevent a clear purpose baseline.
Any missing criterion leaves the stage `IN_PROGRESS`; do not record readiness when a required inspection is unavailable.

## Recording and accepting

Use only stage `02` in the existing `.asdg/lifecycle.json`; do not create a second state file or change other stages.
Register the three concept documents in `artifacts`, retain `not_applicable_reason: null`, and append to `reviews` without rewriting history.
Use `purpose_review.bundle_hashes` to capture the registered documents, README navigation and embedded image dependencies.
Every event contains `decision`, `actor`, `recorded_at` and that exact `artifacts` hash map.
A readiness event uses `actor: ASDG-02` and `criteria`: all eight criterion IDs mapped to nonempty assessment evidence.
Validate with `purpose_review.validate_reviews`; confirm the result through `python3 asdg/scripts/cli.py status --json`.

Present the reviewed document links and pending status to the User.
The User can say **“I accept the current Purpose baseline as done for now.”** Equivalent explicit acceptance is valid.
Only after that decision, append an `ACCEPTED` event with `actor: User`, the matching readiness hashes and the actual decision in `statement`.
Before recording acceptance, verify the current bundle still matches the reviewed version; otherwise reassess and present the new version first.
Positive feedback, agreement on these rules, file creation and agent assessments never count as User acceptance.
Actor labels are recorded provenance; structural validation does not authenticate the human source of a statement.

## Later changes

Changed document, navigation or image bytes make the prior review stale and the current status `IN_PROGRESS`.
Keep the earlier accepted version's hashes in history; reassess and seek acceptance of the revised baseline.
Unchanged accepted bytes remain accepted; no regeneration or repeated acceptance is needed.
When human Purpose acceptance is current and Context has no registered or substantive unregistered work, Stage 01 reports **Accepted — empty**.
This is derived from the recorded human acceptance under this rule; it creates no Context document or separate approval event.
Agent readiness alone never triggers it. Context work or a stale Purpose acceptance returns Context to its evidence-based status.
Purpose acceptance and its derived empty-Context flag do not start a sprint, approve implementation or close the project.
