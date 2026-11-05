---
name: asdg-create-team
description: Set up ASDG governance and twelve specialist chats in the current Codex project, reusing existing focused chats. Use when the user requests their ASDG team; creating or explaining this skill alone does not create chats.
---

# ASDG create team

Give the user thirteen project chats: governance 00 and specialists 01–12, each with its own conversation focus.
These are user-owned chats sharing one repository; creating them does not assign project work or start a sprint.
Read client instructions and [session policy](../asdg-focus/session-policy.md); preserve this chat's focus.
A request to create the team, including invoking this skill for setup, authorizes the missing chats, their initial Focus prompts and project-local ordering below, subject to the shared-preference approval gate.
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

Follow [missing-chat creation](create-chats.md); retain confirmed role-to-chat IDs before ordering.

## Keep lifecycle order stable

After setup, arrange only the verified target project's ASDG team chats in this fixed sequence:

00 Governance → 01 Context → 02 Purpose → 03 UseCases → 04 EvalStrategy →
05 Architecture → 06 POC → 07 Planning → 08 Specs → 09 Coding →
10 ReviewQA → 11 Operations → 12 Observability.

Discover supported sidebar tools and current sorting preferences (`list_threads` in Codex); never assume returned recency order is sidebar display order.
If manual sorting changes a shared preference, explain that it affects Recents and chats across projects and Codex/Work; obtain explicit approval before changing it. Existing manual sorting needs no preference change.
Prefer supported app tools with their current schemas. Project-list or section reordering is not project-chat reordering; never invent a project-chat API or edit internal app databases or configuration stores.
Apply a supported fixed order only to confirmed role-to-chat IDs; unresolved roles or ambiguous matches stay unresolved. Preserve unrelated sidebar items and their positions; decline operations whose scope cannot preserve them.
Reuse existing chats; preserve contents, identities, role selections, subjects, attitudes, native notification dots and unread states. Do not open/mark chats read, send activity to simulate order, rename, pin or move them to force sorting.
If supported tools cannot set fixed project-chat order, explain the limitation and provide manual instructions: inspect the sidebar sort control, select manual order only after approval of any shared scope, then drag verified team chats into the sequence above without moving unrelated items. If the UI lacks fixed ordering too, report it unavailable.
Record intended order, target IDs, preference approval if needed, attempted operations and acknowledgements. Separate tool readback from visually verified results; say when visual verification was unavailable. An acknowledgement alone never proves visible order or stability after activity.
Creation and ordering must not start project work or a sprint; editing this policy authorizes neither team creation nor reordering.

## Show the team

Return a compact thirteen-role roster with actual chat titles and created/reused/unresolved outcomes; distinguish pending activation.
Emit the native `::created-thread{threadId="..."}` link for every newly created chat.
State any missing tools or partial result plainly; offer the verified Focus skill for manual setup when native creation is unavailable.
The user can continue in any specialist chat; team setup leaves this chat's focus and all project-action gates unchanged.
