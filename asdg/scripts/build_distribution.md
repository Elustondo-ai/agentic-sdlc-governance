# Build a portable ASDG ZIP

`build_distribution.py` selects and verifies the canonical package before creating a local artifact.
It uses Python's standard library and makes no network or model requests.

![Reviewed package files become a verified ZIP, then a locally initialized client.](../docs/images/distribution-flow.svg)

| Interface | Responsibility and effects |
| --- | --- |
| `refresh_manifest(core)` | Validate selected sources and record current hashes; changes only the current manifest, never delivery history or approval. |
| `build(core, output)` | Check integrity, freeze/recheck bytes, write deterministic ZIP entries and a checksum sidecar; returns the ZIP path. |
| `main()` | Parse `--output` and explicit `--refresh-manifest`; report failures with nonzero exit. |

The file-list resolver rejects traversal, symlinks, duplicates and missing files.
The package checker validates links against selected files, so a provider-only file cannot hide a missing dependency.
Archive entries begin with `asdg/`, use stable timestamps and regular-file permissions, and preserve source bytes.
Building may replace the same version's local artifact; it never publishes it or modifies client state.
Run the [distribution tests](../tests/test_distribution.md) to check exclusion, reproducibility and extraction behavior.
