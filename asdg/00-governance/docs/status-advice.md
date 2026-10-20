# Coordinator console advice and reports

Use the coordinator to understand the next recommended action and the evidence behind it.
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
Evidence paths remain in prose; runtime metadata stays in the companion JSON receipt.
One response contains both the summary and detailed advice; no summarization turn is run.
The coordinator remains ephemeral, read-only, with approvals denied.

## Bounded report write

Python resolves the catalogue's `asdg-prepare-plan` capability and the project's
`.asdg/project.json` binding. The declared planning folder must already exist.
Reports go only in its `current/advice/` subfolder; the model supplies no destination.
Speaker Coach's resolved destination is `docs/asdg/07-planning/current/advice/`.
Timestamped names include a unique suffix; existing reports are never overwritten.
Symlink destinations, traversal and foreign artifact roots are rejected.
Python validates readable prose within 50 nonblank source lines.
A matching JSON receipt preserves runtime details, exact document hash and the complete result.
An overlong or invalid report is rejected before writing, with an explicit failure.
The document and receipt are published exclusively; ordinary failure removes only this attempt’s files.

Readable reports retain the project context, evaluation date, recorded state, recommendation,
rationale, evidence, uncertainties and decisions. JSON retains exact times and runtime/tool receipts.
Reports are advisory: they do not approve plans, register evidence or authorize work.
The bounded report write never changes workflow state, hooks or application files.

## Failures and automation

`--facts-only --verbose` and `--json --verbose` without `--advise` are usage errors.
Plain factual JSON retains the existing UTC evaluation timestamp and invokes no LLM.
JSON advice modes emit one JSON object without console progress or path messages.
Unavailable advice or save failure exits 1; valid advice remains visible if saving fails.
`advice_report.status` is `saved`, `failed` or `not_saved`; only `saved` includes a path.
Console failures explicitly state that no report was saved.
