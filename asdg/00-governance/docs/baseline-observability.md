# Baseline progress and rejected-output evidence

Progress is written only to stderr. Successful `--json` stdout remains one report; failed commands keep stdout empty.
Names use stable role IDs plus full role/stage names, including Context and Domain Analysis and Intent.
Routing reports selected specialists; each specialist reports its position and actual assigned task.
Execution starts/completes separately from validation and promotion. Counts describe observed artifacts, not estimated work.
A running child emits an elapsed-time heartbeat every 15 seconds; no percentages or internal activities are inferred.
Task displays are sanitized, limited to 2048 characters and explicitly marked when shortened.

## Diagnostics and compatibility

Existing receipt statuses, sessions and `written_artifacts` retain their meaning.
Invocation records add execution/validation/promotion status, validated/promoted counts, elapsed time and failure phase.
Citation errors keep their existing rejection text and add `BASELINE_CITATION_*` codes, original line numbers,
artifact-relative paths, bounded sanitized targets, violated rules and expected formats.
Run/role/phase/session identifiers connect diagnostics, invocation logs and the run receipt.
Missing context is recorded as null; an unknown target is never guessed from a generic error.

## Private diagnostic bundles

Before failed invocation cleanup, the runner writes `docs/asdg/00-governance/diagnostics/<run-id>/<phase>/`.
`manifest.json` contains invocation identifiers, timestamps, hashes, structured diagnostics and bounded runtime records.
Copies are explicitly REJECTED/UNVALIDATED, never accepted artifacts, approved output or promotion counts.
Only expected shallow output topic notes and text visuals are eligible; copies use inert `.txt` names.
Source/context, prompts, credential files, arbitrary workspace contents, links, hardlinks and binary visuals are not copied.
Recognized sensitive artifact content causes whole-file omission; display sanitization redacts credentials and terminal controls.
Every omission, redaction and truncation is recorded. New directories are 0700 and files 0600; existing bundles are never overwritten.
Scanning stops at 128 entries, 30 artifacts, 2 MiB per file and 4 MiB total; retained copies cap at 128 KiB/file and 512 KiB total.
Runtime capture drains continuously but retains at most 64 KiB per stream; incomplete truncated tails are omitted.
Session events are parsed independently of retained output, with a 64 KiB JSONL record limit and explicit omission count.
Bundle metadata limits include 4096 characters/string and 128 nodes; truncation/redaction counters are recorded.
A preservation failure is reported separately and never replaces the original execution/validation failure.

## Boundaries

Validation decisions, citation grammar, sandbox permissions, environment filtering, selection and promotion rules are unchanged.
There is no automatic repair, retry, model call or approval in this observability feature.
The prior failed experiment's removed draft is not recovered; new bundles are prospective only.
Secret detection is conservative, not an exhaustive detector of arbitrary confidential prose; diagnostic material remains private.
Timeout/interruption still terminates the process group, waits five seconds, then escalates to KILL when needed.
The offline tests cover actual child-process cleanup, noisy/quiet streams, CLI JSON separation and evidence retention.
See the [observability review and synthetic example](../../../docs/reviews/asdg-baseline-observability/README.md).
