# CLI project contract — schema 1

## Ownership and commands

Provider: `elustondo.ai/asdg`; qualified command: `asdg`; local shortcut: `asdg`.
`./bin/asdg install`: user-local environment setup, with no options; does not initialize an application.
`init`: explicit request to add the bounded project binding and missing artifact structure.
`verify`: read-only structural verification; `status`: read-only binding and path inspection.
`agent list` / `agent describe`: read-only catalogue inspection, with no model execution.
`sprint status/start/stop` manages authoritative `.asdg/sprint.json`; init defaults to inactive.
`sprint check-implementation --path <target>` fails closed unless active and all targets are in scope.
`status`, `next`, agent guidance and read-only `dashboard` share one [derived status](../docs/state-engine.md).
All commands return nonzero on a conflict, missing prerequisite or unsupported input.
`verify`/`status` return 1 for incomplete project structure; this is not a software-build failure.

## Provider inputs

`asdg/00-governance/types/agent-catalog.json`, version 0.2, exactly stages 00 through 12.
Use its exact numbered folder names and preserve order; no locally invented lifecycle labels.
The resolved Git worktree root, never the provider root, supplies the target project.

## Project outputs

`.asdg/project.json` stores schema_version, provider, cli_version, project_id, artifacts_root,
catalog_sha256, methodology_revision_at_init, installation_mode, initialized_at and stages.
No absolute developer checkout path is committed in that binding.
`docs/asdg/` holds project-specific artifacts only, including 00 governance plus twelve stages.
Root `AGENTS.md` contains one identified Elustondo ASDG bootstrap section.
`.codex/hooks.json` configures the pre-tool implementation guard; trust requires Codex review.
`.asdg/lifecycle.json` references stage evidence; presence is distinct from completion or approval.
Generated documents use titles, explanations and at most 50 nonblank source lines.
Preserve spacing and retain review events against exact hashes before marker removal.
No stage completion or PME approval is inferred from initializing a directory.

## Failure and preservation

Existing different providers, schemas or catalogue hashes are conflicts, not automatic migrations.
Existing project content is preserved; only the recognized bootstrap section is added or verified.
Existing approval timestamps are retained as an earlier baseline; AI-MODIFIED is updated on changes.
No silent rewriting of YAML front matter, user shell commands, symlink targets or lifecycle content.
Initialization is idempotent; deterministic structural verification follows successful initialization.
Ordinary write failures trigger best-effort rollback of this operation's own changes only.

## Runtime boundary

This contract installs a CLI and project hook configuration, not running agents or hook trust.
The CLI and hook share the [implementation gate](../docs/sprint-gate.md); trust is not inferred.
Returned entry paths must be explicitly read; their presence is not proof of native role invocation.
Public commands and structured outputs share the same implementation.
