# ASDG test guides

These guides explain what the automated tests and continuation fixtures exercise, how their helpers work, and where their evidence stops.
They describe the maintained code; an execution result must come from an actual test run.

- [Disposable continuation scenarios](continuation_fixture.md): Builds isolated client repositories for trying ASDG continuation behavior against empty, partial, accepted or stale Purpose evidence.
- [Agent configuration compatibility tests](test_agent_config.md): Checks that packaged role adapters parse consistently through the portable fallback, while unsupported syntax and duplicate keys fail.
- [Portable integration tests](test_portable.md): Exercises initialization, relocation, preservation, permission boundaries, logging and advice/report handling in disposable Git repositories.
- [Purpose acceptance tests](test_purpose_review.md): Checks that document presence, agent readiness and human acceptance remain separate, and that edits invalidate acceptance without rewriting history.
- [Stage acceptance tests](test_stage_review.md): Checks stage-local documentation acceptance, dependency hashing and readback without mutating lifecycle state.
- [Distribution tests](test_distribution.md): Builds the real ZIP and checks isolated installation, relocation, file exclusion and reproducibility.
- [Synchronization tests](test_sync.md): Exercises promote/upgrade, conflicts, deletion protection, dry runs and adopted versions in disposable Git repositories.

Return to the [runtime modules](../scripts/lib/README.md).
