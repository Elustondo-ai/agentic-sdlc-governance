# Repository snapshots and adoption baselines

[Source: cli_sync_manifest.py](cli_sync_manifest.py) identifies exactly which local methodology bytes can participate in synchronization.
An adopted snapshot supplies ancestry without treating the target's local changes as upstream content.

![Repository snapshots and a common baseline feed the shared comparison and reviewed apply.](../../docs/images/synchronization.svg)

| Collaborator | Responsibility exchanged |
| --- | --- |
| Local Git | Read-only root, origin, HEAD and tracked-path inspection, bounded to 15 seconds. |
| Descriptor, file list, manifest | Provider/version identity, explicit distribution scope and historical content hashes. |
| Project binding | Read-only identity and initial adoption information from `.asdg/project.json`. |
| [Synchronizer](cli_sync.md) | Consumes bytes/hashes and persists a new adoption record only after explicit apply. |
| [Project inspection](cli_project.md) | Recognizes an adopted version without editing the original project binding. |

## Interfaces

| Callable | Contract |
| --- | --- |
| `digest(data)` / `encoded(value)` | SHA-256 of bytes (None stays None); deterministic UTF-8 JSON bytes. |
| `git(root, *args)` / `repository_id(remote)` | Reads local Git; normalizes HTTP(S)/SSH origins to host/path without storing credentials. |
| `methodology_path(name)` | Validates a distribution-relative path; rejects traversal, local adoption state and excluded project/build areas. |
| `read_json(path)` / `hash_map(value)` | Validates bounded JSON objects and path-to-SHA-256 maps; no writes. |
| `read_state(core)` | Returns schema-1 local adoption state or an empty state; corrupt identities or snapshot hashes fail. |
| `snapshot(location)` | Requires an exact Git root, identifiable origin/HEAD, versioned metadata and the thirteen stable lifecycle identities. Returns bytes, hashes, history, binding and a public identity summary. |
| `baseline(source, target)` | Uses a recorded adoption, otherwise an exact shared current manifest or one unambiguous shared archive; absent/ambiguous ancestry makes differing existing files conflict. |
| `adopted_binding(root, raw, version, catalog_hash)` | True only for an upgrade receipt matching this repository, original binding hash, adopted version and catalogue hash. |

An explicit package list may describe uncommitted candidate files. A legacy pilot without a list selects only Git-tracked ASDG paths.
Missing explicit members, symlinks, unsafe paths, malformed state and unverifiable identity/version raise `Conflict` or a caught JSON/filesystem error.
Manifest equality verifies content, not release approval; promotion additionally exposes the actual working snapshot when the old manifest is stale.
Public summaries identify WORKING_TREE_SNAPSHOT or MANIFEST_MATCHED_DISTRIBUTION, manifest SHA/version/status and path differences. Neither identity establishes validation or approval; both statuses remain NOT_ESTABLISHED.
Adoption records contain source commit/version/hashes and target identity/binding hash, never project evidence or application code.
`metadata/sync-state.json` must remain local to that project and is excluded from both distribution selection and archives.
This module reads no remote, executes no source-repository code and changes no Git or project state.
