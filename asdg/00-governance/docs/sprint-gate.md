# Sprint implementation gate

The observed hello-world failure had no authoritative sprint state or pre-write check.
The agent treated a coding request as authorization; AGENTS.md alone did not stop the write.
`asdg init` now creates inactive `.asdg/sprint.json`, a root `AGENTS.md` bootstrap whose required `asdg/AGENTS.md` links this gate,
and `.codex/hooks.json` plus `.codex/config.toml` enabling hooks. Repeat init preserves valid existing sprint state.
Exact earlier bootstrap blocks move to the top of `AGENTS.md`; edited blocks and custom hook or config files are preserved as conflicts.

A human decides to start or close a sprint, either in a terminal or through an explicit [Sprint start](../../skills/asdg-sprint-start/SKILL.md) / [Sprint close](../../skills/asdg-sprint-close/SKILL.md) request; a coding task alone implies neither:
```sh
python3 asdg/scripts/cli.py sprint status
python3 asdg/scripts/cli.py sprint start --id SPRINT-001 --objective 'Hello endpoint' \
  --scope app.py --acceptance 'GET /hello returns hello world'
python3 asdg/scripts/cli.py sprint check-implementation --path app.py
python3 asdg/scripts/cli.py sprint stop
```
`--scope` and `--acceptance` are repeatable; all fields are required to start.
Scope is an exact repository-relative file or directory ending in `/`, without globs/traversal.
Scope bounds paths only; work inside it must still serve the sprint objective and meet its acceptance criteria.
Protected agent-policy/state paths cannot be scope. The guard must receive EVERY target.
Guard exit 0 means all targets are allowed; exit 1 means blocked. Missing, malformed,
unsupported or symlink state fails closed; active state without supplied targets also blocks.
See [state format](sprint-state.md). This is file scope, not semantic proof of task compliance.
The [Sprint start Git preflight](../../skills/asdg-sprint-start/git-preflight.md) requires a clean worktree and a new sprint branch before activation; dirty work must be committed by the developer first.
This skill-level convention is not enforced by the bare CLI; direct terminal users must perform the same preflight themselves.

## Codex enforcement and activation

The PreToolUse hook and CLI consume the SAME evaluator and permission function; see [engine](state-engine.md).
It checks every patch create/update/delete/rename target BEFORE execution. Documentation formats under client `docs/` need no sprint; code, policy paths, traversal and symlinks receive no documentation exemption.
Mixed patches still check every application target against active scope. File classification does not prove content semantics; see [documentation authority](documentation-authority.md).
It blocks arbitrary
shell execution, REPL/MCP and unknown tools; only a small read-only shell allowlist is accepted.
Only the human-directed sprint utilities may create the sprint branch, invoke start/stop and preserve their closeout receipt; they cannot widen implementation scope or edit policies/hooks.
Use scoped apply_patch for implementation; existing role/runtime rules still govern execution and tests.
If the hook denies a transition or receipt write, report it and provide the human-run command; do not bypass or alter enforcement.
A guard execution failure emits a deny decision through a shell fallback.

Codex supports these hooks locally (observed version 0.162.0-alpha.17.2; hooks enabled).
Source: https://learn.chatgpt.com/docs/hooks
Project hooks run ONLY after project and exact hook definitions are trusted.
Open a fresh Codex session and use `/hooks` to review/trust the generated hook.
`verify` validates hook configuration, NOT runtime trust or native interception.
Until trust is established, instructions remain advisory and this project is NOT fully enforced.
Do not bypass hook trust for ordinary use. Managed hooks deployed by an administrator are
stronger because agents/users cannot disable them through the hook browser.

## Limits and verification

See [current verification](../../docs/verification.md) for CLI, guard, engine and native tests.
This package does not run native trust bypasses; actual runtime enforcement requires local observation.
Disabled/untrusted hooks, direct human writes, concurrent state/path changes, hook timeouts,
and changes whose meaning violates the objective inside an allowed file remain gaps.
Use managed policy and external filesystem/tool mediation for an adversarial security boundary.
Initialization never deletes existing application source.
