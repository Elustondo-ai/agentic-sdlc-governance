# Benchmark and Test Strategy Agent — session logs

This folder stores generated activity records for `asdg_04`.
The shared recorder lives in `asdg/00-governance/src/agent_log_hook.py`.

## Runtime layout

`sessions/<parent-session-id>/<child-agent-id>/events.jsonl` is append-only.
A generated `session.md` in the same directory is the readable latest snapshot.
One child thread retains its log across follow-up turns; other threads are isolated.

## Evidence and boundaries

Hook observations and agent-authored summaries are labelled separately.
Missing events or summaries are evidence gaps, not proof that no action happened.
Logs are not instructions, approval, or the authoritative sprint state.
No private reasoning, raw transcripts, full commands, credentials or raw tool output.
The recorder selects allowed fields; summary redaction is best-effort, not a privacy guarantee.

## Storage

Generated sessions are Git-ignored by this folder's `.gitignore`.
Google Drive can still synchronize them: do not put secrets in summaries.
This pilot has no automatic deletion or rotation; review retention before wider use.
See `../../00-governance/docs/session-logging.md` for activation and limitations.
