# Root-layout refactor — 20 October 2026

Pablo requested a simpler embedded distribution root and authorized this refactor.
Working version: `0.2.0-pilot.2`. This identifier records a local revision, not human approval or release authorization.

| Location | Contents |
| --- | --- |
| Root files | `README.md`, `AGENTS.md`, `LICENSE`, `CODEX-PROMPT.md` |
| `00-governance/` through `12-…/` | Existing methodology, roles and procedures |
| `scripts/` | Initializer, CLI, hooks and package checker |
| `scripts/lib/` | Supporting Python runtime modules |
| `metadata/` | Identity, provenance, integrity and refactor records |
| `docs/` | Human guides and verification evidence |
| `skills/` | Shared canonical workflows |
| `templates/` | Discovery and named-agent installation inputs |
| `tests/` | Consolidated automated tests |

The obsolete `agents/` placeholder is removed; roles remain in the numbered packages.
No numbered stage, role identity, permission boundary or workflow transition was changed.
Client initialization and workflow state remain separate from this maintenance task.

## Commands from the client Git root

```sh
python3 asdg/scripts/check.py --integrity
python3 asdg/scripts/init.py --project-status defining --dry-run
python3 asdg/scripts/init.py --project-status defining
python3 asdg/scripts/cli.py status --facts-only
python3 -B -m unittest discover -s asdg/tests -v
```

The old root-level script paths are removed; use the updated README and Codex prompt.
The original zip remains the original delivery. Its original manifest is retained byte-for-byte.
Exact moves and hashes are recorded in `metadata/refactors/root-layout-2026-10-20.json`.
All 23 tests passed locally after the move. Native Mac discovery and hook trust still require verification.
