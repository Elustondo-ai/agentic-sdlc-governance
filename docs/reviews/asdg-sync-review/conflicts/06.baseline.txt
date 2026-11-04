# Iterate with local Codex and a reviewer

Pablo selected the embedded `asdg/` folder as the evolving working baseline on 20 October 2026.
The delivery snapshot is its starting point. The old governance checkout becomes provenance, not a live dependency.
An iteration changes this baseline only through a visible, bounded diff and suitable validation.

## Responsibilities

Local Codex inspects real files, implements the assigned change, runs relevant checks and reports evidence.
Pablo selects priorities and approves consequential decisions. This chat reviews the supplied results and diffs.
The reviewer cannot observe local work automatically; share the report and changed files/diff after each iteration.
A different conversation is not proof of independence: disclose shared source, assumptions and earlier authorship.

## One iteration at a time

1. State the problem, expected behavior, allowed files and completion evidence.
2. Record Git status and the starting revision when one exists; preserve unrelated local changes.
3. Inspect the actual client and local methodology before editing or reconstructing documents.
4. Make a bounded change under the applicable project/runtime rules; do not bypass a denied operation.
5. Run relevant checks and record failures, skipped checks, runtime versions and remaining uncertainty.
6. Return the exact diff plus a concise report for review; do not infer approval from passing tests.

For the first iteration, finish installation and native discovery verification before application cleanup.
Then review Context and Purpose against the real `app.js` and `index.html`, one conversation at a time.
Specialists remain read-only until their execution policy is explicitly redesigned and tested.
Governance maintenance is a separate explicit task; an application sprint cannot silently authorize it.

## Return for review

Record the objective; changed paths and rationale; commands/results; relevant versions;
file-integrity observations; native discovery/trust evidence; unresolved questions; and the proposed next step.
Use `docs/asdg/07-planning/current/reviews/` for deliberate review reports, with at most 50 nonblank lines each.
Use `logs/` for disposable execution traces. Keep exact-state approval history in `.asdg/`, not ignored logs.
Do not include credentials, full transcripts, private reasoning or unnecessary personal information.
Never claim a commit, push, approval, native invocation or trust operation unless it actually occurred.
Local source edits will differ from the delivery manifest; retain that original manifest as provenance.
Create a new version/manifest only when deliberately packaging the next reviewed distribution.
