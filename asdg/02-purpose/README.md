# Purpose Agent — package

Native name: `asdg_02`. Stable role: `ASDG-02`.
This folder owns the specialization, not the consuming project's results.

| Entry | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Role entry point, boundaries and self-explanation |
| [docs](docs/README.md) | Package guide and relevant shared material |
| [types](types/contract.md) | Input/output contract; no mandated type language |
| [src](src/README.md) | Package-specific operations, when implemented |
| [tests](tests/acceptance.md) | Role interview and negative-boundary acceptance cases |
| [local skill](skills/elicit-purpose/SKILL.md) | Bounded procedure, explicitly loaded by this agent |

Shared [presentation](../skills/asdg-presentation/SKILL.md) and
[component](../skills/asdg-component/SKILL.md) capabilities remain single-source.
Using a capability does not grant its caller a new responsibility or write authority.

## Review

Ask Codex to spawn `asdg_02`, read this package and introduce itself.
Ask an in-scope question, then request an excluded deliverable.
Expect a truthful proposal or an `OUT_OF_SCOPE` return, never fabricated execution.
Current mode is read-only evaluation; native behavior after this migration is not yet tested.
See [package catalogue](../README.md) and [runtime rules](../00-governance/docs/runtime-contract.md).

## Purpose and three perspectives

Purpose asks why the system exists and what outcomes it should enable; it does not select architecture.
Use [Intended / Actual / Planned](../00-governance/docs/stage-perspectives.md) for the target project.
The canonical package is `02-purpose`, native role is `asdg_02`, and procedure is `asdg-elicit-purpose`.

## Perspectives

The stage keeps [Intended](intended/), [Current](current/) and [Planned](planned/) material in separate folders.
Empty folders make no evidence or completion claim; use the [shared contract](../00-governance/docs/stage-perspectives.md).
