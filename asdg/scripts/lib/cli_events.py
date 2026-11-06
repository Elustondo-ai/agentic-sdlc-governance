"""Durable, retry-safe shared turn events; records are evidence, never authority."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import uuid
from contextlib import contextmanager
from pathlib import Path

from agent_log_event import clean_text
from agent_log_store import utc_now
from cli_files import Conflict
from cli_model import catalogue

MAX_INPUT_BYTES = 16 * 1024
MAX_EVENT_BYTES = 80 * 1024
EVENT_ID = re.compile(r'evt-[0-9a-f]{64}\Z')
KEY = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,199}\Z')
HASH = re.compile(r'[0-9a-f]{64}\Z')
OUTCOMES = {'OK', 'OUT_OF_SCOPE', 'BLOCKED', 'ERROR', 'REVIEW_REQUIRED', 'NO_CHANGE'}
REQUIRED = {'idempotency_key', 'role_id', 'focus', 'summary', 'outcome', 'evidence'}
METADATA = {'schema_version', 'record_source', 'event_id', 'recorded_at_utc'}
DIRECTORY = '.asdg/events'


def _text(value, field, limit, *, public=False):
    if (not isinstance(value, str) or not value.strip() or len(value) > limit
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise Conflict(f'{field} must be nonempty text of at most {limit} characters without controls.')
    # Keep reference strings exact. Summaries reuse the hook recorder's best-effort redaction.
    return clean_text(value, limit=limit) if public else value


def normalize_payload(root, payload):
    """Validate the public JSON object; reject rather than discard unknown fields."""
    if not isinstance(payload, dict) or not REQUIRED <= payload.keys():
        raise Conflict('An event requires idempotency_key, role_id, focus, summary, outcome and evidence.')
    if payload.keys() - REQUIRED - {'caused_by'}:
        raise Conflict('Unknown event fields; timestamp and event ID belong to the recorder.')
    key = payload['idempotency_key']
    if not isinstance(key, str) or not KEY.fullmatch(key):
        raise Conflict('Invalid idempotency_key; use one stable 1–200 character identifier per turn.')
    roles, _ = catalogue(Path(root))
    role = payload['role_id']
    if not isinstance(role, str) or role not in {a['role_id'] for a in roles} | {'ASDG-ADMIN'}:
        raise Conflict('role_id must identify one canonical ASDG role or ASDG-ADMIN.')
    outcome = payload['outcome']
    if not isinstance(outcome, str) or outcome not in OUTCOMES:
        raise Conflict('Unsupported event outcome.')
    evidence = payload['evidence']
    if not isinstance(evidence, list) or len(evidence) > 32:
        raise Conflict('evidence must be a list of at most 32 reference objects.')
    references = []
    for item in evidence:
        if (not isinstance(item, dict) or 'ref' not in item
                or item.keys() - {'ref', 'sha256'}):
            raise Conflict('Each evidence item requires ref and permits only an optional sha256.')
        reference = {'ref': _text(item['ref'], 'evidence ref', 1000)}
        if 'sha256' in item:
            digest = item['sha256']
            if not isinstance(digest, str) or not HASH.fullmatch(digest):
                raise Conflict('Evidence sha256 must be exactly 64 lowercase hexadecimal characters.')
            reference['sha256'] = digest
        references.append(reference)
    result = {'idempotency_key': key, 'role_id': role,
              'focus': _text(payload['focus'], 'focus', 240, public=True),
              'summary': _text(payload['summary'], 'summary', 2000, public=True),
              'outcome': outcome, 'evidence': references}
    if 'caused_by' in payload:
        result['caused_by'] = _event_id(payload['caused_by'])
    return result


def _event_id(value):
    if not isinstance(value, str) or not EVENT_ID.fullmatch(value):
        raise Conflict('Invalid event ID.')
    return value


def event_id_for(key):
    """The caller chooses the retry key; only the recorder determines the event ID."""
    return 'evt-' + hashlib.sha256(key.encode('utf-8')).hexdigest()


@contextmanager
def _directory(root, *, create=False):
    """Pin every storage directory through no-follow file descriptors."""
    root = Path(root).resolve(strict=True)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptors = [os.open(root, flags)]
    missing = False
    try:
        for part in ('.asdg', 'events'):
            parent = descriptors[-1]
            if create:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=parent)
                except FileExistsError:
                    pass
                # Also heals the durability gap after an interrupted mkdir/fsync.
                os.fsync(parent)
            try:
                descriptors.append(os.open(part, flags, dir_fd=parent))
            except FileNotFoundError:
                if create:
                    raise
                missing = True
                break
        yield None if missing else descriptors[-1]
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _read(root, directory_fd, event_id, *, durable=False):
    """Read only a bounded ordinary file; optional fsync confirms a retry receipt."""
    descriptor = os.open(event_id + '.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=directory_fd)
    with os.fdopen(descriptor, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_EVENT_BYTES:
            raise Conflict('Event must be an ordinary bounded JSON file.')
        data = stream.read(MAX_EVENT_BYTES + 1)
        if len(data) > MAX_EVENT_BYTES:
            raise Conflict('Event exceeds the supported size.')
        record = json.loads(data)
        if (not isinstance(record, dict) or record.keys() - REQUIRED - {'caused_by'} - METADATA
                or record.get('schema_version') != 1 or record.get('record_source') != 'agent_self_report'
                or record.get('event_id') != event_id):
            raise Conflict('Unsupported or inconsistent recorded event.')
        timestamp = record.get('recorded_at_utc')
        if not isinstance(timestamp, str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z', timestamp):
            raise Conflict('Recorded event is missing its UTC timestamp.')
        payload = {key: value for key, value in record.items() if key not in METADATA}
        if normalize_payload(root, payload) != payload or event_id_for(payload['idempotency_key']) != event_id:
            raise Conflict('Recorded event contents do not match its identity.')
        if durable:
            os.fsync(stream.fileno())
    return record


def record_event(root, payload):
    """Durably publish once, or return the original receipt for an identical retry."""
    root = Path(root).resolve(strict=True)
    normalized = normalize_payload(root, payload)
    event_id = event_id_for(normalized['idempotency_key'])
    name = event_id + '.json'
    record = dict(normalized, schema_version=1, record_source='agent_self_report',
                  event_id=event_id, recorded_at_utc=utc_now())
    encoded = (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if len(encoded) > MAX_EVENT_BYTES:
        raise Conflict('Event exceeds the supported size.')
    duplicate = False
    with _directory(root, create=True) as directory_fd:
        temporary = '.event-' + uuid.uuid4().hex + '.tmp'
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                             0o600, dir_fd=directory_fd)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                # Hard-link publication is atomic and cannot overwrite another writer.
                os.link(temporary, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd,
                        follow_symlinks=False)
            except FileExistsError:
                previous = _read(root, directory_fd, event_id, durable=True)
                old_payload = {key: value for key, value in previous.items() if key not in METADATA}
                if old_payload != normalized:
                    raise Conflict('Idempotency key already records different content; do not create a new key for this turn.')
                duplicate = True
        finally:
            os.unlink(temporary, dir_fd=directory_fd)
        os.fsync(directory_fd)
    return {'event_id': event_id, 'recorded': True, 'duplicate': duplicate,
            'path': DIRECTORY + '/' + name}


def read_event(root, event_id):
    """Return the same persisted record to Governance, specialists and developers."""
    event_id = _event_id(event_id)
    with _directory(root) as directory_fd:
        if directory_fd is None:
            raise Conflict('Event was not found.')
        try:
            return _read(root, directory_fd, event_id)
        except FileNotFoundError as exc:
            raise Conflict('Event was not found.') from exc


def list_events(root):
    """Return the readable project feed, ordered by recorder time then event ID."""
    with _directory(root) as directory_fd:
        if directory_fd is None:
            return []
        names = sorted(name for name in os.listdir(directory_fd)
                       if name.endswith('.json') and EVENT_ID.fullmatch(name[:-5]))
        records = [_read(root, directory_fd, name[:-5]) for name in names]
    return sorted(records, key=lambda record: (record['recorded_at_utc'], record['event_id']))
