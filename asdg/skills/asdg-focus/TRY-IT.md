# Twelve Focus skills and chat rename — acceptance checks

Scope: the existing agentic-sdlc-governance provider checkout and its current discovery adapters.
No consumer binding, native subagent TOML, lifecycle definition or execution permission is changed.
Wait for Drive sync. Select a named skill from the actual Codex picker; restart only if needed.
A skill/configuration file being present is not proof the app discovered or executed it.

## First test — separate messages

Supply `Target project: Speaker Coach` explicitly; the provider folder is not the consumer.
1. New conversation: `$asdg-status` → None, no role activation and no rename.
2. Select **ASDG Focus 02 — Purpose**, or send `$asdg-focus-02-purpose` with no argument.
3. Expect canonical ASDG-02 reads, retained project context and a native current-chat rename attempt.
4. Expected default for known Speaker Coach: `02 Purpose — Speaker Coach`.
5. `$asdg-status` → Purpose remains selected; actual rename receipt shown separately from focus.
6. `What is your role?` → grounded Purpose explanation; no reactivation required.
7. Request Intended / Actual / Planned for Speaker Coach Purpose; unknown evidence stays unknown.
8. Discuss one in-scope hypothetical task, then Status again → same focus and current substantive task.

## Other entries and boundaries

Test each of the twelve [picker entries](focus-choices.md) in a separate disposable conversation.
Verify its fixed role ID, required source reads, canonical exclusions and title prefix; no parameter menu.
Each currently remains read-only evaluation, including Build/Test, POC, Operations and Release.
Choose Architecture after Purpose → successful switch loads ASDG-05 and updates the title; project remains.
Unknown/conflicting selector or missing source → old focus/title remain; no false activation receipt.
Generic `purpose`, `02-purpose`, `intent`, `02-purpose`, `02`, `ASDG-02`, `asdg_02` remain compatible.
Generic command without a selector → points to named skills; no silent default or focus change.
`asdg-focus clear` → None plus General title attempt; no permission change or coordinator activation.
Status twice → no rename, activation or state change. New conversation does not inherit another's focus.
Manual title edit alone → no role change. Explicit title override in activation → honor that title.
Rename denied/unavailable → report it and keep successful focus. Uncertain outcome → no blind retry.
Repeated selection refreshes the same role and can retry a known failed/unavailable rename.
No rename path may touch project files, internal stores, other chats, deletion or archiving.

## Evidence

Record surface/version, picker labels, actual read/rename tool trace, before/after replies and UI title.
Record project-file diff separately; title metadata is not an application-source change.
Multi-turn retention, twelve runtime invocations, reload/resume/compaction need live tests; not assumed passed.
Pablo's earlier screenshot verifies direct user-requested rename on his app, not these updated skills.
Static syntax and references are a separate check. No file state is self-approved by this update.

[Official skills](https://developers.openai.com/codex/skills/)
[Native rename protocol](https://developers.openai.com/codex/app-server/)
