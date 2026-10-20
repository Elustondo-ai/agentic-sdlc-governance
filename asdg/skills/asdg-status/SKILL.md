---
name: asdg-status
description: Report ASDG conversation focus, target project, source-read evidence, responsibilities, boundaries and current task. Use for ASDG status or role questions; never activates a specialist.
---
AI-MODIFIED - 2026-10-19T02:40:42Z

# ASDG Session Status — read-only

Read [session policy](../asdg-focus/session-policy.md) and use [the report format](status-format.md).
This is a cross-role inspection capability, usable before and after specialist activation.
It does not select, refresh, clear or delegate a role, rename the chat, change modes, or perform project work.
It complements native Codex /status and is distinct from the shell command `asdg status`.

## Inspect

Use this conversation's explicit activation/clear history and observed source-read results.
In a fresh conversation without activation, report `None — general ASDG session`.
After observed successful activation, report the selected role, stage and activation mechanism.
A known selection with missing required guidance is `Selected, but blocked`; do not clear it.
Lost or ambiguous history is `Unknown — reactivation required`, not a guessed default.
A failed focus attempt does not overwrite an earlier successful selection; report it separately.
Get the target project from explicit user context or verified binding; otherwise report `Unknown — not supplied`.
Show the latest substantive task, not this status request itself; if none exists, `Awaiting assignment`.
Read needed canonical sources when available to explain responsibilities accurately, without activating them.
Mark any new source reads as `Read for inspection now`, not retrospectively as `Loaded at activation`.
Do not claim every referenced file is loaded, that content is pinned in memory, or that instructions were obeyed.
Record source paths actually read and separate verified facts, session declarations and unknowns.
Do not infer project/sprint status from the selected specialist's stage.

Read the last title-update receipt when retained; do not infer success from the focus or a proposed title.

## Report without mutation

Return the requested compact plain-text report, then stop. Do not start interviews or suggest unrelated work.
For any selected stage, derive responsibility/exclusions from its canonical role; show its actual evaluation limits.
For no selected role, report root governance, not a specialist's private mandate.
Unknown values remain unknown; missing source evidence is stated rather than fabricated.
Runtime settings: `Not inspected; use native Codex /status` unless actual configuration evidence is available.
A declared read-only evaluation rule is not proof of a read-only runtime sandbox.
No filesystem writes, installs, permission changes, approvals, commits, pushes, routing or sprint transitions.
Do not scan credentials, user-wide Codex logs or other sessions to fill this report.
This YAML-first file records AI modification, not whole-file human approval.
