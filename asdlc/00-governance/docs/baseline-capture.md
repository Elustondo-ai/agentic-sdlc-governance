AI-MODIFIED - 2026-10-14T20:39:10Z

# Brownfield baseline capture — v0.1.4 trial contract

`asdg baseline capture --source <legacy-project>` reconstructs existing-system evidence.
It never imports application code, starts a sprint, changes hook trust or grants approval.

## Execution and ownership
1. Verify the bound consumer and inventory legacy text without following links or executing it.
2. Load root instructions, actual Coordinator/selected roles, contracts, local skills, runtime and shared
   `asdlc-documentation` instructions. Missing definitions are reported, never invented.
3. Run a separate Codex Coordinator execution to justify stage selections and evidence-scoped tasks.
4. Run the selected specialists separately, in stage order, with immutable source snapshots and
   prior validated specialist outputs. The first trial is capped with `--max-agents 2`.
5. Validate each owner's visual+notes units and promote the exact authored bytes to
   `docs/asdlc/<stage>/baselines/<run-id>/`; no Coordinator or runner rewrites specialist content.
6. Run a separate Coordinator synthesis execution for governance-only reconciliation and gaps.

## Commands
```sh
asdg baseline capture --source ../../meetingHelper --dry-run
asdg baseline capture --source ../../meetingHelper --max-agents 2
```
`--json` yields only the report on stdout; progress goes to stderr.
Invalid timeout/count values fail even during dry run. Dry run never invokes agents or writes docs.
Separate Codex processes load catalogued roles; native named-subagent execution is disabled.
See [R01 execution, environment and provenance](baseline-validation-r01.md).

## Observable records
See [progress, diagnostics and private rejected-output bundles](baseline-observability.md).
Every invocation has its own compact start/end Markdown log in its stage's `logs/` directory.
Coordinator routing and synthesis are distinct invocations and therefore have distinct logs.
Logs include actual timestamps, role/task, completion status, artifact count, role/prompt hashes,
and emitted Codex session ID, including failed executions when available.
A runner-owned `00-governance/logs/<run-id>__baseline-run.json` receipt records routing,
actual sessions, artifact owner/hash mappings, failures and capture status; it is not knowledge.
New receipts include the source inventory, requested cap and authoritative sprint snapshot at start.
A later failure retains earlier successful artifacts and logs without silently deleting evidence.

## Boundaries and interpretation
Source filtering excludes VCS/dependencies, private names/extensions, binary/unreadable files,
common inline credentials, symlinks and files exceeding limits. Exclusions remain visible.
Documentation is one numbered topic, one visual and one <=50-line notes file with AI-MODIFIED,
owner identity, sources, uncertainties and contradictions. No PME approval or PPTX is produced.
The isolated write permission applies only to baseline documentation, not application work.
See [sandbox and validation](baseline-safety.md) and [trial evidence](baseline-review.md).
The [text-only reader](baseline-source-scope.md) excludes binary source images and VCS history.
The [clean checkpoint plan](baseline-checkpoint-plan-r01.md) is proposed only; Git operations need approval.
