# Portable integration tests: client selection cases

[Main case guide](test_portable-cases.md) · [Module guide](test_portable.md) · [Source](test_portable.py) · [Client integrations](../docs/client-integrations.md)

These `PortableTests` methods cover `--client codex|claude|both` in disposable fixtures. Each takes `self`, returns `None` and uses unittest assertions.
Helpers: `fresh_client(name)` makes another fixture project, `integrations()` reads the recorded clients and `statuses(expect)` reads each client's verify status.
They show file effects and reported status, not native discovery in either client.

| Test method | Responsibility |
| --- | --- |
| `test_fresh_setup_installs_only_the_selected_clients` | Codex-only, Claude-only and combined setups create only their own files and no `CLAUDE.md`; verify and the guard status match the selection. |
| `test_clients_add_in_either_order_without_touching_the_other` | Adding Claude after Codex, or Codex after Claude, leaves the first client's files byte-identical and records both. |
| `test_repeat_setup_and_dry_run_create_nothing_new` | Dry runs write nothing; repeat setup, with or without `--client`, changes nothing, keeps the selection and duplicates no receipt. |
| `test_invalid_client_is_rejected_before_any_write` | An unknown client exits with an argument error and no file changes. |
| `test_edited_client_files_conflict_and_verify_names_the_damaged_client` | An edited Claude adapter conflicts without writes; verify marks only the damaged client. |
| `test_codex_and_claude_adapters_resolve_the_same_canonical_skills_after_relocation` | After relocation, each skill's Codex and Claude adapters link to the same canonical `SKILL.md`. |
| `test_claude_invocation_controls_mirror_the_codex_policy` | `disable-model-invocation: true` appears exactly where Codex forbids implicit invocation, including Admin, Focus, Init and Status. |
| `test_legacy_codex_installation_is_recorded_explicitly` | A pre-tracking installation reports `legacy-unrecorded`; adding Claude records Codex as a legacy installation, says so and keeps its files. |
| `test_claude_bridge_is_added_only_when_claude_md_would_hide_agents_md` | No bridge without a suppressing file; a managed import is added once, a user's import is kept, edits conflict, and `.claude/CLAUDE.md` and `CLAUDE.local.md` cases are handled. |
