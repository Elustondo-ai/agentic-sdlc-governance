# Install ASDG in a client repository

Extract the zip once so the Git root contains `asdg/scripts/init.py`, alongside the existing application.
Do not nest it inside another `asdg/` or run it from the old governance project.
Use Python 3.9+ and Git on macOS/Linux. Windows and remote/cloud hook enforcement are unverified.
Nothing changes outside the selected client repository; no shell startup file or Python environment is edited.

| Location | Ownership |
| --- | --- |
| `asdg/` | Local versioned methodology, scripts, contracts, templates and tests |
| `asdg/scripts/` | Python entry points and supporting runtime modules |
| `asdg/metadata/` | Distribution records; original delivery manifest retained under `deliveries/` |
| `.asdg/` | Durable project/release/sprint/evidence state and document review history |
| `.agents/skills/` | Generated skill discovery adapters; canonical instructions stay in `asdg/` |
| `.codex/agents/` | Generated thirteen named-role adapters |
| `.codex/hooks.json` | Guard and attributed activity-log callbacks; trust must be verified locally |
| Root `AGENTS.md` | Client rules plus a bounded ASDG section |
| `docs/asdg/` | Client evidence and stage README scaffolds; existing documents are preserved |
| `logs/` | Ignored disposable records, centralized by session and child instance |

Run the [README commands](../README.md), or give Codex [the installation prompt](../CODEX-PROMPT.md).
The dry run validates all destinations and reports planned writes. A conflict causes no planned file writes.
Initialization refuses existing conflicting hooks, Codex config or adapters; it never resets them.
Existing instructions and ignore rules are retained; an edited ASDG managed block requires review.
An initial status argument does not change a previously recorded status.
Missing or malformed existing state and incompatible versions require explicit repair/migration.
This fresh-install pilot does not migrate `.asdlc/` or the old linked-provider installation.

## Native Codex checks

Open/reload the project in local Codex and inspect the skills picker and named-agent discovery.
Review the generated hook definitions through `/hooks`; only the human/native trust flow grants trust.
Confirm a harmless denied write in a disposable copy before relying on interception.
Structural verification and direct hook execution are different from native runtime enforcement.
The source guard blocks arbitrary shell/REPL execution, including builds and tests; run those in a human terminal.
After hooks become trusted, reinitialization/report writes may also require the human terminal.
Do not disable the guard merely to make a test or maintenance edit succeed.
Custom agents inherit parent permissions; advisory instructions do not create a separate sandbox.
See [native integration limits](native-integration.md) and the actual local runtime version.

## Repetition and upgrades

Repeat the same initializer to check/restore identical generated entries; valid state is preserved.
Deleting `logs/` loses observations only; it does not remove lifecycle or review history.
Review package updates as diffs against this local working baseline; never replace the folder wholesale.
Keep `.asdg/` across upgrades. Catalogue/version changes require a reviewed migration.
`python3 asdg/scripts/check.py --integrity` compares package bytes to the delivered manifest; edits are visible.
Ordinary status/verify remains usable for intentional local changes if contracts and generated adapters agree.
