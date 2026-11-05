---
name: asdg-update
description: Prepare and explicitly apply an existing project's ASDG update from a selected local canonical distribution, then separately preview its client adapters. Preserves project work and local changes; never updates automatically.
---

# Update an existing ASDG installation

Bring a selected methodology distribution into this project, including discoverable commands when the supported integration engine can add them safely.
Use only for an explicit human update request; a request to explain, create or prepare this skill does not authorize applying an update.
Read client instructions, [session policy](../asdg-focus/session-policy.md) and [synchronization](../../docs/synchronization.md). Require explicitly selected ASDG Admin for methodology maintenance; never select Admin automatically.
Preserve the conversation's role, subject, attitude, title and project binding. Updates assign no project work and start no sprint.
This skill composes existing `upgrade` and `init` engines; there is no `update` CLI subcommand or new file-copy engine.

## Establish source and target

Resolve the client root as `../../..` from this canonical skill directory. Verify the actual target Git root, ASDG binding and recorded client integrations.
Use the human-selected local canonical root and distribution. Ask for missing source/version choices; never fetch, clone, download, publish or select a newer release automatically.
Inspect source and target Git status, HEAD and origin without changing them. Verify the selected source manifest with its own `asdg/scripts/check.py --integrity`; matching hashes are not release approval.
Explain whether the source is a local candidate or a published release, including version, source commit, manifest/snapshot hashes and any working-tree differences. Same version strings never prove identical content.
The current upgrade engine requires both roots to have HEAD and identifiable origins. If either is missing, stop dependent application, report the prerequisite and preserve Git state; do not commit, stage, add a remote or fake identity.
When blocked, offer a read-only content comparison with hashes as preparation only. It is not an executable approval plan; do not bypass the engine with manual copying, replacement extraction or a fabricated baseline.
For a client that lacks this skill, explain how to read this canonical workflow from the selected trusted source; do not claim it is discoverable until installed.

## Preview and approve methodology

Run the selected source's `asdg/scripts/cli.py upgrade --source <canonical-root> --target <client-root> --dry-run --json`, passing arguments safely.
Present every added, modified, deleted, unchanged/retained and conflicting path with the exact `plan_id`, source identity and target. Keep the detailed report accessible; summarize important changes and conflicts.
Any conflict blocks the whole apply. Present the conflicting bytes for a bounded human reconciliation decision; never force, merge, delete local work or refresh a target manifest to manufacture success.
A request to prepare an update stops at the reviewable preview. Obtain explicit approval of its exact plan before applying; prior install approval, invocation, matching hashes or a version label is not that decision.
After approval, repeat with `--apply --plan <plan_id>` instead of `--dry-run`; changed inputs require a fresh preview and decision. Report actual written paths and adoption receipt; source and unrelated files stay unchanged.

## Separately preview and refresh integrations

Upgrade synchronizes `asdg/` only. It does not install skill adapters; a new canonical skill alone will not appear in the client's command list.
After successful upgrade, use the target's own `asdg/scripts/cli.py init --dry-run --json`, omitting `--client` to retain recorded clients. Never add another client or change hook trust as a side effect.
Present the exact integration plan, including any changes outside adapters. New missing adapters can be added; differing existing managed files are conflicts requiring separately authorized reconciliation, not blind overwrite.
Follow [Init's approval presentation](../asdg-init/SKILL.md#mandatory-approval-presentation--both-clients). Apply only after explicit approval of this fresh integration preview, using the same options with `--apply --plan <token>`.
If retained local package edits or incompatible metadata prevent init verification, report the exact gap and preserve them; never restore the incoming manifest over local bytes or run a first-time reinstall.
No-change integration previews need no apply. If integration fails after a successful upgrade, report methodology updated / integration pending; do not claim atomic completion or silently roll back adopted work.

## Verify and hand off

Run the target's `asdg/scripts/cli.py verify --json`. Report package integrity separately; retained local methodology edits may differ from the incoming delivery manifest without being permission to overwrite them.
Check installed selected-client adapter links resolve to the target's canonical Help and Update skills; report absent adapters precisely. Never edit internal app configuration, databases or discovery caches.
Structural verification proves installed files only. Claim native discovery and invocation only if observed; otherwise ask the user to refresh the client skill list or reopen the project and try `$asdg-help` in Codex or `/asdg-help` in Claude.
Report intended, applied, pending and verified states separately with exact source/plan receipts. Point to Status for the user's next assessment; do not invoke team creation, alter sidebar order, approve documentation or start work.
No commit, push, release, deployment, permission change or project-state migration is authorized by this utility.
