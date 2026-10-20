AI-MODIFIED - 2026-10-14T20:44:48Z

# ASDLC baseline observability — independent review

Implemented and verified offline; no human approval is claimed. Nothing staged, committed or pushed.
This pass adds observability only; it does not fix, retry or relax citation validation.
The original target in `20261014T202050Z-7a72b8eddb` remains unknown; its deleted draft is not recovered.

## Implementation
- Stderr progress: stable IDs, full role/canonical stage names, assigned task, specialist position, elapsed time and 15-second heartbeats.
- Execution, validation and promotion have distinct outcomes, artifact counts and evidence paths; JSON stdout retains its contract.
- Citation failures add stable codes, artifact-relative paths/lines, sanitized targets, rules and expected formats to existing errors.
- Private failure bundles retain bounded rejected notes/text visuals and sanitized runtime records before workspace cleanup.
- Bundles include hashes, identifiers, timestamps and omission/truncation records; they never count as validated, promoted or approved.
- Secret screening, provenance decisions, sandbox, environment, routing and promotion policy are preserved; no model was invoked.

## Verification
| Check | Exact result |
| --- | --- |
| Focused baseline suite, Python 3.15 | 73 passed; exit 0 |
| Complete governance suite, Python 3.11 | 196 run: 193 passed, 3 opt-in native skips; 0 failures/errors; exit 0 |
| Package structural validator | 13 packages/adapters valid; exit 0 |
| In-memory compile / Python 3.9 grammar | 34 governance Python files; exit 0 |
| Whitespace check | git diff --check; exit 0 |
[Commands, times and results](verification.json); [focused log](focused.txt); [complete log](governance.txt).
Coverage includes quiet heartbeats, JSON separation, runtime versus validation failure, citation location, cleanup-surviving drafts,
no rejected promotion, secret/control filtering, byte limits, symlinks/hardlinks, timeout, interruption and descendant cleanup.
[Initial exploratory run](initial-test-failure.txt): 63 tests, 1 failure exposed a secondary process-group EPERM masking the reader error.
Cleanup now records secondary errors and preserves the original; both final suites pass the regression.

## Synthetic example — not the original failed experiment
[Exact stderr console](synthetic-example/console.txt), [empty stdout](synthetic-example/stdout.txt), [receipt](synthetic-example/receipt.json).
[Diagnostic manifest](synthetic-example/bundle/manifest.json) and inert rejected drafts are a byte-for-byte retained fixture bundle.
The synthetic target is `https://example.invalid/evidence`, artifact `01-topic/speaker-notes.md`, line 7.
The example uses 0.03-second heartbeats for a short offline process; production uses 15 seconds. Its temporary paths are now removed.
[Example provenance/cleanup](synthetic-example/example.json); regenerate into a NEW directory with `python3 -B generate-example.py <directory>`.

## Diff, preservation and limits
[Incremental bounded patch](observability.patch) applies over the pre-task working tree, including the prior uncommitted runtime correction.
[File hashes and diff scope](changed-files.json); [patch application check](patch-check.json); [preservation evidence](integrity.json).
All 179 consumer and 98 legacy file/link entries match the [pre-task inventory](preservation-before.json), including all five failed-run records.
Methodology HEAD/index and unrelated prior work remain unchanged; source snapshots and sprint state were not changed.
Twelve policy functions are AST-identical to their pre-task versions; existing provenance-negative tests still pass.
Bundles use 0700 directories/0600 files; binary visuals, credentials, links and arbitrary workspace content are omitted explicitly.
Sensitive-content detection cannot identify arbitrary confidential prose; the private diagnostic bundle is not an approval artifact.
No live capture, sprint change, model call, commit, push or approval was performed. Ready for independent review.
