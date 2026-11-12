# ASDG — portable methodology

> **Historical snapshot — not the active ASDG distribution.** The package and instructions below are retained for historical reference. For the current methodology and installation, use the [ASDG repository](https://github.com/Elustondo-ai/asdg) and [ASDG Wiki](https://github.com/Elustondo-ai/asdg/wiki).

ASDG carries twelve lifecycle stages, specialist responsibilities, evidence rules and sprint controls inside your project.
The historical source repository for this snapshot is [agentic-sdlc-governance](https://github.com/Elustondo-ai/agentic-sdlc-governance).
This consolidated pilot is a review candidate; packaging does not establish human approval or native enforcement.

![A verified ZIP carries one asdg folder into the developer's Git repository, where initialization creates local integrations and state.](docs/images/distribution-flow.svg)

## Start

Extract the ZIP so your existing Git root contains `asdg/scripts/init.py` beside the application files.
Python 3.9+ and Git are required. From that root, run:

```sh
python3 asdg/scripts/init.py --client codex --dry-run
# After reviewing and explicitly approving that plan:
python3 asdg/scripts/init.py --client codex --apply --plan TOKEN_FROM_PREVIEW
python3 asdg/scripts/cli.py verify
```

Choose `codex`, `claude` or explicitly `both`; preview is the default and application requires the exact plan token.
An existing canonical clone at an explicitly selected commit uses the same engine; see [installation](docs/installation.md).
First setup records a new project without starting a sprint; use `--project-status defining` for an existing project.
Repeat initialization preserves state and authored files. Conflicts stop setup; different versions require a reviewed upgrade.
ZIP installs need no sibling checkout or global command. Review and trust Codex hooks separately in the native client.

## Included

Governance 00, stages 01–12, an explicit methodology Admin role, shared skills, client adapter templates,
the initializer, deterministic status/evidence engine, sprint checks and activity recorder.
Optional SDK advice and OpenSpec integration require their own dependencies and explicit workflows.
Presentation/video production, component authoring and legacy provider automation stay in the canonical repository outside this core ZIP.
Client evidence belongs in `docs/asdg/`; durable workflow state belongs in `.asdg/`; disposable logs belong in `logs/`.

## Read next

- [Installation and ownership](docs/installation.md) and [client integrations](docs/client-integrations.md).
- [Workflow usage](docs/usage.md), [Codex setup prompt](CODEX-PROMPT.md) and [lifecycle baseline](docs/lifecycle-baseline.md).
- [Build and verification](docs/distribution-build.md), [source provenance](docs/provenance.md) and [review loop](docs/review-loop.md).
- [Promote and upgrade](docs/synchronization.md): preview local methodology differences and explicitly apply a reviewed, conflict-free plan.
- [Historical pilot checks](docs/verification.md) and [native integration limits](docs/native-integration.md).

Skill notation is `$name` in Codex and `/name` in Claude Code. Session roles and attitudes grant no extra authority.
Installation creates no sprint, release, human approval, specialist session or hook trust.
