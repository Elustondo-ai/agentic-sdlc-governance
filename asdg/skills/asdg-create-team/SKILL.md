---
name: asdg-create-team
description: Set up ASDG governance and twelve specialist chats in the current Codex project, reusing existing focused chats. Use when the user requests their ASDG team; creating or explaining this skill alone does not create chats.
---

# ASDG create team

Give the user thirteen project chats: governance 00 and specialists 01–12, each with its own conversation focus.
These are user-owned chats sharing one repository; creating them does not assign project work or start a sprint.
Read client instructions and [session policy](../asdg-focus/session-policy.md); preserve this chat's focus.
A request to create the team, including invoking this skill for setup, authorizes the missing chats and their initial Focus prompts.
Automatic skill discovery, a status request or editing the skill is not a request to create chats.

## Resolve the project and roles

Resolve the client root as `../../..` from this canonical skill directory.
Read [the catalogue](../../00-governance/types/agent-catalog.json) and [Focus choices](../asdg-focus/focus-choices.md).
Use their thirteen identities and labels; verify the single installed `.agents/skills/asdg-focus/SKILL.md` adapter and each catalogue role's sources.
Run `python3 asdg/scripts/cli.py status --json`; inspect current facts without treating missing stage evidence as a setup blocker.
If initialization or required role sources are missing, report the prerequisite; do not initialize or install as a side effect.
Discover the native Codex project/chat tools and use their current schemas; this workflow requires user-visible project chat creation.
Call `list_projects`; match the verified repository path and execution host to its saved project ID.
If the target is ambiguous, ask the user to select it before creating chats. Do not substitute another project or a projectless chat.

## Reuse before creating

Call `list_threads` with enough results to inspect this project's active chats, including pinned entries.
Use titles only to find candidates; read candidate chats for an explicit Focus selection and successful activation.
Reuse only after verifying project, role receipt, subject and stable thread ID; a title alone is not confirmation. Keep distinct subject/attitude sessions independent.
The calling chat may fill its own role when its thread ID and retained activation receipt are known.
If several chats remain plausible for a role/subject, ask which to reuse; do not silently choose the first or newest, merge their state, or create another to evade ambiguity.
If likely matches have unresolved focus or the inventory is incomplete, mark those roles unresolved and ask only about those gaps.
Preserve existing chats: no messages, focus changes, renaming, archiving or worktree moves merely to reuse them.
Keep the role-to-chat mapping in this conversation; do not create shared active-role state or read internal app databases.

## Create the missing chats

Use native `create_thread` for each confirmed missing role, in small batches, with the verified project ID and local environment.
Omit model and reasoning overrides; honor any explicit user preferences. Do not create worktrees, subagents or cloud tasks.
Let each new chat compose its title through [the current title contract](../asdg-focus/rename-chat.md): short role, optional focus, optional attitude; keep the project binding in its receipt.
Each initial prompt must explicitly request `$asdg-focus` with its verified absolute path and that chat's catalogue role ID; no per-role picker skill is needed.
State the project root and request only activation, its required read-only opening/status, a brief role confirmation, then waiting for the user.
New chats start with subject NoFocus and attitude NoAttitude unless the user explicitly assigns them; never copy the caller's attitude or overwrite a reused chat's fields.
State that team setup assigns no documentation or application work; preserve role boundaries, existing files, approvals and sprint state.
A new chat has no inherited conversation history: pass relevant explicit user constraints with provenance, not a fabricated approval.
Do not ask the new chats to create peers, message this chat, run a project task or continue autonomously.
Retain each returned thread ID and host. After dispatch, use bounded `wait_threads` calls for up to eight targets, at most 60 seconds per wait.
Creation success is not focus activation: confirm the returned progress/receipt or report activation pending or failed.
For an uncertain creation outcome, inspect native inventory before retrying; never blindly create a duplicate.
Stop further creation after a shared permission or service failure; retain successes and report remaining roles.

## Show the team

Return a compact thirteen-role roster with actual chat titles and created/reused/unresolved outcomes; distinguish pending activation.
Emit the native `::created-thread{threadId="..."}` link for every newly created chat.
State any missing tools or partial result plainly; offer the verified Focus skill for manual setup when native creation is unavailable.
The user can continue in any specialist chat; team setup leaves this chat's focus and all project-action gates unchanged.
