# Work with the embedded methodology

Run commands from the client Git root. The project-local command is `python3 asdg/scripts/cli.py`.
An older globally installed `asdg` can point elsewhere; do not use it for this pilot without resolving it.

```sh
python3 asdg/scripts/cli.py status --facts-only
python3 asdg/scripts/cli.py status --json
python3 asdg/scripts/cli.py agent list
python3 asdg/scripts/cli.py sprint status
```

These operations are deterministic; they do not call a model. Status reads the recorded project,
release and sprint separately. The earliest unregistered evidence is a mechanical finding, not approval or priority.
An existing code file or stage README never establishes accepted lifecycle evidence.

## A specialist conversation

For whole-project management, use `$asdg-focus on project governance`; its default title is `00 Governance`.
It selects the existing coordinator, distinct from a general chat with no focus; it grants no execution authority.

Select **ASDG focus** in Codex and describe the role, for example “on high level architecture” or “help me clarify the project's purpose.”
Focus interprets the phrase; a clear match proceeds, ambiguity asks for a recommended choice and alternatives, and no match shows all twelve specialists plus Governance separately.
Activation loads the role and reports focus; assign the review task in the following message.
For example: “Read this project's existing code and purpose documents; explain the gaps and propose corrections.”
Stage 02 is Purpose; `intent` remains a generic Focus alias. No `asdg-intent` adapter is installed.
The focus stays in this conversation while its activation receipt remains available.
Use `$asdg-focus subject Security` for a title such as `05 Architecture Security`; role selectors and bare `clear` retain their meanings.
Use `$asdg-attitude black` to append `Black`; `off` removes the attitude from the title. `status` only reports; English/Spanish and temporary scopes remain supported.
Proposed pilot default: a hat persists until changed or turned off; “this answer only” restores the previous hat at completion. See [session fields and titles](../skills/asdg-focus/session-state.md).
`$asdg-status` reports conversation focus; it is distinct from CLI workflow status.
These skills do not create a new window or persistent agent process. Resume the same Codex conversation.
Every agent may save documentation and supporting assets under `docs/` without a sprint or separate save approval; use the [shared documentation contract](../00-governance/docs/documentation-authority.md).
Use `$asdg-decision` in any role: it loads the role's optional `skills/decision/SKILL.md` or uses generic defaults, following the [specialization contract](../skills/asdg-decision/specialization.md).
The skill preserves Focus and explicit selections; recording a decision does not implement it or approve a lifecycle baseline.

## Sprint transitions

Use `$asdg-sprint-start` to verify a clean worktree, create a short sprint branch and activate the chosen scope; `$asdg-sprint-review` assesses evidence without changing state.
If anything is staged, unstaged or untracked, start stops and asks the developer to commit/check it in. `SPRINT-000` uses `sprint-00` unless another name is selected.
Use `$asdg-sprint-close` to preserve a review and end the explicitly selected sprint, including an unfinished or cancelled one. These utilities preserve Focus.
The existing local CLI remains available; perform the [clean-worktree and branch preflight](../skills/asdg-sprint-start/git-preflight.md) before a manual start:

```sh
python3 asdg/scripts/cli.py sprint start --id SPRINT-001 --objective 'Chosen improvement' \
  --scope app.js --acceptance 'Observable acceptance criterion'
python3 asdg/scripts/cli.py sprint check-implementation --path app.js
python3 asdg/scripts/cli.py sprint stop
```

An active sprint authorizes only its file scope and intended work, subject to independent role/runtime restrictions.
Scope may be an exact file or a directory ending in `/`; policies, distribution and state are protected.
Stopping returns the current record to inactive. The close skill preserves a receipt under `.asdg/sprint-closeouts/`; direct CLI stop does not, and no release is closed.
Do not run these example transitions as part of installation.

## Optional AI advice

Plain `status` and `status --verbose` retain the existing Codex SDK advisory path.
The latter saves a report and receipt at the Stage 07 root as `02.1-status-<time>-<id>.md` and a matching JSON receipt.
It requires a compatible separately installed SDK/runtime and Codex sign-in; initialization installs neither.
The retained adapter targets `openai-codex==0.163.0`; live advice has not been revalidated for this package.
If advice is unavailable, report the failure and use `--facts-only`; do not confuse mechanical guidance with AI advice.
