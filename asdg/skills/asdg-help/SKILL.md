---
name: asdg-help
description: Explain ASDG commands, invocation syntax, examples and boundaries. Use for the command list, getting started or help with a named ASDG skill; explanation only.
---

# ASDG command help

Help the user find the command that fits their intent and understand what it does before invoking it.
Read [session policy](../asdg-focus/session-policy.md); preserve role, subject, attitude, title and project binding.
Use this project's installed definitions; resolve the client root as `../../..` from this canonical directory.
A help request explains commands only: do not execute the listed workflows, inspect peer chats, install anything, select a role, record acceptance or start project work or a sprint.

## Explain invocation and availability

In Claude Code use `/asdg-help`; in Codex use `$asdg-help`. Apply that prefix distinction to every skill below; these are chat skills, not terminal subcommands.
If native discovery is unavailable, ask the agent to read and follow `asdg/skills/asdg-help/SKILL.md`; do not claim the command is installed or working from source presence alone.
With no topic, show the complete portable command table below, a few useful examples, and a link to the terminal reference. With a named command or task, explain the relevant entry first; show the full list when requested.
Read the relevant linked canonical skill before explaining arguments, prerequisites or effects in detail. Descriptions below are navigation, not replacement policy.
Keep missing client capabilities and optional dependencies visible: automated team setup and development panes require supported native tools; OpenSpec needs its separately installed workflow.
For “all commands,” include the terminal commands in [the reference](command-reference.md), and distinguish provider-only capabilities from the portable list. Do not invent aliases or expose private stage procedures as public commands.

## Portable chat commands

| Command (Claude spelling) | Purpose and effects |
| --- | --- |
| [/asdg-help](SKILL.md) | Explain commands and examples; changes nothing. |
| [/asdg-update](../asdg-update/SKILL.md) | As selected Admin, preview a distribution update and separate adapter refresh; approve each plan before apply. |
| [/asdg-init](../asdg-init/SKILL.md) | Preview installation; apply only after explicit approval of the exact preview. |
| [/asdg-create-team](../asdg-create-team/SKILL.md) | Reuse/create the thirteen role chats and arrange lifecycle order; shared sorting changes need approval. |
| [/asdg-focus](../asdg-focus/SKILL.md) | Select a role, or use `subject` to change its topic independently. |
| [/asdg-attitude](../asdg-attitude/SKILL.md) | Select a thinking attitude and scope, clear it, or report it. |
| [/asdg-status](../asdg-status/SKILL.md) | Report project/session facts and one project-wide next step; facts-only omits advice. |
| [/asdg-role](../asdg-role/SKILL.md) | Explain the current role's mandate and boundaries; no selection change. |
| [/asdg-admin](../asdg-admin/SKILL.md) | Explicitly select methodology Admin, or `clear` back to Governance; selection authorizes no edits. |
| [/asdg-approve](../asdg-approve/SKILL.md) | Record explicit human acceptance of a previously presented exact documentation bundle. |
| [/asdg-sprint-start](../asdg-sprint-start/SKILL.md) | Start a human-requested scoped sprint from clean Git on a new sprint branch. |
| [/asdg-sprint-review](../asdg-sprint-review/SKILL.md) | Assess the active sprint's evidence without changing its state. |
| [/asdg-sprint-close](../asdg-sprint-close/SKILL.md) | Preserve review/unfinished work and end the explicitly selected sprint. |
| [/asdg-suggestion](../asdg-suggestion/SKILL.md) | Recommend one useful next contribution; advice only. |
| [/asdg-view-dev](../asdg-view-dev/SKILL.md) | Open a relevant file and terminal in supported development panes; UI only. |
| [/asdg-documentation](../asdg-documentation/SKILL.md) | Author or review readable project documentation under the shared standard. |
| [/asdg-decision](../asdg-decision/SKILL.md) | Compare, document or revisit a material decision in the current role's context. |
| [/asdg-openspec-propose](../asdg-openspec-propose/SKILL.md) | Draft a proposal using installed OpenSpec and ASDG evidence; planning only. |

## Examples and boundaries

For orientation, use `/asdg-status` or `/asdg-role`. For role selection use `/asdg-focus Purpose`; for a topic within that role use `/asdg-focus subject onboarding`.
Use `/asdg-attitude Black for this review` for a temporary risk-focused review; `/asdg-attitude status` reports it and `/asdg-attitude NoAttitude` clears it.
Examples are quoted guidance, never activation requests. [More selectors and terminal commands](command-reference.md) explain clears, CLI syntax and optional tools.
Explaining approval or sprint commands grants no approval or transition; listing commands does not commit, push, publish, deploy or start work.
