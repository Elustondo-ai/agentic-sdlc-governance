---
name: asdg-view-dev
description: Open the current Codex chat's development view with a relevant project file on the right and a terminal below. Use when the user asks to arrange or restore development panes; changes UI only, not ASDG focus or project files.
---

# ASDG development view

Keep the conversation alongside a useful document or source file and a bottom terminal.
This is a presentation utility, not a role selector, installation step or permission change.
Read client instructions and [session policy](../asdg-focus/session-policy.md); preserve the current focus and task.
Resolve the client root from this canonical file as `../../..`; never hard-code a developer's home or another project.

## Choose the file

Honor an explicitly supplied project file, resolving relative paths against the client root and checking existence.
Otherwise use the file currently being discussed, if known and available.
With a retained specialist focus, consult [the catalogue](../../00-governance/types/agent-catalog.json) for its stage folder;
prefer that stage's existing client `docs/asdg/<stage-folder>/README.md`, never a reconstructed role path.
For governance or a general chat, prefer the client `docs/asdg/README.md`, then `asdg/README.md`, then root `README.md`.
Open one file by default; honor explicit requests for additional files or a review pane.
If no suitable file exists, open the terminal and report that gap; do not create placeholder documents.

## Open supported panels

Use the exposed native `mcp__codex_app__open_in_codex` tool or its documented equivalent.
Open the verified absolute file path with target type `file` and placement `right`.
Open a terminal with target type `terminal` and placement `bottom`; omit its session ID to let the app select one.
Omit `threadId` so the panels belong to this chat. Another chat requires the user's explicit request and verified identity.
For a requested diff, use a native review target with the requested scope; opening it never stages, commits or changes files.
Preserve existing tabs and terminal sessions. Do not run commands, start servers or change directories merely to arrange the view.
No ASDG state reads, model calls or initialization are needed just to open panels.
If a native operation is unavailable or denied, report the limitation once; do not edit internal app state or bypass a refusal.

## Explain what happened

Report the chosen file and actual tool outcomes briefly. A queued request is not verified visibility or an exact restored layout.
Native panel opening does not expose exact widths, split ratios, sidebar visibility or file-tree expansion controls.
For the remaining manual adjustment on macOS, the documented file-tree toggle is Command+Shift+E; pane dividers can be adjusted by the user.
Only offer the toggle if needed; blindly toggling can hide an already-visible tree.
Consult the current [official shortcut reference](https://learn.chatgpt.com/docs/reference/commands) for other platforms or changed shortcuts.
Do not claim the screenshot was reproduced unless actually observed; a supplied screenshot is reference material, not live UI state.
Keep files, hooks, permissions, focus, chat title, sprint state and other chats unchanged.
