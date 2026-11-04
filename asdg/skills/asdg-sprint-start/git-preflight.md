# Begin with a clean Git baseline

Sprint start creates its branch from the verified current checkout before changing sprint state or project files.
This is the user's sprint-start convention; creating or maintaining the skill never triggers a branch automatically.
Branch creation is part of an explicitly requested start, not permission to commit or publish.

## Verify the starting point

Resolve the client Git root and inspect the current branch, HEAD and `git worktree list --porcelain`.
Require an existing commit and an attached base branch. Ask the developer to establish the intended baseline if either is missing.
Stop for an unfinished merge, rebase, cherry-pick or revert even if the file listing looks clean.
Run `git status --porcelain=v1 --untracked-files=all --ignore-submodules=none`; require exit 0 and empty output.
This includes staged, unstaged, untracked and reported submodule changes. Ignored files are outside Git's clean-worktree definition.
On any listed change, report `BLOCKED: GIT_WORKTREE_DIRTY`, summarize affected paths and tell the developer to commit/check in their work before starting.
Do not stage, commit, stash, reset, delete, alter ignore rules or skip ASDG state/document changes to manufacture a clean result.
An unreadable Git status is unknown, not clean. Recheck after the developer says cleanup is complete.
Retain the verified base branch and full HEAD commit as the sprint's comparison baseline.

## Derive and create the branch

Honor an explicit branch name or naming constraint. Otherwise derive a short name from the sprint ID, respecting any required repository prefix.
For numbered sprints, use at least two digits: `SPRINT-000` → `sprint-00`, `SPRINT-007` → `sprint-07`, `SPRINT-123` → `sprint-123`.
For other IDs, use a short readable lowercase Git-safe form; clarify if normalization would be ambiguous.
Validate with `git check-ref-format --branch <name>`; inspect existing local/remote refs and worktrees for conflicts.
If the target name already exists, report it and request a reuse or new-name decision; never reset, overwrite or silently switch to an existing branch.
Do not fetch, pull, push or infer that a clean local checkout is synchronized with its remote.
Immediately before creation, recheck the base branch, HEAD, clean status and intended sprint state.
Make `git switch -c <name>` the first mutation of the start workflow, passing the validated name as one safely quoted argument.
Require command success, the expected current branch, the original HEAD and empty porcelain status before starting the sprint.
If branch creation fails or is denied, leave sprint state unchanged and report the exact failure.

## Interrupted starts and existing sprints

If branching succeeds but CLI start fails, retain the branch and report the partial result; do not delete it or switch back automatically.
Retry only after inspecting current branch, HEAD and sprint state. A known continuation may reuse its own verified branch; it is not a fresh start.
If a sprint is already active, an ordinary repeated start reports that state instead of creating another branch or restarting the sprint.
An explicit request to add its missing branch may perform this same clean preflight and branch creation while preserving the active sprint bytes.
Record that as a branch correction after activation, not as evidence the original sprint began on a branch.
After successful activation, the changed `.asdg/sprint.json` is expected sprint work; do not retroactively fail the clean starting-point check.
Record the new branch, base branch, starting commit, observed preflight result and transition outcome in the conversation.
