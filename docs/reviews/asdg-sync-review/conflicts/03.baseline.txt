# ASDG Distribution — portable pilot 0.2.0-pilot.2

ASDG is Agentic Software Development Lifecycle Governance: twelve stages, specialist responsibilities,
evidence rules and sprint controls carried inside your client repository.
This pilot is an iteration baseline, not a claim of production enforcement or approved methodology.

## Start

Unpack this one `asdg/` folder beside the client's application files, inside its existing Git root.
Python 3.9+ and Git are required. Bootstrap uses the standard library and makes no model calls.
For the fresh Speaker Coach project, run from its root:

```sh
python3 asdg/scripts/init.py --project-status defining --dry-run
python3 asdg/scripts/init.py --project-status defining
python3 asdg/scripts/cli.py status --facts-only
python3 asdg/scripts/cli.py verify
```

The status declaration is explicit: project defining, release none, sprint inactive, evidence unregistered.
For a truly new project, omit `--project-status`; its initial project state is `new`.
Repeat initialization preserves state and refuses conflicting configuration.
Use this local CLI path; an existing global `asdg` command may still point to the old checkout.

## Included

Governance 00, all twelve stages, thirteen role definitions and local procedures, Focus/Status skills,
the initializer, status/evidence engine, sprint transitions, guards and central activity recorder.
The optional existing Codex SDK advice adapter is retained; deterministic operation needs no SDK.
Presentation/video production, historical work reports and the external-source baseline generator are omitted.

## Read next

- [Codex handoff prompt](CODEX-PROMPT.md): copy into a general Codex conversation in this client.
- [Installation and ownership](docs/installation.md): generated files, conflict handling and native trust.
- [Workflow usage](docs/usage.md): focus, status, sprint scope and optional advice.
- [Lifecycle baseline](docs/lifecycle-baseline.md): exact twelve-stage order.
- [Review loop](docs/review-loop.md): the embedded folder evolves through bounded local iterations.
- [Verification](docs/verification.md): executed checks and remaining native-runtime work.
- [Source and changes](docs/provenance.md): selected snapshot, exclusions and adaptations.

Runtime Python lives in `scripts/`, package records in `metadata/`, and verification in `docs/`.
Keep `asdg/`, `.asdg/`, discovery adapters and engineering documents in Git; ignore disposable `logs/`.
No sprint, release, human approval, specialist session or hook trust is created by extraction.
