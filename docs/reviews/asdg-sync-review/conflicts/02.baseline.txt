# Using and maintaining embedded ASDG

This directory is the client's local methodology distribution, not the client application's evidence.
Follow the client root `AGENTS.md` and the user's explicit task. No external provider checkout is required.
Read [the lifecycle baseline](docs/lifecycle-baseline.md); preserve governance 00 and stages 01–12.
Use [the catalogue](00-governance/types/agent-catalog.json) for identities and paths; Stage 02 is Purpose.

## Client work

Read [the session policy](skills/asdg-focus/session-policy.md) on every turn.
A new conversation has no specialist focus. Only explicit invocation activates a named role.
Named roles and Focus retain read-only evaluation; do not turn an advisory request into execution.
Read the selected role, its local procedure, runtime contract and response envelope in full.
Use client sources as evidence; definitions in this folder never establish application behavior.
Apply [Intended / Actual / Planned](00-governance/docs/stage-perspectives.md) to the stated client subject.
Run `python3 asdg/scripts/cli.py status --json` from the client root for project/release/sprint facts.
`$asdg-status` describes conversation focus; the CLI describes recorded project workflow.
Use `docs/asdg/` for accepted client artifacts and `.asdg/` for durable state and review records.
Use root `logs/` for disposable activity records; no role may claim complete logging without evidence.
Check every implementation target through the sprint guard; hook trust is a separate runtime check.

## Explicit ASDG maintenance

Maintaining these definitions does not activate the specialist whose file is being edited.
The user has chosen this embedded folder as an evolving working baseline; record bounded changes here.
Do not silently pull or overwrite it from the old sibling repository, package or Google Drive source.
Keep canonical skills here; native discovery adapters remain thin references generated from `templates/`.
Preserve state, evidence, user configuration and prior review records through changes.
Read [the iteration contract](docs/review-loop.md) before preparing a local maintenance handoff.
Preserve existing governance boundaries; packaging repairs never grant role writes or start a sprint.
Run the relevant tests and distinguish configured, observed, tested and human-approved results.
Follow [the documentation standard](00-governance/docs/documentation-standard.md).
Record edited documentation with exact hashes; never transfer an old approval to new bytes.
Keep YAML front matter first. Do not add human approval without an exact-state decision.
Do not infer commit, push, publication, deletion or deployment authority from a proposal.
