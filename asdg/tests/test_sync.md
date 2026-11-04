# Promote and upgrade integration tests

[Source: test_sync.py](test_sync.py) exercises both operations in disposable Git repositories with distinct origins and embedded methodology metadata.
The suite uses actual filesystem changes and CLI subprocesses; no real repository, remote service or model is modified.

![Tests exercise comparison, preview and explicit application while preserving client-owned areas.](../docs/images/synchronization.svg)

| Fixture or collaborator | Responsibility |
| --- | --- |
| `SyncTests.setUp`, `commit`, `refresh`, `edit` | Create temporary repositories, controlled baselines, versioned files and source/local variations. |
| `git`, `tree` | Inspect local Git and exact non-Git bytes for preservation checks. |
| `preview`, `apply`, `row` | Call the shared synchronizer, pass the reviewed digest and locate a reported path. |
| Portable CLI and selected package | Test parser modes and a real initialized Codex/Claude client's version upgrade and structural verification. |
| Existing file transaction | Inject failed creation/stream setup, an interrupted partial write and a replacement failure after deletion; verify cleanup, descriptor closure, prior-write rollback and preservation of unrelated replacement inodes. |

Checks cover identical copies, new/updated/deleted files, local-only edits, conflicting edits, untracked collisions and deletion protection.
Missing/invalid/nested roots, missing origins, identity/version/binding errors, malformed catalogues and corrupt adoption records fail safely.
Dry runs preserve tree bytes and Git index; stale/missing plan digests and stale canonical manifests block apply.
Manifest freshness tests distinguish working snapshots from manifest-matched content in JSON, console and adoption records without inferring validation or approval.
Repeated apply is idempotent. Source and target are exercised in both directions; application files, client evidence, workflow state and integrations remain intact.
Older tracked-only pilots use exact shared delivery manifests; absent or ambiguous historical ancestry blocks different existing content. Current endpoint manifests take precedence over older archives.
The full-package fixture explicitly previews and approves initialization before testing synchronization.
A full-package upgrade changes version metadata and runtime version, then runs the target's own `verify` while preserving all non-distribution bytes.
Temporary fixtures clean up themselves. These checks do not prove native agent invocation, hook trust, human approval or release readiness.

Run `python3 -B -m unittest discover -s asdg/tests -p test_sync.py -v` from the repository root.
