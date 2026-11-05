# Distribution boundary tests

These tests build the actual ZIP and install its extracted bytes in unrelated temporary Git repositories.
They exercise the developer promise without relying on a sibling provider or globally installed launcher.

![The tests follow the provider-to-ZIP-to-client installation path.](../docs/images/distribution-flow.svg)

| Check | Evidence produced |
| --- | --- |
| Repeated builds | Stable bytes and checksum; every member comes from the explicit file list. |
| Approval instructions | ZIP contains the exact current canonical Init skill and both reusable prompts. |
| Exclusions | Unlisted provider files never enter the archive. |
| Stale or missing bytes | Build fails before creating an artifact. |
| Unsafe selections | Traversal, symlink, duplicate members and project-local adoption records are rejected. |
| Link closure | A file present only in the provider cannot satisfy a portable link. |
| Extracted installation | Codex-only, Claude-only and combined setups initialize and verify. |
| Relocation and repeat | Paths with spaces/apostrophes work; authored guidance, application bytes and state remain identical. |

The fixture copies only selected source files, records fixture hashes and cleans up its own temporary directories.
Initialization fixtures explicitly preview and apply the returned token; production defaults remain read-only.
CLI subprocesses use the current Python interpreter and a 30-second limit; no model or network calls occur.
These checks do not demonstrate native discovery, tool interception, hook trust or human acceptance.
Run `python3 -B -m unittest discover -s asdg/tests -p test_distribution.py -v` from the repository root.
