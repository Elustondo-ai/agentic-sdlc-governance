# Keep the current chat title aligned with its state

Run once required sources load: a new session starting under 00 Governance, a legacy role None migrating to it, a clear returning to it, any explicit role selection including ASDG Admin, subject or attitude selection/clear, repeat selection, explicit-scope expiry or an explicit title refresh.
Status alone never renames. Preserve valid selection even if native renaming is unavailable or fails.
Read the current [session receipt](session-state.md); the title is its projection, never evidence of authority.

## Compose the title

Use `NN <short role label> [<focus>] [<attitude>]`, joined with single spaces; brackets indicate optional fields and are never literal.
Take stage/role identity from [the catalogue](../../00-governance/types/agent-catalog.json) and its short label from [Focus choices](focus-choices.md).
For example: `00 Governance`, `05 Architecture`, `05 Architecture Security`, or `05 Architecture Security Black`.
ASDG Admin is outside the stages: use `ASDG Admin [<focus>] [<attitude>]` with no number.
Use the exact short labels supplied in Focus choices; preserve catalogue numbering and project binding in the receipt.
Append an explicitly selected focus, then a selected English attitude color. Omit unset fields entirely: no Off, NoAttitude, NoFocus, None or placeholder separators.
The default role displays `00 Governance`; there is no `General` title. Unknown or blocked role displays `Role unknown` without inventing a prefix.
Report unknown focus/attitude in the receipt and reply; do not infer an empty selection. Omit unverified optional title fields.
Never append the project name automatically or use it as an inferred focus. Goal, project and temporary scope stay in the receipt.
Use one line with no pipes, dots, dashes, secrets or control characters added as separators; retain the full selected focus in the receipt if its display needs shortening.
Identical selections may share a title; route by verified receipts and stable IDs, never by title alone.
Honor a directly requested custom title while retaining the computed projection separately; a custom title changes no state.

## Supported native action

Use the current client's supported rename-chat action and its actual schema.
For `mcp__codex_app__set_thread_title` or `codex_tui.set_thread_title`, pass `title` and omit `threadId` to target this chat.
In the Claude desktop app's Code tab, use `mcp__ccd_session_mgmt__set_session_title` with `session_id` `"self"`, then read back with `get_session` `"self"`; observed working on 31 October 2026.
An equivalent exposed native current-chat operation is acceptable; never invent an API or directive.
When a stable ID is required, use the calling thread ID supplied by the runtime, never a title match.
If the current title is actually observed to equal the computed title, report UNCHANGED without a redundant mutation.
When no native tool exists, record UNAVAILABLE and the proposed title; keep the reply's state declaration accurate.
Do not scan unrelated chats or session logs, run another app server, or edit internal files/databases as a fallback.
No file, project or peer-chat rename, new chat, worktree change or routing follows from this operation.
Respect denials; do not try another access route to evade them.

## Outcome receipt

| Outcome | Required evidence |
| --- | --- |
| RENAMED | Native action explicitly acknowledged success; retain requested title and actual result. |
| UNCHANGED | Current native title was observed to equal the requested title. |
| UNAVAILABLE | No supported exposed native rename action was available. |
| FAILED | The attempted action returned an explicit error or denial. |
| UNKNOWN | Attempted action had no conclusive outcome; do not invent success or retry blindly. |

Verify through supported current-chat readback when available; otherwise say UI readback not inspected.
If native evidence shows title clipping, report the mismatch. When the readback is only a shortened preview, do not assume the stored title changed.
Record computed, requested and observed titles separately. Report any client limit without changing the role label or inventing a subject selection.
Retain computed title, last observed title, actual action outcome and any mismatch in this conversation's receipt.
A stale title after failure does not roll back role, subject, attitude or expiry.
Reconcile only at a later authorized selection, explicit retry or expiry with suitable evidence; never turn Status into a silent mutation.
On recovery use the receipt, not the label. See the [native protocol reference](https://developers.openai.com/codex/app-server/); exposure depends on the client.
