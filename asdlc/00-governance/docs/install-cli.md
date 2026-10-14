AI-MODIFIED - 2026-10-13T19:52:56Z

# Local CLI installation and project initialization — v0.1.3

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
Python 3.9+ standard library; no sudo, downloads, package installs, registry or account login.
Creates two managed Python launchers: `~/.local/bin/elustondo-asdlc` and `~/.local/bin/asdg`.
The qualified command avoids depending on a globally unique bare asdlc name.
An existing `asd` command is left untouched; rerun this installer to add `asdg`.
Records the Python interpreter and provider checkout in `~/.config/elustondo-asdlc/installation.json`.
Updates zsh `.zprofile` and `.zshrc`, respecting a HOME-contained ZDOTDIR.
For bash, updates `.bashrc` and the first existing `.bash_profile`, `.bash_login`, or `.profile`.
If none exists, creates `.bash_profile`; never hides an existing lower-priority login file.
Appends an identified PATH block only once; changed files have byte-exact backups in the config folder.
Never edits system folders or rewrites unrelated shell configuration.
Colliding executables, edited managed blocks, unsupported shells and symlink destinations stop the install.
Existing shell aliases/functions may shadow PATH; inspect `command -v asdg` in that shell.
An installer cannot export into its parent shell. A fresh terminal loads the saved PATH block.
For the current shell: `export PATH="$HOME/.local/bin:$PATH"`; restart VS Code when needed.
The launchers preserve the caller's directory and support checkout paths with spaces and quotes.
Root `asdg` imports `cli.main`; its `install` operation calls the Python installer directly.
Installed launchers re-execute root `asdg` with the recorded interpreter for reproducibility.
ASDLC scripts use Python >= 3.9; application projects may use any language.

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
