# Using and maintaining embedded ASDG

This directory is the client's local methodology distribution, not the client application's evidence.
The client root `AGENTS.md` loads this file through its ASDG bootstrap block; also follow the project-owned guidance after that block and the user's explicit task.
Read [the lifecycle baseline](docs/lifecycle-baseline.md); preserve governance 00 and stages 01–12. No external provider checkout is required.
Use [the catalogue](00-governance/types/agent-catalog.json) for identities and paths; Stage 02 is Purpose.

## Startup sources

Before project work, read this file, then [the session policy](skills/asdg-focus/session-policy.md), again on every turn, and [session fields](skills/asdg-focus/session-state.md).
Every session acts under an accountable role: 00 Governance by default, or a specialist only after explicit selection loads it.
Read the selected role's entry, local procedure, [runtime contract](00-governance/docs/runtime-contract.md) and response envelope in full; [Governance's entry](00-governance/AGENTS.md) lists its own.
A missing or contradictory startup source blocks dependent work as `BLOCKED: GOVERNANCE_BOOTSTRAP`; read-only diagnosis stays allowed.
In initialized clients, run `python3 asdg/scripts/cli.py status --json` before substantial work; a global `asdg` may be older. In the canonical provider, follow its root maintenance and package checks instead.
`python3 asdg/scripts/cli.py verify` checks structure only; folders and passing checks do not prove compliance.

## Client work

Keep goal, role, subject focus and attitude separate in this chat's receipt; title changes reflect selections and explicit expiry, never grant authority.
Every agent may save project documentation under `docs/` without an active sprint or separate save approval; follow [documentation authority](00-governance/docs/documentation-authority.md).
Purpose Focus begins a read-only opening assessment; assigned Purpose work produces saved client documentation.
Use the [continuation contract](00-governance/docs/continuation.md); other specialist openings await the pilot review.
Human-directed [Sprint start](skills/asdg-sprint-start/SKILL.md), [review](skills/asdg-sprint-review/SKILL.md) and [close](skills/asdg-sprint-close/SKILL.md) preserve Focus and specialist delivery boundaries.
Use client sources as evidence; definitions in this folder never establish application behavior.
Apply [Intended / Actual / Planned](00-governance/docs/stage-perspectives.md) to the stated client subject.
Skills are written `$name` here, as in Codex; in Claude Code invoke them as `/name`, per [client integrations](docs/client-integrations.md).
`$asdg-status` combines project facts with session progress; `$asdg-role` explains the current role's mandate; [`$asdg-admin`](skills/asdg-admin/SKILL.md) explicitly switches to ASDG Admin, and `$asdg-admin clear` returns to Governance.
Keep client artifacts in `docs/asdg/` and durable state and review history in `.asdg/`, preserving both; root `logs/` holds disposable activity records, and no role may claim complete logging without evidence.

## Implementation gate

Before any application edit, follow the [sprint gate](00-governance/docs/sprint-gate.md) and check every target with `python3 asdg/scripts/cli.py sprint check-implementation --path <target>`.
Without an active scoped sprint, implementation is blocked; only an explicit human decision starts or stops a sprint, and a sprint never widens a role's authority.
Never edit `.asdg/` state, hook definitions or ASDG policies as application implementation; Codex hooks enforce nothing until a human reviews and trusts them.
Installation, passing checks and proposals grant no approval, publication, commit, push, deletion, deployment or hook trust.

## Documentation rules for every adopting project

Governance 00, all twelve specialists and methodology maintainers must follow the [documentation standard](00-governance/docs/documentation-standard.md).
All reader-facing `docs/asdg/` artifacts explain the project to humans, with useful embedded visuals and technically precise prose.
Material decisions across all roles use [ASDG Decision](skills/asdg-decision/SKILL.md), with generic defaults and an [optional local specialization](skills/asdg-decision/specialization.md); role authority remains unchanged.
Every maintained source file requires a [CRC-inspired Markdown companion](00-governance/docs/code-companions.md), kept current with the code.
Documentation, guides and designs for a graphical interface open with who uses it and a captioned [representative visual](00-governance/docs/gui-visuals.md).
Apply the [documentation review criteria](00-governance/docs/documentation-review.md) before claiming documentation complete; initialization alone proves no compliance.
These portable requirements travel with this distribution and do not depend on SpeakerCoach or an external provider checkout.

## Explicit ASDG maintenance

Agent changes to these definitions run only under explicitly selected [ASDG Admin](admin/AGENTS.md) within a human-authorized scope; any role may propose them.
Maintaining a definition never activates the specialist whose file is edited, and no agent selects Admin to escape a restriction.
The canonical methodology repository produces the reviewed distribution; each client owns its versioned embedded copy.
Record bounded changes; propose reusable improvements upstream. Never overwrite client changes or state during an upgrade.
Keep canonical skills here; native discovery adapters remain thin references generated from `templates/`.
Preserve state, evidence, user configuration and prior review records through changes.
Read [the iteration contract](docs/review-loop.md) before preparing a local maintenance handoff.
Preserve code, approval and state-transition gates; documentation authority does not start a sprint.
Run the relevant tests and distinguish configured, observed, tested and human-approved results.
Record edited documentation with exact hashes; never transfer an old approval to new bytes.
Keep YAML front matter first. Do not add human approval without an exact-state decision.
