# Ownership regression evidence

[Tests](test_ownership.py) exercise real portable installation, CLI and generated hook commands in disposable Git repositories, using explicit synthetic session context.

![The fixtures test owned documentation separately from sprint implementation permission.](../00-governance/docs/images/documentation-authority.svg)

| Case | Expected boundary |
| --- | --- |
| All catalogue roles | Own documentation works without sprint; both integrations initialize and repeat setup preserves bytes. |
| Architecture/Purpose | Purpose reads work; updates, deletion and cross-owner moves return a proposal/handoff. |
| OpenSpec | ASDG-08 exact artifacts in a custom resolved-store fixture pass; other roles, missing workflow and reserved roots fail. |
| Coding | Only ASDG-09 plus active scope allows application patches; another role or target fails. |
| Shared utilities | Explicit Governance records, Admin maintenance, authorship, review and closeout paths retain narrow allowances. |
| Unknown identity | Missing/stale session context, tool-supplied role and unknown IDs grant no write authority. |
| CLI | Preflight reports handoff and leaves the repository unchanged. |

The test class borrows PortableTests fixture helpers, not its test methods. `check` calls the ownership function; hook helpers execute the generated command.
Tests do not apply a denied patch, consume model usage, alter trust or authenticate a human approval.
A separate optional native test uses the installed OpenSpec CLI in an isolated home, derives store/artifact paths from instructions, preflights ASDG-08 targets and strictly validates a proposal/spec/design/tasks bundle. It does not invoke a native agent or the upstream skill.
Run `python3 -B -m unittest discover -s asdg/tests -p test_ownership.py`.
See [control limits](../00-governance/docs/write-controls.md) before claiming native enforcement.
