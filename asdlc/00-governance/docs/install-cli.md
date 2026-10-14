AI-MODIFIED - 2026-10-14T16:07:31Z

# Local CLI installation and project initialization — v0.1.4

## User workflow
Prerequisites: Python 3.9+ as `python3` on PATH, zsh/bash, and writable user configuration.
Check `command -v python3` and `python3 --version`; another Python elsewhere does not satisfy this check.
`asdg init` also requires Git on PATH and a separate existing Git worktree.
Run `./asdg install` from the cloned methodology repository; no options are required or accepted.
If a Drive-synced copy lacks its executable bit, use `python3 asdg install`.
Optionally restore local execution with `chmod +x asdg`; no shell bootstrap is needed.
For Git distribution, record `asdg` as executable in a separately authorized Git change.
Open a fresh terminal, change into the application repository, and run `asdg init`.
`asdg init` automatically checks structure after initialization using the same inspection function as `asdg verify`.
Both commands exit 0 only when structural verification passes; failures exit non-zero with actionable errors.
Successful output is two short lines ending in `ALL GOOD!`; file details remain available with `--json`.
Initialization also creates inactive `.asdlc/sprint.json` and a Codex PreToolUse hook configuration.
Review and trust the project hook with `/hooks` in a fresh Codex session before implementation.
See [sprint gate](sprint-gate.md) for commands, enforcement boundaries and activation.
`asdg status` / `status --json`, `asdg next`, and `asdg dashboard` share the [state evaluator](state-engine.md).
Init creates an empty `.asdlc/lifecycle.json` evidence index; it grants no stage approval.
`asdg verify` remains available to re-check structure at any time; `asdg status` reports the provider and entry paths.
The same commands accept `--json` only as an optional machine-readable output format.
`asdg agent list` / `asdg agent describe architect` inspect definitions, not live agents.

## Installer behavior
See [installer runtime](install-runtime.md) for launchers, backups, shell handling and limits.

## Initialization behavior
Operate on the current Git worktree root; plain directories are not silently converted into Git repos.
Use all 13 exact folder slugs from `types/agent-catalog.json` under target `docs/asdlc/`.
Create small project-artifact READMEs and provider-identified metadata; never copy governance implementation.
Append a bounded project AGENTS.md bridge; preserve approval baseline and update AI-MODIFIED.
Back up a modified existing AGENTS.md under Git-ignored `.asdlc/backups/`.
Refuse a conflicting bridge, YAML-first instructions, overlong merge or foreign `.asdlc/` data.
Preflight before writes; repeat init preserves authored files and repairs only missing structure.
No branch, commit, push, feature code, sprint start or review approval.
The generated project hook configuration is not automatically trusted or proven active.

## Deliberate limits
Development-mode installation references a live checkout, not an immutable packaged release.
Catalogue hashes detect layout drift; a recorded Git SHA is provenance, not a full content lock.
Runtime status provides resolved paths; this is a bootstrap instruction bridge, not native-agent activation.
Native agent registration, cross-project logging, live ping/ask and sprint transitions are separate work.
Safe file checks are not a defense against a malicious concurrent process or a disk failure during rollback.
Read [contract](../types/cli-project-contract.md) and [verification](cli-verification.md).
