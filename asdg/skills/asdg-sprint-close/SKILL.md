---
name: asdg-sprint-close
description: Review and close an explicitly selected ASDG sprint, preserving its definition and evidence before stopping it. Closing ends implementation permission; it does not imply successful completion, release or acceptance.
---

# Close an ASDG sprint

End the user's selected sprint without losing its definition, evidence or unfinished work.
Read client instructions, [session policy](../asdg-focus/session-policy.md), [the sprint gate](../../00-governance/docs/sprint-gate.md) and [recording rules](recording.md).
Resolve the client root as `../../..` from this canonical skill directory; preserve the current Focus.
Explicit human closure authorizes only the closeout receipt and the local stop command. It grants no product or release approval.

## Identify the decision and review

Read `python3 asdg/scripts/cli.py sprint status --json` and project `status --json`; bind the request to the active sprint.
If no sprint is active, report that fact and inspect only a relevant existing receipt; do not fabricate a closure.
If the user names another sprint, preserve the active sprint and clarify the target before writing.
A direct "close this sprint" is a closure decision. A question, review request, conditional future instruction or skill-maintenance request is not immediate authorization.
Reuse a fresh [sprint review](../asdg-sprint-review/SKILL.md) of the same definition and evidence; otherwise perform that read-only review now.
Choose `completed` only when all criteria have supporting PASS evidence; otherwise use `unfinished` and preserve the gaps.
If the user explicitly cancels the sprint, use `cancelled` and retain any available results.
Honor conditions such as "close only if everything passes"; if unmet, leave it active and report the failed condition.
An unconditional close may end an unfinished sprint. Do not demand another confirmation of that same decision or claim unmet work is complete.

## Preserve, stop and verify

Save and verify the closeout receipt under [the recording rules](recording.md) before invoking stop.
Retain the full active definition, criterion assessments, evidence references, carry-forward items and actual human closure statement.
Immediately before stopping, reread the active state and compare its exact hash with the reviewed snapshot; refresh a changed review or clarify a changed target.
Run `python3 asdg/scripts/cli.py sprint stop` only for the matching authorized active sprint.
The CLI clears ID, objective, scope and criteria; it has no separate `close` command and creates no review history itself.
After successful stop, read `sprint status --json` and require the inactive state with null identity/objective and empty scope/criteria.
Append the observed stop result and readback to the receipt; report archival failure separately if that final write fails.
A prepared receipt is not proof of closure. On command failure or uncertainty, inspect current state before any retry.
The existing CLI has no atomic compare-and-stop operation; if concurrent change is observed, stop and report the conflict rather than attempting another transition.
Respect runtime denials; provide human-run steps that preserve the receipt before stopping, without bypassing the guard or patching sprint state directly.

## Report the result

State the sprint ID, completed/unfinished/cancelled outcome, observed inactive or still-active state, and link the receipt.
List remaining work without silently starting another sprint or moving files.
Closing does not commit, push, delete work, deploy, accept documentation, alter role authority or close a release.
