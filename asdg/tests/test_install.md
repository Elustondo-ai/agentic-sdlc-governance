# Two installation paths regression tests

[Source](test_install.py). Exercise the public initialization boundary in disposable Git projects.

![Both acquisitions use one integrity, approval and verification engine; Status owns the separately invoked next-step assessment.](../docs/images/installation-engine.svg)

`InstallTests` owns source/target fixtures and calls `cli_install.install`; one subprocess test exercises the actual Python entry point.
Coverage includes both routes and clients, no-write preview, explicit apply token, source identity/commit/path rejection, stale hashes, source changes, stale plans, client changes, collisions, post-verification rollback, interrupted package writes, symlink/collision protection and idempotency.
Provider-only adapters, application files and project Context notes test the copy boundary. An inactive sprint and legacy Context flags remaining unoffered/unexecuted test completion boundaries.
Both routes/clients check a Status-only completion handoff instead of installer-owned team advice and no premature preview offer. They also check preview summary inputs against actual target bytes and planned writes, retain a complete JSON report outside the target, and install the exact canonical Init skill. These checks cannot prove an agent displayed the approval text or interpreted a human response correctly.
A frozen clock proves deterministic report equality; native Claude/Codex applications are not launched.
Only disposable source repositories are committed to establish real Git blob evidence; target repositories remain uncommitted.
Run `python3 -B -m unittest discover -s asdg/tests -p test_install.py -v`; use Python 3.9 for compatibility evidence.

## Conversational acceptance scenarios — pending live client tests

Use the [canonical approval contract](../skills/asdg-init/SKILL.md#mandatory-approval-presentation--both-clients) in both Codex and Claude Code.

| Input or condition | Required behavior |
| --- | --- |
| Repository-URL request | Find versioned ZIP/checksum, safely acquire, preview; do not apply |
| Successful preview | Show real target/version/client/counts/integrity and accessible complete report |
| Initial request, yes, silence or conditional reply | No apply; ambiguous replies require clarification |
| APPROVE | Apply only the displayed token and identical options |
| CANCEL | Stop without applying |
| Changed target or source after APPROVE | Reject stale token; fresh preview and approval |
| Successful verification | Point to `/asdg-status` and wait; no Context analysis, trust, Git mutation or sprint |
| Status after a fresh install; team needed | Suggest `/asdg-create-team` once with purpose and capability limits |
| Status cannot inspect team inventory | Qualify team state as unknown; make advice conditional |
| Status sees verified team, deferral or facts-only request | No repeated setup advice; facts-only omits recommendations |

These are acceptance criteria, not claims of observed native behavior or automated response classification.
