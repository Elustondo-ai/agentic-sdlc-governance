# Purpose Agent — package

Native name: `asdg_02`. Stable role: `ASDG-02`.
This folder owns the specialization, not the consuming project's results.

| Entry | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Role entry point, boundaries and self-explanation |
| [docs](docs/README.md) | Package guide and relevant shared material |
| [types](types/contract.md) | Input/output contract; no mandated type language |
| [Completion](types/completion.md) | Agent readiness criteria and User acceptance of the exact baseline |
| [src](src/README.md) | Package-specific operations, when implemented |
| [tests](tests/acceptance.md) | Role interview and negative-boundary acceptance cases |
| [local skill](skills/elicit-purpose/SKILL.md) | Bounded procedure, explicitly loaded by this agent |

Shared [documentation](../skills/asdg-documentation/SKILL.md) remains single-source.
Using a capability does not grant its caller a new responsibility or write authority.

## Review

Ask Codex to spawn `asdg_02`, read this package and introduce itself.
Ask an in-scope question, then request an excluded deliverable.
Expect a truthful proposal or an `OUT_OF_SCOPE` return, never fabricated execution.
Purpose documentation authoring is allowed under the contract; native behavior after this change is not yet tested.
See [package catalogue](../README.md) and [runtime rules](../00-governance/docs/runtime-contract.md).

## Purpose and three perspectives

Purpose asks why the system exists and what outcomes it should enable; it does not select architecture.
Use [Intended / Actual / Planned](../00-governance/docs/stage-perspectives.md) for the target project.
The canonical package is `02-purpose`, native role is `asdg_02`, and procedure is `asdg-elicit-purpose`.

## Perspectives

Client Purpose documents follow the [stage layout](../00-governance/docs/stage-layout.md), one file per concept:
`01-purpose.md`, `02-current-capabilities.md` and `03-planned-improvements.md`, linked from `README.md`.
Name sprint-specific work `03.N-sprint-<topic>.md`; create additional documents only when needed.
Every completed Purpose delivery includes an explanatory image near the opening of `01-purpose.md`, from the local `images/` subfolder.
Use a vision/current-state caption and alt text; inspect image quality and the rendered document when available.
Reuse a suitable image across wording updates. A text-only draft is incomplete; report unavailable tools or preview checks.
These express the [shared perspectives](../00-governance/docs/stage-perspectives.md) using names specific to Purpose.
