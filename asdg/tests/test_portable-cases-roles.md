# Portable integration tests: role and session cases

[Main case guide](test_portable-cases.md) · [Module guide](test_portable.md) · [Source](test_portable.py)

These `PortableTests` methods cover the 00 Governance default, the governance bootstrap gate and the separate ASDG Admin package.
Each takes `self`, returns `None` and uses unittest assertions. Names describe the checks; this index is not an execution result.
Text-consistency cases show that instructions say the right thing, not that an agent obeys them.

| Test method | Responsibility |
| --- | --- |
| `test_new_session_bootstrap_reports_governance_default_ready` | A fresh client reports the 00 Governance default as READY, rejects a role-None state and labels enforcement instructional. |
| `test_missing_governance_source_blocks_bootstrap_and_implementation` | A missing coordinator contract reports `GOVERNANCE_BOOTSTRAP` and blocks the sprint check and guard for an in-scope file. |
| `test_entry_point_without_distribution_link_blocks_bootstrap` | A managed block without the `asdg/AGENTS.md` link, or a removed block whose project text mentions it, blocks the bootstrap. |
| `test_known_legacy_blocks_move_first_and_keep_project_text` | Each of the three earlier blocks, appended, alone or with text after it, moves to the top with a backup; project text is kept and repeat setup changes nothing. |
| `test_project_text_after_bootstrap_is_preserved_byte_for_byte` | CRLF, tabs, trailing spaces and UTF-8 in existing instructions survive setup exactly; later project additions survive repeat setup. |
| `test_edited_moved_or_duplicated_bootstrap_conflicts_without_writes` | An edited, moved or duplicated current block, or an edited legacy block, fails setup with a specific message, writes nothing and fails verify. |
| `test_bootstrap_template_is_generic_and_removed_rules_have_homes` | The bootstrap stays small and project-neutral; `asdg/AGENTS.md` links the startup sources, and every rule removed from the root has a stated home; text checks only. |
| `test_admin_role_is_registered_outside_the_lifecycle` | ASDG Admin is registered with explicit-only activation, no default, no native adapter and resolvable sources; the 13-role catalogue is unchanged. |
| `test_admin_skill_installs_relocates_and_is_explicit_only` | The `$asdg-admin` adapter installs from its template, survives relocation, keeps implicit invocation off and links to a canonical skill whose links resolve; repeat setup changes nothing. |
| `test_project_work_cannot_patch_asdg_rules_through_the_guard` | With an active sprint, the guard and sprint check deny patches to an ASDG rule and `asdg/` cannot be scope; this is role-agnostic. |
| `test_session_instructions_define_no_role_none_path` | Session, role and Admin instructions state the Governance default, title-sync triggers and Admin limits, with no role-None or old maintainer allowance; text checks only. |
| `test_documentation_writes_require_governance_bootstrap_but_no_sprint` | With no sprint, docs are allowed; a missing coordinator contract or session-state file blocks docs and code writes with the named source, while read-only commands stay allowed. |
| `test_valid_admin_package_passes_without_changing_catalogue_or_binding` | A valid Admin package passes verify and repeat setup; catalogue bytes and the project binding hash are unchanged. |
| `test_invalid_admin_package_fails_preflight_and_verify_with_diagnostic` | Missing, malformed, wrong-identity, non-explicit, default, extra-field, escaping-path or missing-source Admin cases fail verify and setup with a specific message and no writes. |
