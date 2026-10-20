# Rename the current conversation after Focus

Run only after successful focus activation, explicit clear or repeat activation, not from Status.
Pablo requested this chat-label effect as part of Focus; it does not authorize any project action.
Keep the selected focus even if the client cannot rename or the rename fails.

## Name

Use `NN <short focus label> — <target project display name>`; use `General — <project>` after clear.
Take the label from [UI choices](focus-choices.md), not an invented or renumbered role.
Prefer the user's supplied project display name; `agentic-speaker-coach` may display as `Speaker Coach`.
For other projects without a display name, use their verified project name as supplied; do not guess one.
Unknown project: omit the project suffix. Examples: `02 Purpose`, `02 Purpose — Speaker Coach`.
Honor an explicit title supplied for this activation instead. A title never supplies role or project authority.
Keep it one line, concise and free of secrets. Never truncate the role prefix.

## Native action

Use the current client's supported rename-chat action/tool, just as for a direct rename request.
Inspect the available interface and use its actual schema; do not invent a tool or directive.
If `codex_tui.set_thread_title` is exposed, pass `title` and omit `threadId` to target the calling thread.
If `mcp__codex_app__set_thread_title` is exposed, pass `title` and omit `threadId`.
An equivalent native current-chat rename tool/action is acceptable when the client provides it.
When an ID is required, use only the current thread ID supplied by the runtime; never guess from a title.
If no suitable native action is available, report UNAVAILABLE plus the proposed title; do not claim success.
Do not list other chats, scan session logs, start another app server or alter internal files/databases.
Do not rename folders, source files or projects; do not delete, archive, fork or create any conversation.
Respect runtime permissions; a denial is not authorization to try a different access route.

## Evidence

RENAMED: a native action explicitly acknowledged success; record the requested title and action result.
Verify by a native current-chat readback when available; otherwise say UI readback not inspected.
UNCHANGED: current title was actually observed to equal the requested title; no rename needed.
FAILED: the native action returned an error. UNKNOWN: attempted action had no conclusive result.
Keep outcomes distinct; do not retry an uncertain result without an available current-chat check.
Put the receipt in this conversation, not a shared active-role or title-state file.
Status reports the last title-update receipt, not an unobserved claim about the current UI title.

## Reference

[Codex App Server thread/name/set](https://developers.openai.com/codex/app-server/)
The native interface depends on the client; a protocol method alone does not make it an exposed tool.
