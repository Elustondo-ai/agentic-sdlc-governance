# Verify the ASDG–OpenSpec wrapper

These are bounded checks, not claims that they have run. Use a disposable client for write exercises; never create a real feature proposal merely to test installation.
The [workflow diagram](images/proposal-flow.svg) shows the integration boundary; the [canonical skill](SKILL.md) supplies the procedure.

| Scenario | Evidence to inspect |
| --- | --- |
| Native discovery | The current Codex catalogue lists `openspec-propose`; distinguish that from opening its file. Missing discovery stops the wrapper. |
| Portable installation | Normal ASDG initialization copies the thin adapter; it resolves after relocation. Existing native OpenSpec files and state are unchanged. |
| Clear fixture request | Use the installed workflow's resolved paths and artifact graph; create the required set, validate it, and check links to fixture ASDG evidence. |
| Accepted and draft mix | Source table matches current hashes and exact review coverage; unregistered files and stale acceptances are not labeled accepted. |
| Material conflict | A draft requiring explicit confirmation versus accepted automatic promotion produces a review question before scaffolding. |
| Missing evidence | A missing unrelated stage remains a limitation; a missing decision that changes observable behavior pauses drafting. |
| Existing name or missing root | Follow upstream collision/setup handling; do not overwrite, install or initialize silently. |
| Boundary and preservation | Application, upstream skills, ASDG state and hook bytes match their starting snapshots; no apply/sync/archive or sprint transition occurs. |

Record actual commands, versions, paths, statuses and limits. CLI validation proves only the rules it checks; a self-authored fixture is not an independent behavior test or human acceptance.
Do not claim separate-store, failed-tool, fresh-picker or resume behavior unless exercised in that environment.
