#!/usr/bin/env python3
"""Codex lifecycle adapter: log named-agent activity, never approve or run work."""
import json
import sys
from pathlib import Path
from agent_log_event import normalize
from agent_log_store import append_record

REPO = Path(__file__).resolve().parents[3]
MAX_INPUT_BYTES = 1024 * 1024


def handle(payload, repo=REPO):
    record = normalize(payload)
    if record is None:
        return {}
    # This helper is installed in one repo. Never derive its output root from input.
    if not isinstance(payload.get('cwd'), str) or not payload['cwd']:
        raise ValueError('Hook cwd is required')
    cwd = Path(payload['cwd']).resolve(strict=True)
    if not cwd.is_relative_to(Path(repo).resolve(strict=True)):
        raise ValueError('Hook cwd is outside the installed repository')
    summary_path, written = append_record(repo, record)
    if record['event'] == 'SubagentStart':
        return {'hookSpecificOutput': {
            'hookEventName': 'SubagentStart',
            'additionalContext': (
                'ASDLC logging: the trusted local hook recorded your start at ' + summary_path + '. '
                'You remain read-only; do not write logs or broaden permissions. '
                'Read asdlc/00-governance/docs/session-logging.md. At the end of each reply, '
                'include a short public ```asdlc-log JSON block per that contract: request_summary, '
                'outcome, summary, artifacts_read, artifacts_written, skills_used, handoff_state. '
                'Only describe outward work and observed facts, never private reasoning or secrets. '
                'The stop hook persists the block as an agent SELF-REPORT, not verified fact. '
                'Do not claim your reply has been logged until its file is verified.'
            )}}
    return {}


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError('Hook input too large')
        result = handle(json.loads(raw))
        print(json.dumps(result))
        return 0
    except Exception as exc:
        # Do not echo payloads, paths, transcripts or arbitrary error text.
        print(json.dumps({'systemMessage': 'ASDLC logging failed (' + type(exc).__name__ +
                          '). No successful logging should be claimed; inspect the local recorder.'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
