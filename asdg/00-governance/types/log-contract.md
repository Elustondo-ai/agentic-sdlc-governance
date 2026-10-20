# Agent activity log contract — v0.1

## Input

One documented Codex hook JSON object on stdin, maximum 1 MiB.
Required attribution: `hook_event_name`, `agent_type`, `agent_id`, `session_id`, `cwd`.
Optional identifiers: `turn_id`, `tool_use_id`; source supplies them, never the model.
Recognize only catalogue names asdg_coordinator and asdg_01 through asdg_12.
Unknown hooks/agents and tool events without complete child identity produce no entry.
The repository is determined from the installed recorder, never from a supplied output path.

## Event output

Common fields: schema_version, record_source, event, role_id, agent_type,
parent_session_id, agent_instance_id, turn_id, recorded_at_utc, sequence, fingerprint.
An identifiable duplicate delivery is not appended twice.
Without stable event identity each delivery is retained; duplicates may require later review.
A SubagentStart adds role_contract_sha256, not a claim that the contract was followed.
Tool callbacks add tool_name, tool_use_id and available exit/error metadata only.
SubagentStop adds report_state: present, missing or invalid.
A valid public block adds evidence_kind=agent_self_report, outcome, request_summary,
summary, artifacts_read, artifacts_written, skills_used and handoff_state.
The summary reports claimed artifact references, not automatic file-access tracking.

## Invariants and failures

Output is restricted by catalogue to the agent's local logs/sessions/ subtree.
Each parent-session/child-instance pair has one append-only events.jsonl.
session.md is a derived latest view within 50 nonblank source lines; events.jsonl retains earlier entries.
Symlink paths, unsafe IDs, inconsistent catalogue entries and oversized logs are rejected.
A logger failure returns exit 1 with a content-minimized warning; no success is invented.
Successful callbacks emit valid JSON, never a permission decision or forced continuation.
Permission settings are observed, not changed. No caller-authority policy is added here.

## Privacy and interpretation

No raw prompts, commands, tool output, full transcripts, credentials or private reasoning.
Unknown report fields are discarded and common secret formats are redacted best-effort.
Free-text redaction cannot guarantee confidentiality; reviewers must check summaries.
Logs may be incomplete, duplicated without event IDs, or human-edited; not tamper-proof.
Read a reported refusal as a claim until runtime/code-change evidence supports it.
No event marks human approval, changes sprint state, or grants permissions.
