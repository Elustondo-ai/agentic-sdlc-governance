AI-MODIFIED - 2026-10-10T04:17:45Z

# High-Level Architecture Agent — package

Native name: `asdlc_05`. Stable role: `ASDLC-05`.
This folder owns the specialization, not the consuming project's results.

| Entry | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Role entry point, boundaries and self-explanation |
| [docs](docs/README.md) | Package guide and relevant shared material |
| [types](types/contract.md) | Input/output contract; no mandated type language |
| [src](src/README.md) | Package-specific operations, when implemented |
| [tests](tests/acceptance.md) | Role interview and negative-boundary acceptance cases |
| [local skill](skills/propose-architecture/SKILL.md) | Bounded procedure, explicitly loaded by this agent |

Shared [presentation](../skills/asdlc-presentation/SKILL.md) and
[component](../skills/asdlc-component/SKILL.md) capabilities remain single-source.
Using a capability does not grant its caller a new responsibility or write authority.

## Review
Ask Codex to spawn `asdlc_05`, read this package and introduce itself.
Ask an in-scope question, then request an excluded deliverable.
Expect a truthful proposal or an `OUT_OF_SCOPE` return, never fabricated execution.
Current mode is read-only evaluation; native behavior after this migration is not yet tested.
See [package catalogue](../README.md) and [runtime rules](../00-governance/docs/runtime-contract.md).
