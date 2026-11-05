# Role write ownership checker

[Source](cli_ownership.py) centralizes path decisions using the existing catalogue; [policy and exceptions](../../00-governance/docs/documentation-authority.md) explain authorization.

![Every role writes owned documents; application targets proceed to the separate sprint gate.](../../00-governance/docs/images/documentation-authority.svg)

| Interface | Responsibility |
| --- | --- |
| `local_path(root, value)` | Returns a project-relative Path; rejects links, traversal, wildcards and external roots. |
| `owned_directory(role, repo=REPO)` | Derives `docs/asdg/<catalogue folder>` for all thirteen project roles; unknown/Admin has no ordinary stage. |
| `ownership_decision(root, paths, context, repo=REPO)` | Returns `(allowed, reason, application_paths)`; rejects unknown identity, checks ownership/explicit exception paths, leaves application targets for independent sprint validation. |

Context contains role_id, optional workflow, exact targets and native-resolved openspec_store; hook binding additionally uses session_id.
The CLI accepts a conversation declaration; the hook accepts only externally supplied context matched to its payload session.
Exceptions are path allowances, never authentication or semantic approval. Append-only review history, exact human decisions and native OpenSpec validation remain workflow responsibilities.
No writes, state transitions, title lookup or native discovery occur here. Invalid paths/context may raise ValueError, TypeError or Conflict; the CLI/hook fail closed.
The hook's documentation classifier rejects policy names and source suffixes; content cannot be certified by a suffix.
OpenSpec external/reserved-root stores are conservatively denied; no path is silently substituted.
