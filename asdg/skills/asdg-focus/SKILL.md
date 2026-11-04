---
name: asdg-focus
description: Preserve conversational ASDG role selection; use subject plus a topic to change subject focus within the current role. Clarify ambiguous requests before switching; all selections retain existing authority.
---

# ASDG Focus — role selection and subject focus

Read [session policy](session-policy.md) and [session fields](session-state.md). Only explicit requests change selection.
This remains the single public Focus skill; existing role phrases, IDs and clear commands retain their meaning.
Pass the complete user phrase and task context; never interpret them as shell commands.

## Resolve the requested dimension

An explicit `subject <topic>`, `subject clear`, `subject status`, or clear within-role topic request uses [subject focus](subject-focus.md); then return without running role activation.
For role requests, read [the catalogue](../../00-governance/types/agent-catalog.json) and [interpretation guidance](focus-choices.md).
“Focus on high level architecture,” numeric IDs, canonical IDs, native names, folder basenames and established aliases still select roles.
If subject-versus-role intent remains ambiguous, ask one question before changing either field or the title.
For one clear role match, state the interpreted role and proceed without another confirmation.
For overlapping responsibilities, ask among plausible specialists with a recommendation and reason; an unanswered option is not a selection.
For missing or unrecognizable intent, ask which specialist the user wants, showing the twelve plus Governance separately.
Quoted examples, hypothetical requests and explanations select nothing.
For legacy `clear`, “clear focus,” or “return to general,” return the role to 00 Governance by loading its sources as for any selection; preserve goal/subject/attitude/project, then rename and report Status.
Resolve a role to exactly one catalogue entry, or for an explicit Admin selector to the [Admin registration](../../admin/types/admin-role.json); do not synthesize paths, identities or numbering from user input.
00 selects ASDG-COORDINATOR, which is also the default role; there is no role None. Clarification and invalid input preserve the prior receipt and title.

## Read before role activation

Resolve client root as `../../..` and distribution root as `../..` from THIS canonical skill directory.
Read client AGENTS.md and `asdg/AGENTS.md`; verify the session-policy reference or report BLOCKED: SESSION_POLICY_NOT_CONFIGURED.
Retain the target project and all other session fields; unknown project is valid for an interview.
Read [the lifecycle baseline](../../docs/lifecycle-baseline.md); stop on identity/order disagreement.
Read the selected catalogue entry, required sources and procedure in full, including contract, runtime rules and response envelope; for Admin, its registration lists them.
Resolve links from their containing files; confirm role ID/native name/stage match the catalogue.
Missing or contradictory sources block the proposed switch and preserve the previous role and title; if the Governance sources themselves fail, report `BLOCKED: GOVERNANCE_BOOTSTRAP`.
Inspection alone does not activate a role; do not substitute an old provider checkout or remembered definition.

## Activate, rename and report

After successful reads, replace only this chat's role. Preserve subject even across role changes; flag an out-of-role subject without silently erasing it.
Record the selecting phrase, interpreted role, actual sources, invoked skill and the retained goal/subject/attitude/project.
All agents retain [documentation authority](../../00-governance/docs/documentation-authority.md); code, approvals and operations retain separate gates.
Purpose begins its [read-only opening](../../02-purpose/skills/elicit-purpose/opening.md); activation alone writes no artifacts.
Follow [current-chat renaming](rename-chat.md): short role name, selected subject, selected attitude; project binding stays in the receipt.
A failed rename does not undo selection. Repeated role selection refreshes required reads and retries the title; it does not reset other fields.
For Purpose, collect [Status](../asdg-status/SKILL.md) facts-only once and reuse the result in its opening, with the actual rename outcome.
If selection includes an assignment, continue that authorized work without a redundant interview.
For clear or another role without an assignment, return Status and stop; other specialist openings await pilot review.
Keep the compact first-line state declaration accurate. No activation grants implementation, installation, delegation, commit, deployment or sprint authority.
