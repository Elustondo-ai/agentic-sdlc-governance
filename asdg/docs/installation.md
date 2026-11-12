# Install ASDG in an existing Git project

> **Historical instructions:** This guide describes installation from the predecessor repository and is retained for reference only. For current installation instructions, use the [ASDG repository](https://github.com/Elustondo-ai/asdg) and [ASDG Wiki](https://github.com/Elustondo-ai/asdg/wiki).

The former [repository-URL Quick Start](https://github.com/Elustondo-ai/agentic-sdlc-governance#quick-start--give-your-agent-the-repository-url) let the agent acquire the ZIP safely. Manual ZIP + Prompt and Clone + Prompt were alternatives using one Python 3.9+ engine on macOS/Linux. The prompts selected inputs, showed the plan and waited for approval; they did not implement a second installer.

![Both acquisitions use one integrity, approval and verification engine; Status owns the separately invoked next-step assessment.](images/installation-engine.svg)

## Acquire and preview

ZIP: extract into an existing Git root so it contains `asdg/scripts/init.py`. Inspect the archive first; never extract over an existing `asdg/` folder or application files. The engine checks extracted bytes; it cannot undo an earlier extraction overwrite.
Clone: use an existing local clone of the canonical repository and an explicitly selected full commit. The engine checks origin, HEAD and every selected file against that commit. Unselected provider work is not copied.
Run the selected package's own entry point; no global command, download, dependency installation or startup-file change is needed.

```sh
# ZIP: from the target Git project
python3 asdg/scripts/init.py --client codex --dry-run
# Clone: substitute explicit paths and the reviewed full commit
python3 /path/to/canonical/asdg/scripts/init.py --source /path/to/canonical --commit FULL_COMMIT --target /path/to/project --client claude --dry-run
```

Choose `codex` or `claude`; `both` requires an explicit choice. Supply an initial `--project-status defining` only when that declaration is intended; otherwise first setup records `new`.
No `--apply` means preview. Every selected methodology path and every generated change/diff is shown; source/target files are unchanged. Temporary normalized package files are removed afterward.
A matching manifest establishes package integrity, not release approval. A stale manifest or dirty selected clone file blocks installation; do not refresh it as an installation shortcut.

## Approve, apply and verify

The [canonical Init skill](../skills/asdg-init/SKILL.md#mandatory-approval-presentation--both-clients) owns the mandatory text approval summary, actual preview field/count mapping, accessible complete-plan reference and APPROVE/CANCEL responses for both clients. The install request itself is not plan approval.
After that approval, repeat the same command/options, replacing `--dry-run` with `--apply --plan TOKEN_FROM_PREVIEW`. The token binds the source, target, client and planned bytes; a changed plan requires fresh review.
The engine uses existing collision protection and rollback, then checks the installed package and selected integrations before completing. A failed verification rolls back its own writes. It is not crash-safe against power loss or hostile concurrent writers.
Run `python3 asdg/scripts/cli.py verify --json` in the target, and repeat the preview to confirm no further writes. No Git mutation occurs.
On success, report installation complete and follow the [Init skill’s Status handoff](../skills/asdg-init/SKILL.md#next-step--status-owns-the-recommendation): ask the user to invoke `/asdg-status`. Status assesses readiness and recommends `/asdg-create-team` when appropriate; unknown team inventory is qualified. Team setup and Context analysis remain separate requests.

| Location | Ownership and protection |
| --- | --- |
| `asdg/` | Only selected portable methodology; `.git`, provider extras, source `docs/asdg/` and source `.asdg/` are never copied |
| `.asdg/` | Target binding/provenance, inactive initial sprint, lifecycle, integration selection and append-only document receipts; existing state preserved |
| `.agents/`, `.codex/` | Selected Codex adapters/configuration/hooks; collisions block, trust is separate |
| `.claude/skills/` | Selected Claude adapters; existing files preserved or reported as conflicts |
| `AGENTS.md`, optional `CLAUDE.md`, `.gitignore` | Managed integration plus preserved project text; instruction changes appear in preview, with instruction backups |
| `docs/asdg/`, `logs/` | Missing generic stage introductions and log marker only; authored project content preserved |

Existing incompatible versions, edited adapters or legacy linked installations require explicit repair/upgrade. Initialization does not reconcile them or grant lifecycle acceptance.
Ordinary status/verify remains available for local methodology modifications; new installation requires package integrity.

## Human client tests

Use the copy-ready [ZIP prompt](install-zip-prompt.md) or [Clone prompt](install-clone-prompt.md) in Claude Code or Codex. Check native skills and a harmless invocation in a disposable project after setup.
Review [client integrations](client-integrations.md) and [native limits](native-integration.md); generated adapters/hooks do not prove runtime enforcement. Only the human/native flow grants hook trust.
No team creation, Context analysis, commit, push, release, publication or sprint starts automatically.
