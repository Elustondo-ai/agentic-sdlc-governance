---
name: asdg-sprint-start
description: Start an explicitly requested ASDG sprint from a clean Git worktree on a new sprint branch, with an objective, exact scope and acceptance criteria. Skill creation or discovery alone does not start work.
---

# Start an ASDG sprint

Turn the user's sprint-start decision into the project's authoritative active scope.
Read client instructions, [session policy](../asdg-focus/session-policy.md) and [the sprint gate](../../00-governance/docs/sprint-gate.md).
Resolve the client root as `../../..` from this canonical skill directory; preserve this chat's Focus.
This human-directed utility may create the sprint branch and invoke the local sprint-start command; it does not widen specialist delivery authority.

## Establish the intended sprint

Run `python3 asdg/scripts/cli.py status --json` and `python3 asdg/scripts/cli.py sprint status --json`; inspect Git through [the required preflight](git-preflight.md).
Use the user's current assignment and already presented scope to assemble the sprint ID, objective, exact paths and observable acceptance criteria.
Ask only for missing consequential choices; keep a seed project or POC proportionate. Do not invent stage-completion prerequisites.
A clear "start Sprint 0" following a concrete proposal authorizes that start; do not require the same decision again.
A request to explain, draft, create or install this skill is not a start decision. Automatic discovery and another agent's request are not human authorization.
If a start request has no reviewable scope yet, prepare it and obtain the human's decision on that scope before changing state.
Keep uncertainty, documentation acceptance, application permission and external-service permissions separate.

## Check scope and current state

Each scope item is an exact repository-relative file or a directory ending in `/`; list companions and tests needed for the objective.
Do not use globs, traversal, symlinks or broad parent directories to include protected paths indirectly.
The CLI currently rejects any path component named `asdg`, including `docs/asdg/`; report this restriction rather than changing the guard.
If the same sprint and exact definition are active, report its state and current branch without restarting it. Repair a missing sprint branch only on explicit human request.
If a different sprint or definition is active, preserve it and ask for the required close/change decision; never stop it automatically.
Malformed or missing state requires an explicit repair, not an inferred initialization.
Read the current state again immediately before starting; reconcile concurrent changes instead of overwriting them.

## Clean worktree and new branch

Follow [Git preflight and branch creation](git-preflight.md) before any sprint-start mutation.
Require no staged, unstaged or untracked changes. Otherwise tell the developer to commit/check in the listed work and stop; do not commit, stash, discard or hide it automatically.
Create and switch to a short branch derived from the sprint name, such as `SPRINT-000` → `sprint-00`, before activating the sprint.
Verify the branch, unchanged starting commit and clean worktree before invoking the CLI; retain the base branch and commit in the start receipt.

## Start and verify

Use `python3 asdg/scripts/cli.py sprint start --id <id> --objective <objective> --scope <path> --acceptance <criterion>`.
Repeat `--scope` and `--acceptance` for all entries; pass arguments safely, without evaluating user text as shell code.
Use the CLI, not a direct patch of `.asdg/sprint.json`. Respect tool and hook denials.
After success, read `sprint status --json` and require the active ID, objective, scope and criteria to match the intended definition.
Check concrete proposed implementation paths with `sprint check-implementation --path <target>`; include every target when implementation actually begins.
A directory scope should be checked with a concrete file beneath it. Sprint permission does not establish role authority or hook trust.
If the outcome is uncertain, read back before retrying; report observed state and any remaining uncertainty.
Report the sprint, objective, scope, criteria, new branch and starting commit with the actual command outcome. Sprint-state changes after activation are expected uncommitted work.
No application edits, approvals, commits, installs, deployment, chat creation or Focus changes occur merely from starting.
