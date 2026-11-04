# Commit preparation tests

These provider-only tests invoke the existing builder through the new wrapper in disposable directories.

| Scenario | Evidence |
| --- | --- |
| Changed selected Markdown | Manifest refresh permits a ZIP containing those exact changed bytes. |
| Repeat after replacing output with junk | ZIP is regenerated and equals the original deterministic build; checksum exists. |
| Missing selected package member | Failure propagates without creating an output directory. |
| CLI invoked from another directory, missing builder | Root follows the script location and CLI exits nonzero with a failure message. |

Fixtures copy only the selected portable files. No Git state, hooks, user configuration or network service is modified.
Run `python3 -B -m unittest discover -s scripts/tests -v` from the provider root.
See the [wrapper contract](../prepare_commit.md) and its [distribution flow](../../asdg/docs/images/distribution-flow.svg).
