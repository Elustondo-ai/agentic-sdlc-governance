# Create confirmed missing team chats

Use only within [Create team](SKILL.md), after project and reuse verification.

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

