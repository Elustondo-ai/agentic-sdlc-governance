"""Bounded, private diagnostic copies; never accepted baseline artifacts."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path

from cli_baseline_diagnostics import SECRET, sanitize_text
from cli_files import Conflict, safe_path

PREFIX = Path('docs/asdg/00-governance/diagnostics')
MAX_ENTRIES, MAX_ARTIFACTS = 128, 30
MAX_SCAN_FILE, MAX_SCAN_TOTAL = 2 * 1024 * 1024, 4 * 1024 * 1024
MAX_COPY_FILE, MAX_COPY_TOTAL = 128 * 1024, 512 * 1024
MAX_RECORD_STRING, MAX_RECORD_NODES = 4096, 128
TEXT_NAMES = {'speaker-notes.md', 'visual.mmd', 'visual.puml', 'visual.svg'}
BINARY_NAMES = {'visual.png', 'visual.jpg', 'visual.jpeg', 'visual.webp'}
UNIT = re.compile(r'\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\Z')
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _record(value, changes: dict, budget: list[int], depth: int = 0):
    """Bound metadata defensively even when a caller supplies unexpected records."""
    budget[0] -= 1
    if budget[0] < 0 or depth > 5:
        changes['truncated'] += 1
        return '[OMITTED: record limit]'
    if isinstance(value, str):
        cleaned = sanitize_text(value, limit=max(MAX_RECORD_STRING, len(value) * 4 + 64),
                                multiline=True)
        if '[REDACTED' in cleaned and cleaned != value:
            changes['redacted'] += 1
        if len(cleaned) > MAX_RECORD_STRING:
            changes['truncated'] += 1
        if cleaned != value:
            changes['sanitized'] += 1
        return cleaned[:MAX_RECORD_STRING]
    if isinstance(value, dict):
        result = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= 32 or budget[0] < 1:
                changes['truncated'] += 1
                result['_omitted'] = 'record limit'
                break
            raw_key = str(key)
            safe_key = sanitize_text(raw_key, limit=max(80, len(raw_key) * 4 + 64))
            if safe_key != raw_key:
                changes['sanitized'] += 1
                if '[REDACTED' in safe_key:
                    changes['redacted'] += 1
            if len(safe_key) > 80:
                changes['truncated'] += 1
            result[safe_key[:80]] = _record(item, changes, budget, depth + 1)
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for index, item in enumerate(value):
            if index >= 32 or budget[0] < 1:
                changes['truncated'] += 1
                result.append('[OMITTED: record limit]')
                break
            result.append(_record(item, changes, budget, depth + 1))
        return result
    if value is None or isinstance(value, (bool, int, float)):
        return value
    changes['sanitized'] += 1
    return '[OMITTED: unsupported record type]'


def _open_destination(root: Path, relative: Path) -> int:
    """Create a new bundle without following links or changing existing folders."""
    if (relative.is_absolute() or relative.parts[:len(PREFIX.parts)] != PREFIX.parts
            or len(relative.parts) != len(PREFIX.parts) + 2
            or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', part)
                   for part in relative.parts[len(PREFIX.parts):])):
        raise Conflict('Unsafe failure-evidence destination.')
    safe_path(root, relative)
    current = os.open(root, DIR_FLAGS)
    try:
        for index, part in enumerate(relative.parts):
            created = False
            try:
                os.mkdir(part, mode=0o700, dir_fd=current)
                created = True
            except FileExistsError:
                if index == len(relative.parts) - 1:
                    raise Conflict('Failure-evidence bundle already exists; refusing overwrite.')
            next_fd = os.open(part, DIR_FLAGS, dir_fd=current)
            os.close(current)
            current = next_fd
            if index >= len(PREFIX.parts) - 1:
                mode = stat.S_IMODE(os.fstat(current).st_mode)
                if mode & 0o077:
                    raise Conflict('Failure-evidence directory must have private permissions.')
            if created:
                os.fchmod(current, 0o700)
        return current
    except BaseException:
        os.close(current)
        raise


def _write(directory: int, name: str, data: bytes) -> None:
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600, dir_fd=directory)
    with os.fdopen(fd, 'wb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def retain_failure(root: Path, relative: Path, workspace: Path, metadata: dict,
                   diagnostic: dict, runtime: dict) -> dict:
    """Retain safe rejected output before cleanup; preservation errors propagate."""
    relative = Path(relative)
    bundle_fd = _open_destination(Path(root), relative)
    changes = {'redacted': 0, 'sanitized': 0, 'truncated': 0}
    budget = [MAX_RECORD_NODES]
    manifest = {
        'schema_version': 1,
        'status': 'REJECTED_UNVALIDATED_DIAGNOSTIC_EVIDENCE',
        'validated': False, 'promoted': False, 'approved': False,
        'retained_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'invocation': _record(metadata, changes, budget),
        'diagnostic': _record(diagnostic, changes, budget),
        'runtime': _record(runtime, changes, budget),
        'record_processing': changes,
        'artifacts': [], 'omissions': [], 'truncations': [],
        'limits': {'entries': MAX_ENTRIES, 'artifacts': MAX_ARTIFACTS,
                   'scan_file_bytes': MAX_SCAN_FILE, 'scan_total_bytes': MAX_SCAN_TOTAL,
                   'copy_file_bytes': MAX_COPY_FILE, 'copy_total_bytes': MAX_COPY_TOTAL},
        'copy_format': 'Inert UTF-8 .txt copies; content may be sanitized or truncated.',
    }
    counters = {'entries': 0, 'scanned': 0, 'retained': 0}

    def omit(path, reason):
        manifest['omissions'].append({'path': sanitize_text(path, limit=320), 'reason': reason})

    def count_entry() -> bool:
        counters['entries'] += 1
        if counters['entries'] > MAX_ENTRIES:
            if not any(item['reason'] == 'entry_limit' for item in manifest['omissions']):
                omit('output/', 'entry_limit')
            return False
        return True

    def copy_file(unit_fd: int, name: str, source_path: str) -> None:
        if name in BINARY_NAMES:
            omit(source_path, 'binary_visual_not_retained')
            return
        if name not in TEXT_NAMES:
            omit(source_path, 'unsupported_artifact_path')
            return
        if len(manifest['artifacts']) >= MAX_ARTIFACTS:
            omit(source_path, 'artifact_limit')
            return
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=unit_fd)
        except OSError:
            omit(source_path, 'unreadable_or_symlink')
            return
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                omit(source_path, 'nonregular_or_hardlinked')
                return
            if info.st_size > MAX_SCAN_FILE or counters['scanned'] + info.st_size > MAX_SCAN_TOTAL:
                omit(source_path, 'scan_byte_limit')
                return
            data = stream.read(info.st_size)
            after = os.fstat(stream.fileno())
            counters['scanned'] += len(data)
            if (len(data) != info.st_size or after.st_size != info.st_size
                    or after.st_mtime_ns != info.st_mtime_ns or after.st_nlink != 1):
                omit(source_path, 'changed_during_read')
                return
        if SECRET.search(data):
            omit(source_path, 'sensitive_content_entire_artifact_omitted')
            return
        try:
            text = data.decode('utf-8')
        except UnicodeError:
            omit(source_path, 'non_utf8_binary')
            return
        if '\0' in text:
            omit(source_path, 'binary_content')
            return
        available = min(MAX_COPY_FILE, MAX_COPY_TOTAL - counters['retained'])
        if available <= 0:
            omit(source_path, 'copy_byte_limit')
            return
        # Sanitize the complete scanned text before clipping so a secret or unsafe
        # escape split at a truncation boundary cannot leak its prefix.
        cleaned = sanitize_text(text, limit=len(text) * 4 + 64, multiline=True)
        encoded = cleaned.encode('utf-8')
        retained = encoded[:available].decode('utf-8', errors='ignore').encode('utf-8')
        truncated = len(retained) < len(encoded)
        target = f'rejected-{len(manifest["artifacts"]) + 1:03d}-{name}.txt'
        _write(bundle_fd, target, retained)
        counters['retained'] += len(retained)
        entry = {'artifact': sanitize_text(source_path, limit=320), 'copy': target,
                 'original_bytes': len(data), 'original_sha256': _digest(data),
                 'retained_bytes': len(retained), 'retained_sha256': _digest(retained),
                 'sanitized': cleaned != text,
                 'redacted': '[REDACTED' in cleaned and cleaned != text,
                 'truncated': truncated,
                 'status': 'REJECTED_UNVALIDATED'}
        manifest['artifacts'].append(entry)
        if truncated:
            manifest['truncations'].append({'artifact': entry['artifact'], 'reason': 'copy_byte_limit',
                                            'original_bytes': len(data), 'retained_bytes': len(retained)})

    try:
        try:
            workspace_fd = os.open(workspace, DIR_FLAGS)
        except OSError:
            omit('output/', 'workspace_unreadable_or_symlink')
        else:
            try:
                try:
                    output_fd = os.open('output', DIR_FLAGS, dir_fd=workspace_fd)
                except OSError:
                    omit('output/', 'output_absent_nonregular_or_symlink')
                else:
                    try:
                        with os.scandir(output_fd) as units:
                            for unit in units:
                                if not count_entry():
                                    break
                                unit_path = 'output/' + unit.name
                                if not UNIT.fullmatch(unit.name) or not unit.is_dir(follow_symlinks=False):
                                    omit(unit_path, 'unexpected_unit_or_symlink')
                                    continue
                                try:
                                    unit_fd = os.open(unit.name, DIR_FLAGS, dir_fd=output_fd)
                                except OSError:
                                    omit(unit_path, 'unit_unreadable_or_symlink')
                                    continue
                                try:
                                    with os.scandir(unit_fd) as files:
                                        for item in files:
                                            if not count_entry():
                                                break
                                            copy_file(unit_fd, item.name, unit_path + '/' + item.name)
                                finally:
                                    os.close(unit_fd)
                                if counters['entries'] > MAX_ENTRIES:
                                    break
                    finally:
                        os.close(output_fd)
            finally:
                os.close(workspace_fd)
        manifest['observed'] = counters
        encoded = (json.dumps(manifest, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode('utf-8')
        _write(bundle_fd, 'manifest.json', encoded)
    finally:
        os.close(bundle_fd)
    return {'path': relative.as_posix(), 'manifest_path': (relative / 'manifest.json').as_posix(),
            'manifest_sha256': _digest(encoded), 'artifacts': manifest['artifacts'],
            'omissions': manifest['omissions'], 'truncations': manifest['truncations'],
            'status': manifest['status']}
