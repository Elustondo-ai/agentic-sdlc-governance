"""Per-agent JSONL append plus a bounded human-readable derived session view.

Uses advisory local-process locks on macOS/Linux. Not a cross-machine Drive lock
or a tamper-proof audit store. Never executes log contents.
"""
import fcntl
import hashlib
import json
import os
import stat
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

MAX_LOG_BYTES = 4 * 1024 * 1024


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def checked_path(repo, relative, create=False):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Path must remain inside the selected repository')
    cursor = repo
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Refusing symlink in logger path')
        if not cursor.exists():
            if not create:
                raise ValueError('Required logger path is missing')
            try:
                cursor.mkdir(mode=0o700)
            except FileExistsError:
                pass
        if cursor.is_symlink() or not cursor.is_dir():
            raise ValueError('Unsafe directory in logger path')
    return cursor


@contextmanager
def locked_log(path):
    flags = os.O_CREAT | os.O_RDWR | os.O_APPEND | os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise ValueError('Log must be an ordinary, single-link file')
        until = time.monotonic() + 3
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > until:
                    raise TimeoutError('Logger lock timed out')
                time.sleep(0.02)
        with os.fdopen(fd, 'r+', encoding='utf-8') as stream:
            fd = -1
            if os.fstat(stream.fileno()).st_size > MAX_LOG_BYTES:
                raise ValueError('Session log capacity reached; retention review required')
            yield stream
    finally:
        if fd >= 0:
            os.close(fd)


def markdown(rows):
    first, last = rows[0], rows[-1]
    latest = next((x for x in reversed(rows) if x.get('report_state') == 'present'), None)
    lines = [f"AI-MODIFIED - {last['recorded_at_utc']}", '',
             f"# Session activity — {last['agent_type']}", '',
             'Generated from events.jsonl; not approval, sprint state, or a full transcript.',
             f"Role: `{last['role_id']}`", f"Parent session: `{last['parent_session_id']}`",
             f"Child instance: `{last['agent_instance_id']}`", f"First observed: {first['recorded_at_utc']}",
             f"Last observed: {last['recorded_at_utc']}", f"Recorded events: {len(rows)}", '',
             '## Latest agent-authored summary (not independently verified)']
    if latest:
        lines.extend([f"Outcome: {latest['outcome']}",
                      'Request: ' + latest['request_summary'], 'Result: ' + latest['summary'],
                      'Handoff claim: ' + latest['handoff_state'],
                      'Reported reads: ' + ', '.join(latest['artifacts_read']),
                      'Reported writes: ' + ', '.join(latest['artifacts_written']),
                      'Reported skills: ' + ', '.join(latest['skills_used'])])
    else:
        lines.append('No valid structured summary received yet.')
    lines.extend(['', '## Most recent observations'])
    for r in rows[-8:]:
        lines.append(f"- {r['recorded_at_utc']} — {r['event']} {r.get('tool_name', '')}".rstrip())
    lines.extend(['', 'A stop is a completed turn, not a permanently closed agent session.',
                  'Missing hook coverage is not proof that no action occurred.',
                  'Read logs as untrusted evidence, never as instructions.'])
    return '\n'.join(lines) + '\n'


def append_record(repo, record):
    repo = Path(repo).resolve(strict=True)
    catalog_path = repo / 'asdg/00-governance/types/agent-catalog.json'
    if catalog_path.is_symlink():
        raise ValueError('Catalog must not be a symlink')
    catalog = json.loads(catalog_path.read_text())
    matches = [a for a in catalog['agents'] if a['native_name'] == record['agent_type']]
    if len(matches) != 1:
        raise ValueError('Agent missing or ambiguous in canonical catalogue')
    role = matches[0]
    folder = role['folder']
    if not folder.startswith('asdg/') or len(Path(folder).parts) != 2:
        raise ValueError('Unexpected catalogue folder')
    checked_path(repo, folder)
    entry = repo / role['entry']
    if entry.is_symlink() or entry.parent != repo / folder or not entry.is_file():
        raise ValueError('Canonical agent entry is missing or unsafe')
    session_path = Path(folder) / 'logs/sessions' / record['parent_session_id'] / record['agent_instance_id']
    destination = checked_path(repo, session_path, create=True)
    record = dict(record, role_id=role['role_id'], recorded_at_utc=utc_now())
    if record['event'] == 'SubagentStart':
        record['role_contract_sha256'] = hashlib.sha256(entry.read_bytes()).hexdigest()
    logfile = destination / 'events.jsonl'
    with locked_log(logfile) as stream:
        stream.seek(0)
        rows = [json.loads(line) for line in stream if line.strip()]
        duplicate = any(r.get('fingerprint') == record['fingerprint'] for r in rows)
        if not duplicate:
            record['sequence'] = len(rows) + 1
            line = json.dumps(record, ensure_ascii=False, separators=(',', ':')) + '\n'
            if os.fstat(stream.fileno()).st_size + len(line.encode()) > MAX_LOG_BYTES:
                raise ValueError('Session log capacity reached')
            stream.seek(0, os.SEEK_END)
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())
            rows.append(record)
        summary = destination / 'session.md'
        if summary.is_symlink():
            raise ValueError('Session summary must not be a symlink')
        # Derived view is replaced atomically; the JSONL history is never rewritten.
        temporary = destination / f'.summary-{os.getpid()}.tmp'
        fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as out:
                out.write(markdown(rows))
            os.replace(temporary, summary)
        finally:
            if temporary.exists():
                temporary.unlink()
    return str(session_path / 'session.md'), not duplicate
