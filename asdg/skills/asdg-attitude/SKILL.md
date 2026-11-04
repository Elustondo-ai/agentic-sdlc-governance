---
name: asdg-attitude
description: Select White, Red, Green, Yellow, Black, Blue or NoAttitude as this chat's thinking attitude, including temporary scopes; status only reports the selection. Explicit requests preserve role, subject, goal and project gates.
---

# ASDG attitude

Change how this conversation examines its subject, keeping its role, goal, subject focus, history and project.
Read client instructions, [session policy](../asdg-focus/session-policy.md), [session fields](../asdg-focus/session-state.md) and [attitudes and scopes](attitudes.md).
Resolve the client root as `../../..` from this canonical skill directory. No CLI state write or new agent is needed.

## Interpret the request

Activate only on an explicit request, including natural-language equivalents and English/Spanish colors.
“Attitude green,” “put on the black hat,” “Actitud amarilla” and “sin sombrero” are valid examples.
Use context to resolve “now green” when it clearly refers to this attitude conversation; unrelated color requests do not activate it.
Reading a hat description, quoting a command, proposing a switch or asking what a hat means leaves state unchanged.
A bare skill invocation asks which attitude the user wants; do not infer one from their mood, role or task.
For status / estado, report the current attitude, scope, expiry and retained title outcome, then stop without selection or renaming.
Unknown, conflicting or ambiguous selections leave the prior valid receipt and title intact; ask one focused clarification.
NoAttitude / Off / no hat / actitud normal ends the selection and any pending override; retain NoAttitude in the receipt and omit the attitude from the title.

## Select and apply

Recover the current receipt; validate the requested attitude and scope before changing any field.
Unknown role or subject stays Unknown; selecting an attitude neither recovers nor activates another field.
Record the explicit request, selected attitude, scope, expiry and prior attitude/scope to restore.
Pilot default — proposal for review: an unscoped selection lasts in this session until changed or turned off.
Honor explicit persistence and temporary scope; do not infer an expiry from a topic change, role change or completed task.
For “this answer only,” apply it to this response; for “this review,” identify the review and its observable completion.
If a temporary endpoint or nesting request is unclear, clarify it before replacing the current selection.
A later explicit selection supersedes the prior pending switch; never let an old expiry undo the user's newer selection.
After a successful selection, apply [current-chat renaming](../asdg-focus/rename-chat.md) using all current fields.
Use the selected thinking emphasis while keeping factual honesty, important caveats and existing authority.
Do not automatically cycle through hats, spawn another agent, infer user emotions, or execute work merely because a hat suggests it.

## Expire and report

At the explicit scope boundary, restore the recorded preceding attitude whose scope remains valid, otherwise its valid prior value; report Unknown if recovery evidence is missing.
NoAttitude or a newer explicit selection cancels obsolete restoration; preserve every intervening goal, role and subject update.
Finalize one-answer expiry before returning the completed response: retain the attitude used, restore state, and attempt the restored title.
Start the response with the accurate [session declaration](../asdg-focus/session-state.md); for an expired override identify both the restored value and attitude used.
Make expiry and native title outcome visible in the closing receipt; do not leave a persistent Black title after a completed Black-only answer.
If interrupted before expiry, retain the pending boundary in the checkpoint; reconcile it when the authorized response/review actually completes.
Rename failure does not undo attitude selection or expiry. Distinguish computed title from last observed UI title.
This skill grants no documentation acceptance, implementation permission, installation, external messaging or sprint transition.
