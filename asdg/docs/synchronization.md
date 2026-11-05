# Promote and upgrade local methodology

Maintainers use `promote` to bring pilot improvements into the canonical repository and `upgrade` to adopt a reviewed canonical distribution in a pilot.
Both commands use the same conservative file comparison; neither decides that one project's methodology is better.

![Pilot and canonical snapshots are compared with an adopted baseline; review precedes explicit application and a local adoption record.](images/synchronization.svg)

The conversational [Update skill](../skills/asdg-update/SKILL.md) guides approved upgrades and a separate integration preview for new command adapters; it preserves the engine prerequisites below.

## Preview, review, apply

Use Python 3.9+ and Git. Run the current project-local entry point; no global command or model is required.
Supply absolute Git roots, each with an identifiable HTTP(S)/SSH `origin`, a HEAD commit and an embedded versioned distribution.
The canonical descriptor's `canonical_repository` must match its origin. The pilot must have a valid `.asdg/project.json` binding.

```sh
python3 -B asdg/scripts/cli.py promote --source /path/to/pilot --target /path/to/canonical --dry-run
python3 -B asdg/scripts/cli.py upgrade --source /path/to/canonical --target /path/to/pilot --dry-run
```

Review every added, modified, deleted, unchanged and conflicting path. `unchanged` also identifies retained local changes.
Add `--json` for machine-readable hashes, identities, baseline, counts and `plan_id`; conflicting previews exit 1 while still emitting the report.
After explicit authorization, repeat the selected command with `--apply --plan <plan_id>` instead of `--dry-run`.
The digest must match a fresh comparison. Any conflict blocks the entire apply; there is no force option or automatic content merge.
Reconcile differences explicitly, then preview again. A changed file, HEAD, binding or receipt invalidates the old plan.

## Distribution and preservation

Only files selected by `asdg/metadata/package-files.json` participate; older pilots without it use Git-tracked methodology paths under `asdg/`.
The first comparison prefers an exact shared current delivery, otherwise one unambiguous shared archive; absent/ambiguous ancestry makes differing existing files conflict.
Source-only changes apply when the target still matches the baseline. Target-only changes are retained; changes on both sides conflict unless bytes agree.
Tracked deletions follow the same rule. An untracked target file is never deleted, and a differing untracked addition collision blocks copying.
Application code, `docs/asdg/`, `.asdg/`, installed adapters, hooks and root configuration are outside the write scope.
The source is never modified. Apply writes a local `asdg/metadata/sync-state.json` adoption record, excluded from synchronization and ZIPs.
Keep that record with the adopting project: it stores repository identities, source commit, exact incoming hashes and version for subsequent comparisons.
The incoming baseline remains separate from retained local edits. Repeating an unchanged applied operation writes nothing.

## Version and governance limits

Upgrade apply requires the canonical working tree to match its delivery manifest; [build and review](distribution-build.md) it first.
Promotion can preview a pilot whose delivery manifest is stale: the report identifies actual working bytes and warns about the mismatch.
Console/JSON identify WORKING_TREE_SNAPSHOT versus MANIFEST_MATCHED_DISTRIBUTION and MATCH/STALE delivery status; JSON lists the exact manifest differences. Adoption records preserve this distinction. Matching content does not establish tests or approval: both statuses remain NOT_ESTABLISHED.
A manifest or adoption receipt proves content identity, not human approval, validation quality, a release or permission to change governance.
An explicit reviewed apply adopts only those bytes. No command stages, commits, pushes, merges, tags, publishes or contacts GitHub.
Version upgrades are recognized through the adoption record without rewriting `.asdg/`; incompatible lifecycle state or client adapters can still fail `verify`.
Run `python3 -B asdg/scripts/cli.py verify` in the pilot afterward. Changed adapter templates require separate reviewed integration work.
Claude and Codex use the same Python files; this command does not establish native discovery, invocation or hook trust.
Writes use the existing rollback mechanism for ordinary failures; concurrent writers and power-loss recovery are outside its transaction guarantee.

See the [synchronizer](../scripts/lib/cli_sync.md), [identity and baseline reader](../scripts/lib/cli_sync_manifest.md) and [disposable tests](../tests/test_sync.md).
