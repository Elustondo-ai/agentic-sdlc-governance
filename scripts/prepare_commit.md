# Prepare a provider commit or push

`python3 scripts/prepare_commit.py` regenerates the portable ZIP and SHA-256 sidecar before each commit/push, using Python 3.9+ and the standard library.
The command works from any current directory when invoked by its correct path. It is a provider-only convenience script.

![The existing builder selects and verifies the portable ASDG package.](../asdg/docs/images/distribution-flow.svg)

| Interface | Responsibility and effects |
| --- | --- |
| `prepare(root)` | Run that provider root's existing builder with `--refresh-manifest`; propagate subprocess failure. |
| `main()` | Locate this checkout, report success or failure, and explain the remaining human actions. |

The existing builder owns selection, validation, deterministic archive construction and checksum generation; this wrapper adds no second packaging engine.
It refreshes `asdg/metadata/MANIFEST.json` and replaces the current version's ignored artifacts in `build/distributions/`.
Review the manifest and include it in the commit. Re-run after any further selected-package edit and before pushing; preparation does not stage or commit the manifest.
An unchanged package produces identical ZIP bytes even though the ZIP is regenerated. This command does not increment the distribution version.
A build failure exits nonzero. The refreshed manifest and generated outputs are local candidate evidence, not approval or proof that a commit was published.
No Git hook is installed: the repository instructions require this explicit preparation command; invocation is not automatic.
Commit, push, version selection and release-asset publication remain separate human actions. The ZIP contains current working-tree bytes, which may include uncommitted edits.

See [build policy](../asdg/docs/distribution-build.md) and [tests](tests/test_prepare_commit.md).
