# ASDG state engine: observe, guard, guide

Reusable implementation lives only in the methodology repository, under `asdg/00-governance/`.
`src/cli_status.py:project_status` evaluates authoritative project/sprint/evidence files.
`cli_policy.py:implementation_permission` calculates permission for the CLI guard, hook and views.
The deterministic engine owns facts/gates; `status` adds advisory coordinator output via the Codex SDK.

## Authoritative inputs and model

- `.asdg/project.json`: existing provider binding and stage layout.
- `.asdg/sprint.json`: existing authoritative sprint identity, scope and acceptance criteria.
- `.asdg/lifecycle.json`: stage evidence references; see [evidence format](lifecycle-evidence.md).
- `docs/asdg/<stage>/`: referenced project evidence, not copied methodology implementation.
- `.codex/hooks.json` and config: observable guard configuration; runtime trust remains UNKNOWN.
- Canonical methodology labels/order: `docs/status/lifecycle-baseline.md` and agent catalogue.
- `types/lifecycle-rules.json`: explicit actions/evidence requirements sourced to stage contracts.

Status includes project name/root, provider/version, structure, inferred stage, lifecycle readiness,
sprint status/ID/objective/scope/criteria, permission/reason, blockers, missing evidence,
guard configuration/trust, recommendation/reason and UTC evaluation timestamp.
The inferred stage is the earliest unmet evidence area; it is not an asserted team activity.
Evidence presence, execution, human approval and lifecycle completion remain distinct.

## Explicit recommendation rules

1. Invalid structure/state/methodology rules: repair the reported error first.
2. Otherwise select the earliest stage without registered, existing, non-empty evidence.
3. Stage 06 alone permits an explicit unnecessary-POC reason, as the canonical baseline allows.
4. Stages 01–06: recommend the corresponding contract's work, in canonical order.
5. From planning onward with no active sprint: define/review the plan and start scoped work.
6. With active sprint: recommend the earliest unmet stage; Stage 09 recommends scoped build/test.
7. With all twelve evidence areas established: review evidence and select the next roadmap/cycle.
An early active sprint does not fabricate missing evidence. Its path permissions remain restricted;
missing lifecycle evidence guides work but is not an additional implicit approval/write gate.

## Views and exit codes

`asdg status` prints facts, then concise advice; `--verbose` saves a [bounded report](status-advice.md).
`status --json` and `--facts-only` skip AI; `--json --advise` adds it. `next [--json]` stays deterministic.
`asdg sprint status` uses the same model's sprint. Start/stop remain explicit human CLI operations.
`asdg verify` and automatic init verification retain the shared structural inspection path.
A policy block is normal status (exit 0); invalid state or unavailable requested advice exits 1.
`asdg sprint check-implementation --path <target>` exits 1 when blocked and includes next guidance.
`asdg dashboard [--port 8765]` runs read-only on 127.0.0.1; `/` renders HTML, `/status.json` renders
fresh evaluator JSON. No mutation routes, browser scripting or external assets/dependencies exist.
It refreshes every 30 seconds, rejects non-loopback Host headers, escapes text and serves no files.

## Limits

Runtime hook trust cannot be proven from files; local policy is not an adversarial OS boundary.
Evidence indexing checks presence, not semantic quality or human approval; registration is manual.
This is a first ordered-cycle heuristic, not a complete product roadmap/sprint state machine.
Later-stage 11/12 requirements derive from the baseline; detailed contracts are absent.
See [sprint gate](sprint-gate.md) for activation and tool coverage; [verification](state-engine-verification.md).
