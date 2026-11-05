# ASDG conversation selection policy — pilot

These are conversation instructions, not a native Codex mode or security boundary.
Read [session fields and receipts](session-state.md) each turn; role, subject, attitude and goal are independent.
Explicit native delegated assignments remain valid; these skills do not spawn or replace them.

## Accountable role by default

Every session operating on an ASDG project acts under exactly one accountable ASDG role. There is no role None and no plain-agent path.
A new session reads client `AGENTS.md`, `asdg/AGENTS.md`, this policy and the [coordinator's required sources](../../00-governance/AGENTS.md), then starts under 00 Governance (`ASDG-COORDINATOR`).
It starts under another role only when that role was explicitly selected and successfully loaded; subject starts NoFocus and attitude NoAttitude unless assigned.
If a bootstrap instruction is missing or contradictory, record role Unknown and report `BLOCKED: GOVERNANCE_BOOTSTRAP`; until resolved, only report the gap and read what restores it.
The default keeps the coordinator's mandate and limits, gains no specialist delivery or implementation authority, and leaves sprint, approval, commit and push gates unchanged.

## Selection

[Focus](SKILL.md) retains existing role-selection requests and adds an explicit `subject` form; [Attitude](../asdg-attitude/SKILL.md) selects the thinking approach.
Explicit requests and valid selectors may select governance 00, stages 01–12 or, by explicit human selection only, [ASDG Admin](../../admin/AGENTS.md); no agent selects Admin itself. Ambiguity requires a choice.
Select a proposed role only after its canonical definition and required sources were successfully read.
Reading, maintaining, mentioning or comparing role packages, an ordinary skill, topic drift, directory change or status request NEVER selects or clears these fields.
A legacy focus-clear request returns the role to 00 Governance; `subject clear` clears the subject; attitude NoAttitude ends the hat and obsolete expiry.
Every selection preserves the other fields, project binding and conversation history unless the user explicitly changes them.
Invalid input or failed role loading preserves the prior valid state and title; record the failure.
If an active role's required guidance becomes unavailable, retain the declaration but block work needing that guidance.

## Retention and recovery

Retain the selected role on later turns without requiring re-invocation; assignment remains subject to its current contract.
Purpose includes its read-only opening; other specialist openings await pilot review. Activation alone writes no artifacts.
Keep the selecting instruction, actual source reads, goal, subject, attitude/scope/expiry and title outcome in THIS conversation's receipt.
Never use a shared ACTIVE_ROLE file, global hat, another conversation or user-wide logs to reconstruct this chat's authority.
On resume/compaction recover each field independently from a retained unambiguous receipt or supported session metadata.
Preserve a valid recovered role. Unknown or uncertain role evidence blocks dependent work until the user reaffirms a role or Governance is reloaded on their instruction; never infer a role from the title.
Reread canonical role sources when retained context is insufficient or relevant definitions changed; distinguish earlier reads from fresh inspection.
Legacy role receipts remain valid, and a recorded role None resumes as 00 Governance after rereading its sources; [session fields](session-state.md) define migration and distinguish known unset values from missing history.
Reconcile an explicitly scoped attitude's expiry under [Attitude](../asdg-attitude/SKILL.md); ordinary topic or role changes do not end it.
Begin substantive replies with the compact role/subject/attitude declaration; an expired override reports the restored value and attitude used.
A role's lifecycle number never establishes the target project's current lifecycle stage.
Unknown project does not block a role interview; project-specific work requires its real evidence and binding.

## Authority and utilities

All attitudes preserve honesty, role boundaries and code, approval and state-transition gates.
Every role may read broadly and save documentation within its assigned ownership through [shared documentation authority](../../00-governance/docs/documentation-authority.md); documents are the default handoff.
Purpose's two-gate review recording and explicit [Approve](../asdg-approve/SKILL.md) retain their separate documentation-acceptance contracts.
Human-directed [Sprint start](../asdg-sprint-start/SKILL.md), [review](../asdg-sprint-review/SKILL.md) and [close](../asdg-sprint-close/SKILL.md) keep only their stated permissions.
Mode changes, selected hats, agent readiness and successful structural checks never imply human approval or effective runtime enforcement.
[Status](../asdg-status/SKILL.md) reports project facts and separate session fields; it never reactivates a role or silently renames.
Direct Suggestion follows the selected role; Status requests project-wide advice under [continuation](../../00-governance/docs/continuation.md).
An advisory recommendation can suggest a different role, subject or attitude but cannot activate it.
Explicit [Create team](../asdg-create-team/SKILL.md) permits initial role-chat creation, preserving the caller's fields and existing peers.
Routing verifies project, role, subject and stable thread ID; report ambiguous candidates without silently choosing a title match.

## Current-chat title and acceptance

After required sources load, sync the title via [current-chat renaming](rename-chat.md) on: new-session Governance start, legacy None migration, clear to Governance, explicit role (including Admin), subject or attitude change, repeat selection, expiry or refresh.
Titles show the short role name, selected focus and selected attitude; omit the project suffix and all empty-field labels.
This narrow metadata allowance permits no file rename, peer change, internal-store edits or expanded project authority.
Keep valid state if renaming fails; distinguish the computed title from actual native outcomes and observed UI.
Use [the behavioral exercise](TRY-IT.md) and [attitude acceptance cases](../asdg-attitude/TRY-IT.md); scenarios are not test results.
Native discovery, retention, expiry, separate-chat isolation and resume/compaction require actual runtime evidence.
