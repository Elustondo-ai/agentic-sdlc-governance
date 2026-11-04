# Distribution metadata

These records describe the embedded ASDG distribution.
The client's durable workflow state remains in `.asdg/` at the project root.

| Record | Purpose |
| --- | --- |
| `distribution.json` | Distribution identity, version, layout and requirements |
| `MANIFEST.json` | Current candidate integrity hashes, not human approval |
| `package-files.json` | Explicit portable file list; excludes provider tooling and client state |
| `source-manifest.json` | Original source provenance and current path mapping |
| `deliveries/0.2.0-pilot.*.json` | Unchanged historical delivery manifests |
| `refactors/root-layout-2026-10-20.json` | Moves, modifications and verification of the root cleanup |

Integrity records do not grant human approval or execution permission.
