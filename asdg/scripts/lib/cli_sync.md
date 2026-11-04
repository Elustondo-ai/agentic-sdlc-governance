# Conservative methodology synchronization

[Source: cli_sync.py](cli_sync.py) shares one deterministic implementation between upstream promotion and downstream upgrade.
It plans local distribution edits, retains local differences and applies only a conflict-free, explicitly reviewed snapshot.

![Both synchronization directions compare source, baseline and target before review and explicit apply.](../../docs/images/synchronization.svg)

| Collaborator | Responsibility exchanged |
| --- | --- |
| [CLI dispatcher](cli.md) | Selects direction, endpoints, preview/apply mode and review digest; prints text or JSON. |
| [Snapshot reader](cli_sync_manifest.md) | Validates repositories and bindings; supplies incoming bytes, hashes and common baseline. |
| [File transaction](cli_files.md) | Plans add/replace/delete operations, preflights current bytes and rolls back its own writes on ordinary failure. |

## Interfaces

| Callable | Contract |
| --- | --- |
| `endpoints(operation, source, target)` | Requires separate, nonnested Git roots, canonical origin identity and a valid embedded pilot binding; raises `Conflict`. |
| `classify(old, incoming, local)` | Accepts SHA-256 strings or None and returns `(status, reason)`; equal bytes are unchanged, source-only changes can apply, target-only changes remain local. |
| `preview(operation, source_path, target_path)` | Returns `(report, changes, source, target)` with no writes; checks actual destination bytes even for unlisted addition collisions. |
| `synchronize(operation, source_path, target_path, *, apply=False, expected_plan=None)` | Returns a JSON-ready report; apply requires matching digest, zero conflicts and, for upgrade, a current canonical delivery manifest. |
| `render(report)` | Produces all file statuses, reasons, totals, warnings and the review digest as text. |

Reports include source/target identity, HEAD, version, snapshot hash, baseline provenance and one row per relevant path.
Snapshot kind and manifest MATCH/STALE status appear in JSON, console preview and adoption records, with exact added/modified/deleted paths versus the manifest. Validation and human approval remain NOT_ESTABLISHED even for matching hashes.
Rows contain baseline/source/target hashes, target Git-tracked status and added/modified/deleted/unchanged/conflicting classification.
`plan_id` hashes the report before adding execution results. A second comparison immediately before writing detects changed inputs.
Apply records the incoming snapshot in local `metadata/sync-state.json`, separately from any retained target edits.
No Git mutations, network operations, source writes or application-state changes occur; deletion requires a baseline and a tracked target.
Conflicts and invalid inputs raise `Conflict`; JSON/filesystem errors propagate to the dispatcher. There is no force mode or content merge.
Per-file writes reuse existing mode preservation and ordinary-failure rollback, without claiming a crash-safe or concurrent-writer transaction.

See [usage](../../docs/synchronization.md) for commands and [tests](../../tests/test_sync.md) for executed scenarios.
