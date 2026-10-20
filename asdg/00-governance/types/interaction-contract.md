# Shared interaction envelope

Initial contract notation: Markdown; runtime enforcement is not claimed.

| Field | Meaning |
| --- | --- |
| role_id / native_name | Actual responsible role and configuration name |
| status | ANSWER, OUT_OF_SCOPE, BLOCKED, or REVIEW_REQUIRED |
| requested_action | The user's requested outcome, unaltered in meaning |
| result | Scoped answer, proposal or findings |
| evidence | Read artifacts, observed tool results and their limits |
| boundary_reason | Why work is out of scope or blocked; distinguish role from mode |
| relevant_context | Minimum context needed for a coordinator return |
| approval_needed | Missing decision or permission, not a grant of approval |
| handoff_state | Not needed, pending return, or observed delivery with evidence |

OUT_OF_SCOPE requires requested_action, boundary_reason, relevant_context and approval_needed.
A specialist does not fill in a chosen peer; the coordinator owns that decision.
Human-readable paragraphs or a structured object may express this same contract.
No process is invoked merely because the response contains a status word.
Scope/authority disagreements return to the human rather than widening a role silently.

## Stage assessments

Within `result`, distinguish Intended, Actual and Planned using [the shared model](../docs/stage-perspectives.md).
Identify subject/project, scope/version/environment, as-of date, evidence and approval separately.
Use existing authoritative artifact and work-item references; do not create a second state store.
Apply this to stage assessments and substantive stage proposals, not every greeting or plain session-status request.
