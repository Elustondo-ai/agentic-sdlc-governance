"""Allow-listed, content-minimized Codex hook records; no transcript parsing."""
import hashlib
import json
import re
import uuid
from pathlib import PurePosixPath

EVENTS = {'SubagentStart', 'SubagentStop', 'PreToolUse', 'PostToolUse'}
OUTCOMES = {'OK', 'OUT_OF_SCOPE', 'BLOCKED', 'ERROR'}
IDENTIFIER = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z')
ROLE = re.compile(r'asdg_(?:coordinator|0[1-9]|1[0-2])\Z')
REPORT = re.compile(r'^```asdg-log\s*\n(.*?)\n```\s*$', re.M | re.S)


def identifier(value, field):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError('Missing or invalid ' + field)
    return value


def clean_text(value, limit=400):
    if not isinstance(value, str):
        return ''
    # Defense in depth. It is not possible to recognize every secret in free text.
    value = re.sub(r'(?i)\bBearer\s+\S+', 'Bearer [REDACTED]', value)
    value = re.sub(r'\b(?:sk-|gh[pousr]_|github_pat_)[A-Za-z0-9_-]+', '[REDACTED]', value)
    value = re.sub(r'(?i)\b(api[_ -]?key|password|secret|token)\s*[:=]\s*\S+',
                   r'\1=[REDACTED]', value)
    value = ' '.join(value.split())
    return value[:limit]


def relative_paths(value):
    if not isinstance(value, list):
        return []
    result = []
    for item in value[:12]:
        if not isinstance(item, str) or len(item) > 240:
            continue
        p = PurePosixPath(item)
        if (p.is_absolute() or '..' in p.parts or '\\' in item or '\n' in item
                or '\r' in item or ':' in item or '\x00' in item):
            continue
        if any(x in {'.env', '.git', 'credentials', 'secrets'} for x in p.parts):
            continue
        if re.fullmatch(r'[A-Za-z0-9_./-]+', item):
            result.append(item)
    return result


def public_report(message):
    """Only read the explicitly labelled public summary, never the full answer."""
    matches = REPORT.findall(message if isinstance(message, str) else '')
    if not matches:
        return {'report_state': 'missing'}
    try:
        if len(matches[-1]) > 8192:
            raise ValueError('Oversized report')
        report = json.loads(matches[-1])
        if not isinstance(report, dict) or report.get('outcome') not in OUTCOMES:
            raise ValueError('Invalid report')
        return {
            'report_state': 'present', 'evidence_kind': 'agent_self_report',
            'request_summary': clean_text(report.get('request_summary')),
            'summary': clean_text(report.get('summary'), 600),
            'outcome': report['outcome'],
            'artifacts_read': relative_paths(report.get('artifacts_read')),
            'artifacts_written': relative_paths(report.get('artifacts_written')),
            'skills_used': relative_paths(report.get('skills_used')),
            'handoff_state': report.get('handoff_state')
            if report.get('handoff_state') in {'none', 'requested', 'delivered'} else 'unknown',
        }
    except (ValueError, TypeError):
        return {'report_state': 'invalid'}


def normalize(payload):
    """Return None for unrelated/unsupported events without recording private data."""
    if not isinstance(payload, dict):
        raise ValueError('Expected one JSON object')
    event = payload.get('hook_event_name')
    name = payload.get('agent_type')
    if event not in EVENTS:
        return None
    # Tool hooks may omit child identity in some versions: do not invent attribution.
    if not isinstance(name, str) or not ROLE.fullmatch(name):
        return None
    if event in {'PreToolUse', 'PostToolUse'} and not payload.get('agent_id'):
        return None
    record = {
        'schema_version': 1, 'record_source': 'codex_hook',
        'event': event, 'agent_type': name,
        'parent_session_id': identifier(payload.get('session_id'), 'session_id'),
        'agent_instance_id': identifier(payload.get('agent_id'), 'agent_id'),
        'turn_id': identifier(payload['turn_id'], 'turn_id') if payload.get('turn_id') else None,
    }
    mode = payload.get('permission_mode')
    if mode in {'default', 'acceptEdits', 'plan', 'dontAsk', 'bypassPermissions'}:
        record['permission_mode'] = mode
    if event in {'PreToolUse', 'PostToolUse'}:
        tool = payload.get('tool_name', '')
        record['tool_name'] = tool if isinstance(tool, str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,160}', tool) else 'unknown'
        if payload.get('tool_use_id'):
            record['tool_use_id'] = identifier(payload['tool_use_id'], 'tool_use_id')
        response = payload.get('tool_response')
        if isinstance(response, dict):
            if type(response.get('exit_code')) is int:
                record['exit_code'] = response['exit_code']
            if type(response.get('isError')) is bool:
                record['tool_reported_error'] = response['isError']
        record['tool_content_policy'] = 'arguments-and-output-not-stored'
    if event == 'SubagentStop':
        record.update(public_report(payload.get('last_assistant_message')))
        record['stop_semantics'] = 'turn_stopped_not_session_closed'
    # Without an event identity, prefer extra records over silently merging work.
    if not record['turn_id'] or (event in {'PreToolUse', 'PostToolUse'} and not record.get('tool_use_id')):
        record['delivery_nonce'] = uuid.uuid4().hex
    stable = json.dumps(record, sort_keys=True, ensure_ascii=True).encode()
    record['fingerprint'] = hashlib.sha256(stable).hexdigest()
    return record
