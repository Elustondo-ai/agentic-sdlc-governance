# Selectors, terminal commands and optional tools

Use this reference with [ASDG Help](SKILL.md). Chat skills guide a conversation; terminal commands invoke the local Python engine. Help explains both without executing them.

## Common chat selectors

Examples use Claude's `/`; substitute `$` in Codex. Read the linked skill for its full contract.

| Example | Meaning |
| --- | --- |
| `/asdg-focus Architecture` or `/asdg-focus 05` | Load the selected role and retain the other session fields. |
| `/asdg-focus clear` | Return the role to 00 Governance; preserve subject and attitude. |
| `/asdg-focus subject <topic>` / `subject clear` / `subject status` | Change, clear or report only the within-role topic. |
| `/asdg-attitude <color>` | Select White (facts), Red (intuition), Green (ideas), Yellow (benefits), Black (risks) or Blue (process). |
| `/asdg-attitude Green for this answer only` | Use an explicitly bounded attitude, then restore its prior value. |
| `/asdg-attitude NoAttitude` / `status` | Clear the attitude or report it without changing it. |
| `/asdg-update` | Prepare an update from a selected local canonical source; methodology and adapter application need separate exact-plan approval. |
| `/asdg-admin clear` | Leave Admin and load Governance. |
| `/asdg-status facts-only` | Request project/session facts without advice. |
| `/asdg-decision <question>` | Analyze a decision; explicitly request recording when that is the intended output. |
| `/asdg-openspec-propose <change>` | Request a bounded planning proposal; requires native `openspec-propose`. |

## Terminal command families

Run from the client Git root with `python3 asdg/scripts/cli.py <command>`. `--help` and `<command> --help` list exact current options; `--version` reports the local version.
These names are CLI commands, not slash skills. Prefer the conversational skill for installation, sprint changes and documented closeout. [Dispatcher reference](../../scripts/lib/cli.md) describes effects and collaborators.

| Command | Purpose / boundary |
| --- | --- |
| `init` | Preview integration; `--client codex\|claude\|both` selects clients. `--apply --plan <token>` requires explicit preview approval. |
| `status` | Project facts and optional advice; `--json` or `--facts-only` skips model advice unless requested. `--verbose` may save reports. |
| `verify` | Validate structure/integration; never establishes native operation or acceptance. |
| `next` | Report the deterministic next-stage registration heuristic; not a human decision or the Suggestion skill. |
| `agent list` / `agent describe <name>` | Inspect role definitions; never starts live agents. |
| `sprint status` | Inspect authoritative sprint state; accepts `--json`. |
| `check-write --context <JSON> --path <target>` | Read-only role ownership preflight; application targets also require sprint scope. |
| `sprint check-implementation --path <target>` | Check each proposed target against current scope; repeat `--path`. |
| `sprint start` | Writes scope/state; needs `--id`, `--objective`, repeated `--scope` and `--acceptance`, plus the sprint skill's authorization/preflight. |
| `sprint stop` | Stops sprint state; the Close skill additionally preserves review and carry-forward evidence. |
| `promote` / `upgrade` | Preview pilot-to-canonical / accepted-version-to-client synchronization with `--source`, `--target`, `--dry-run`; approved apply needs `--apply --plan <digest>`. |
| `dashboard` | Start a local read-only dashboard server; optional `--port`. Help never starts it. |

Use [synchronization](../../docs/synchronization.md) for promote/upgrade contracts and [installation](../../docs/installation.md) for ZIP/clone flows. `python3 asdg/scripts/init.py` delegates to the same init engine; it is not a second policy.

## Provider capabilities outside the portable core

The provider may also contain `asdg-presentation` (source-first presentation creation/builds, including video tooling) and `asdg-component` (component scaffolding/validation). These are outside portable acceptance and may be absent from clients.
Check their actual availability before offering invocation; read their canonical `SKILL.md` only when present. Do not advertise them as installed portable commands. Stage-local procedures are selected through Focus and role guidance rather than invented slash aliases.
