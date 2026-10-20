AI-MODIFIED - 2026-10-14T16:14:00Z

# Baseline validation record — 2026-10-14
Historical pre-R01 results; see [Correction Report R01](baseline-correction-report-r01.md) for fresh checks.

## Automated tests (offline; no model-generated specialist evidence)
`python3 -B -m unittest discover -s asdlc/00-governance/tests -p test_baseline.py -v`
Result: **23 passed**, zero failures/errors. Explicit offline-* sessions are simulated doubles.
`python3 -B -m unittest discover -s asdlc/00-governance/tests -p 'test_*.py'`
Result: **142 tests: 126 passed, 13 errors, 3 opt-in native skips**; suite exits non-zero.
All errors are pre-existing AgentPackageTests setup failures: missing `asdlc/README.md`.
That file and missing stage 11/12 packages were absent before this patch; no definitions invented.
Full output: `/private/tmp/asdg-baseline-focused.txt`, `/private/tmp/asdg-baseline-regressions.txt`.
Changed Python parses under 3.9 grammar; this is not proof of execution on every supported version.

## Coverage and corrections
- Real CLI registration/JSON/invalid arguments; init/verify/status/sprint behavior preserved.
- Dry-run creates no files/invocations; validates counts/timeouts even in dry-run mode.
- Distinct role-specific output, prior-stage context, owner/session hashes and per-invocation logs.
- Full thirteen-role orchestration is offline only; Coordinator routing/synthesis have separate logs.
- Missing actual definitions/skills, unjustified routing and nonexistent assignment evidence fail closed.
- Secrets/binaries/private paths/symlinks excluded; changing source snapshots rejected.
- Unauthorized files/directories, wrong owners, approvals, oversized notes and active visuals rejected.
- Empty numbered topic directories rejected; valid Mermaid comments/declarations preserved unchanged.
- Failure/timeout logs preserve emitted session IDs; completed earlier outputs remain available.
- Canonical-state mutation test rejects promotion and reports `sprint_changed: true` honestly.
- Fixed original standalone test imports, mocked output cwd and ambiguous timestamp/visual prompt.
- Added real role/local skill/root/interaction materials, assignments and authoritative state context.
- Replaced broad-write child settings with output-only named permissions; connectors/network disabled.
- First actual trial rejected an invalid Intent Mermaid visual; safe comment/dialect handling and
  unambiguous visual instructions were corrected, then the capped retry succeeded.
- Original failing diagram bytes were temporary; its exact invalid declaration is not established.

## Native and consumer checks
Two local Codex Seatbelt probes: output write allowed, source write denied, snapshot read allowed,
outside synthetic temp canary read denied. No model or real secret read in these probes.
Evidence: `/private/tmp/asdg-baseline-review/native-probes.json` and sandbox code/contract.
Explicit temp/home denies were necessary; root-deny alone had allowed the synthetic temp read.
Installed `/Users/pablo.elustondo/.local/bin/asdg verify`: exit 0, ALL GOOD!; sprint inactive.
Direct launcher under a different Python: existing exact hook-command comparison fails; not changed.
Actual dry run: 22 eligible files/21,170 bytes, one `.git` directory excluded, no files/agents created.
Actual capped retry: four real sessions, 16 validated files, compact finalized start/end logs.
All published hashes/owners and <=50-line notes rechecked with final validation; source unchanged.
See [handoff and actual IDs](baseline-review.md); AI documentation remains unapproved.
