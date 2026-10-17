AI-MODIFIED - 2026-10-16

# Coordinator console advice and reports

Run these commands from an initialized consuming project:

| Command | Coordinator | Report |
| --- | --- | --- |
| `asdg status` | One turn; concise console summary | None |
| `asdg status --verbose` | Same concise summary | Timestamped Markdown |
| `asdg status --json` | Never | None |
| `asdg status --facts-only` | Never | None |
| `asdg status --json --advise` | One turn; structured JSON | None |
| `asdg status --json --advise --verbose` | Same structured result | Path in `advice_report.path` |

Normal output retains recorded facts, then shows recommended action and reason
in 1–2 short sentences each, with at most one essential question.
Evidence paths and runtime metadata remain in structured JSON and verbose reports.
One response contains both the summary and detailed advice; no summarization turn is run.
The coordinator remains ephemeral, read-only, with approvals denied.

## Bounded report write

Python resolves the catalogue's `asdlc-prepare-plan` capability and the project's
`.asdlc/project.json` binding. The declared planning folder must already exist.
Reports go only in its `advice/` subfolder; the model supplies no destination.
Speaker Coach's resolved destination is `docs/asdlc/07-planning/advice/`.
Timestamped names include a unique suffix; existing reports are never overwritten.
Symlink destinations, traversal and foreign artifact roots are rejected.
Python validates and wraps the detailed result to at most 50 readable physical lines.
An overlong or invalid report is rejected before writing, with an explicit failure.
A complete staged file is published exclusively; failed publication leaves no partial report.

Each report includes the actual UTC save timestamp, project identity/evaluation time,
recorded project/release/sprint facts, recommendation, rationale, evidence references,
uncertainties/questions, approval/routing needs and observed SDK/runtime/model metadata.
Reports are advisory: they do not approve plans, register evidence or authorize work.
The bounded report write never changes workflow state, hooks or application files.

## Failures and automation

`--facts-only --verbose` and `--json --verbose` without `--advise` are usage errors.
Plain factual JSON retains the existing UTC evaluation timestamp and invokes no LLM.
JSON advice modes emit one JSON object without console progress or path messages.
Unavailable advice or save failure exits 1; valid advice remains visible if saving fails.
`advice_report.status` is `saved`, `failed` or `not_saved`; only `saved` includes a path.
Console failures explicitly state that no report was saved.
