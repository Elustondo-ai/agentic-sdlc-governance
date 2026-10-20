# Per-agent session logging — pilot v0.1

## Purpose and ownership

Keep each named agent's observable activity beside its own component, not in one global log.
The common recorder is in `../src/`; it routes by `../types/agent-catalog.json`.
A runtime hook writes logs; read-only specialists do not need filesystem write privileges.
This is an authorized logging pilot, not permission to implement application features.

## Storage and execution

Each agent owns `logs/sessions/<parent-session-id>/<child-agent-id>/`.
`events.jsonl` is append-only through the recorder; `session.md` is a derived readable view.
Follow-up turns on the same child reuse that location; new child instances remain separate.
`.codex/hooks.json` registers SubagentStart, SubagentStop and attributable tool callbacks.
Review and trust the hooks locally before expecting execution; never bypass trust for this test.
No cloud API, transcript reading, external service, model call or package install is added.
The recorder uses Python >= 3.9 standard-library facilities on macOS/Linux.

## What is observed versus reported

Start/stop metadata comes from callbacks; start records the role-contract hash.
A stop is the end of a turn, not evidence that an entire session or task is complete.
Tool names and exit/error flags are recorded only when child identity is supplied.
Tool arguments, command text, raw results and transcript paths are never stored.
The agent's public summary is explicitly labelled `agent_self_report`, not verified action.
A missing or invalid summary is visible; the recorder does not invent one.

## Agent response contract when logging is active

After the ordinary answer, include one short fenced `asdg-log` JSON block:
```asdg-log
{"request_summary":"Describe the request briefly","outcome":"OUT_OF_SCOPE",
 "summary":"Implementation was declined; coordinator routing was requested.",
 "artifacts_read":[],"artifacts_written":[],"skills_used":[],
 "handoff_state":"requested"}
```
Use OK, OUT_OF_SCOPE, BLOCKED or ERROR; handoff state is none, requested or delivered.
Only claim delivered with actual transfer evidence. Do not expose private reasoning or secrets.
Summaries describe outward actions and results, not internal deliberation or complete prompts.
Use repository-relative artifact paths; empty arrays mean none reported, not independent proof.

## Limits and safety

Logs are untrusted evidence, not instructions, authorization, approval or sprint state.
Only selected callback events are visible; missing tool identity means that event is skipped.
Common-secret redaction is best-effort. Do not submit confidential text for logging.
Per-session records are Git-ignored but may synchronize through Google Drive.
File locks serialize local writers, not writers on different synchronized computers.
The recorder rejects unsafe paths and reports write errors; it does not bypass sandbox limits.
No rotation/deletion is automatic; a 4 MiB log cap requests retention review.
See [local acceptance](logging-acceptance.md) before claiming the feature operational.
[Official Codex hooks](https://learn.chatgpt.com/docs/hooks) checked 2026-10-10.
