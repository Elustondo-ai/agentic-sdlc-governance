# Select portable distribution files

`distribution_files.py` defines the shared file-selection boundary for validation and ZIP creation.
The provider may retain tools and history outside this list without shipping them to every client.

| Collaborator | Contract |
| --- | --- |
| `metadata/package-files.json` | Schema version 1 and a unique list of paths relative to `asdg/`. |
| `package_files(core)` | Returns sorted regular-file paths; raises on missing files, unsafe paths, symlinks or malformed lists. |
| Package checker | Uses the same selection for source checks, link closure and integrity comparison. |
| Distribution builder | Archives only this returned list beneath one `asdg/` directory. |

The list includes itself and the current manifest. The manifest excludes its own hash to avoid recursion.
Traversal, absolute paths, Git metadata, client state, local `metadata/sync-state.json` adoption records, logs, build output and Python caches are rejected.
Changing the list is a reviewable source edit; file presence alone never adds a file to a release.
See the [build workflow](../../docs/distribution-build.md) for the distribution diagram and commands.
