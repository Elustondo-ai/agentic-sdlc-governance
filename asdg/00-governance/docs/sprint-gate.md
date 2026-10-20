# Sprint implementation gate

The observed hello-world failure had no authoritative sprint state or pre-write check.
The agent treated a coding request as authorization; AGENTS.md alone did not stop the write.
`asdg init` now creates inactive `.asdg/sprint.json`, an implementation gate in AGENTS.md,
and `.codex/hooks.json` plus `.codex/config.toml` enabling hooks. Repeat init preserves valid existing sprint state.
Exact legacy bridges migrate; edited bridges/custom hook or config files are preserved as conflicts.

A human starts and stops sprints in a terminal, never implicitly through an agent coding task:
```sh
asdg sprint status
asdg sprint start --id SPRINT-001 --objective 'Hello endpoint' \
  --scope app.py --acceptance 'GET /hello returns hello world'
asdg sprint check-implementation --path app.py
asdg sprint stop
```
`--scope` and `--acceptance` are repeatable; all fields are required to start.
Scope is an exact repository-relative file or directory ending in `/`, without globs/traversal.
Protected agent-policy/state paths cannot be scope. The guard must receive EVERY target.
Guard exit 0 means all targets are allowed; exit 1 means blocked. Missing, malformed,
unsupported or symlink state fails closed; active state without supplied targets also blocks.
See [state format](sprint-state.md). This is file scope, not semantic proof of task compliance.

## Codex enforcement and activation

The PreToolUse hook and CLI consume the SAME evaluator and permission function; see [engine](state-engine.md).
It checks patch create/update/delete/rename targets BEFORE execution. It blocks arbitrary
shell execution, REPL/MCP and unknown tools; only a small read-only shell allowlist is accepted.
Agents cannot start/stop sprints, edit state/policies/hooks or write outside declared scope.
Use scoped apply_patch for implementation; run builds/tests in a human terminal for now.
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

See [current verification](state-engine-verification.md) for CLI, guard, engine and native tests.
The full suite retains existing package errors caused by the missing asdg/README.md.
Native tests use one-off trust bypass for vetted temporary hooks; real-project trust is unchanged.
Disabled/untrusted hooks, direct human writes, concurrent state/path changes, hook timeouts,
and changes whose meaning violates the objective inside an allowed file remain gaps.
Use managed policy and external filesystem/tool mediation for an adversarial security boundary.
Initialization never deletes existing application source.
