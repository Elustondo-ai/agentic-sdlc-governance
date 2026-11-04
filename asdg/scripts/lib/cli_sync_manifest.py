"""Read local repository identities, distribution snapshots and adopted baselines."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from cli_files import Conflict, read_bytes, safe_path

PROVIDER = 'elustondo.ai/asdg'
STATE = 'metadata/sync-state.json'
MANIFEST = 'metadata/MANIFEST.json'
INDEX = 'metadata/package-files.json'
DESCRIPTOR = 'metadata/distribution.json'


def digest(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def encoded(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired as exc:
        raise Conflict('Git identity inspection timed out; nothing synchronized.') from exc
    if result.returncode:
        raise Conflict('Cannot establish Git identity: ' + ' '.join(args))
    return result.stdout.strip()


def repository_id(remote: str) -> str:
    """Normalize HTTPS and SSH origin forms without storing credentials."""
    match = re.fullmatch(r'(?:[^/@:]+@)?([^/:]+):([^/].*)', remote)
    if '://' not in remote and match:
        host, path = match.groups()
    else:
        parsed = urlsplit(remote)
        if parsed.scheme not in ('https', 'http', 'ssh') or not parsed.hostname:
            raise Conflict('Repository origin must be an identifiable HTTP(S) or SSH URL.')
        host, path = parsed.hostname, parsed.path.lstrip('/')
    path = path.rstrip('/')
    if path.endswith('.git'):
        path = path[:-4]
    if not re.fullmatch(r'[\w.-]+(?:/[\w.-]+)+', path):
        raise Conflict('Invalid repository identity.')
    return host.lower() + '/' + path.lower()


def methodology_path(name: str) -> str:
    """Allow distribution areas only, never installed project/state locations."""
    p = PurePosixPath(name)
    top = p.parts[0] if p.parts else ''
    roots = {'AGENTS.md', 'README.md', 'LICENSE', 'CODEX-PROMPT.md',
             'admin', 'docs', 'metadata', 'scripts', 'skills', 'templates', 'tests', 'scaffolds'}
    if (not name or p.is_absolute() or p.as_posix() != name or '..' in p.parts or '\\' in name
            or any(c in name for c in '\n\r\0') or name == STATE
            or any(part in {'.git', '.asdg', '__pycache__', 'logs', 'build', 'components'} for part in p.parts)
            or (top not in roots and not re.fullmatch(r'(?:0[0-9]|1[0-2])-[a-z0-9-]+', top))
            or (len(p.parts) > 1 and top == 'docs' and p.parts[1] == 'asdg')
            or p.suffix == '.pyc'):
        raise Conflict('Outside portable methodology scope: ' + name)
    return name


def read_json(path: Path) -> dict:
    raw = read_bytes(path)
    value = json.loads(raw) if raw is not None else None
    if not isinstance(value, dict):
        raise Conflict('Missing or invalid JSON object: ' + str(path))
    return value


def hash_map(value) -> dict:
    if not isinstance(value, dict):
        raise Conflict('Invalid methodology hash manifest.')
    for name, value_hash in value.items():
        methodology_path(name)
        if not isinstance(value_hash, str) or not re.fullmatch(r'[0-9a-f]{64}', value_hash):
            raise Conflict('Invalid methodology hash: ' + name)
    return value


def read_state(core: Path) -> dict:
    path = safe_path(core, STATE)
    if read_bytes(path) is None:
        return {'schema_version': 1, 'upstreams': {}}
    state = read_json(path)
    if state.get('schema_version') != 1 or not isinstance(state.get('upstreams'), dict):
        raise Conflict('Invalid methodology sync state; restore it before synchronizing.')
    for identity, entry in state['upstreams'].items():
        if not isinstance(entry, dict) or entry.get('operation') not in ('promote', 'upgrade'):
            raise Conflict('Invalid adopted methodology record.')
        files = hash_map(entry.get('files'))
        if (entry.get('source_repository') != identity or not isinstance(entry.get('target_repository'), str)
                or not isinstance(entry.get('source_commit'), str)
                or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', entry['source_commit'])
                or not isinstance(entry.get('version'), str)
                or entry.get('snapshot_sha256') != digest(encoded(files))):
            raise Conflict('Invalid adopted methodology identity or snapshot hash.')
    return state


def snapshot(location: str | Path) -> dict:
    requested = Path(location).expanduser()
    if requested.is_symlink() or not requested.is_dir():
        raise Conflict('Expected an existing, nonsymlink Git repository root: ' + str(requested))
    root = requested.resolve()
    if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
        raise Conflict('Supply the Git repository root, not a subdirectory.')
    identity = repository_id(git(root, 'remote', 'get-url', 'origin'))
    head = git(root, 'rev-parse', 'HEAD')
    core = safe_path(root, 'asdg')
    descriptor = read_json(safe_path(core, DESCRIPTOR))
    version = descriptor.get('version')
    if (descriptor.get('schema_version') != 1 or descriptor.get('provider') != PROVIDER
            or descriptor.get('installation_mode') != 'embedded-distribution'
            or not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?', version)):
        raise Conflict('Cannot establish the ASDG provider and source version.')
    manifest_raw = read_bytes(safe_path(core, MANIFEST))
    manifest = read_json(safe_path(core, MANIFEST))
    if manifest.get('schema_version') != 1 or manifest.get('version') != version:
        raise Conflict('Distribution descriptor and manifest versions disagree.')
    historical = hash_map(manifest.get('files'))
    tracked = set(git(root, 'ls-files', '-z', '--', 'asdg/').split('\0')) - {''}
    index_raw = read_bytes(safe_path(core, INDEX))
    if index_raw is not None:
        index = json.loads(index_raw)
        names = index.get('files') if isinstance(index, dict) else None
        if (not isinstance(index, dict) or index.get('schema_version') != 1
                or not isinstance(names, list) or not all(isinstance(n, str) for n in names)
                or len(set(names)) != len(names) or not {DESCRIPTOR, MANIFEST, INDEX} <= set(names)):
            raise Conflict('Invalid portable package file list.')
    else:
        # Legacy portable pilots predate the index: only committed/indexed ASDG paths qualify.
        names = [p.removeprefix('asdg/') for p in tracked if p != 'asdg/' + STATE]
        if not {DESCRIPTOR, MANIFEST} <= set(names):
            raise Conflict('Legacy pilot lacks versioned distribution metadata.')
    data = {}
    for name in sorted(names):
        methodology_path(name)
        raw = read_bytes(safe_path(core, name))
        if raw is None and index_raw is not None:
            raise Conflict('Package list references a missing file: ' + name)
        if raw is not None:
            data[name] = raw
    hashes = {p: digest(raw) for p, raw in data.items()}
    current = {p: h for p, h in hashes.items() if p != MANIFEST}
    matches = current == historical
    differences = {
        'added': sorted(set(current) - set(historical)),
        'modified': sorted(p for p in current.keys() & historical.keys() if current[p] != historical[p]),
        'deleted': sorted(set(historical) - set(current)),
    }
    catalog = read_json(safe_path(core, '00-governance/types/agent-catalog.json'))
    roles = catalog.get('agents', [])
    if (not isinstance(roles, list) or len(roles) != 13
            or not all(isinstance(r, dict) and type(r.get('stage')) is int for r in roles)
            or sorted(r['stage'] for r in roles) != list(range(13))
            or any(r.get('role_id') != ('ASDG-COORDINATOR' if r['stage'] == 0 else f"ASDG-{r['stage']:02d}")
                   or r.get('native_name') != ('asdg_coordinator' if r['stage'] == 0 else f"asdg_{r['stage']:02d}")
                   for r in roles)):
        raise Conflict('Canonical lifecycle identities cannot be established.')
    state = read_state(core)
    binding_raw = read_bytes(safe_path(root, '.asdg/project.json'))
    return {'root': root, 'core': core, 'descriptor': descriptor, 'data': data, 'hashes': hashes,
            'tracked': tracked, 'state': state, 'manifest_raw': manifest_raw, 'baseline': historical,
            'binding_raw': binding_raw,
            'info': {'root': str(root), 'repository': identity, 'head': head, 'version': version,
                     'snapshot_sha256': digest(encoded(hashes)), 'binding_sha256': digest(binding_raw),
                     'manifest_matches_worktree': matches,
                     'snapshot_kind': 'MANIFEST_MATCHED_DISTRIBUTION' if matches else 'WORKING_TREE_SNAPSHOT',
                     'delivery_manifest': {'sha256': digest(manifest_raw), 'version': manifest['version'],
                                           'status': 'MATCH' if matches else 'STALE', 'differences': differences},
                     'validation_status': 'NOT_ESTABLISHED', 'human_approval_status': 'NOT_ESTABLISHED',
                     'selection': 'package-files' if index_raw is not None else 'legacy-git-tracked'}}


def baseline(source: dict, target: dict) -> tuple[dict, str]:
    source_id, target_id = source['info']['repository'], target['info']['repository']
    for owner, other in ((target, source_id), (source, target_id)):
        entry = owner['state']['upstreams'].get(other)
        if entry:
            if entry.get('target_repository') != owner['info']['repository']:
                raise Conflict('Adoption record belongs to another repository.')
            return entry['files'], 'adopted snapshot from ' + other
    # An exact shared delivery manifest establishes ancestry for older pilots.
    candidates = []
    for item in (source, target):
        paths = [safe_path(item['core'], MANIFEST)]
        deliveries = safe_path(item['core'], 'metadata/deliveries')
        if deliveries.exists():
            paths += sorted(deliveries.glob('*.json'))
        candidates.append([(read_bytes(safe_path(item['core'], p.relative_to(item['core']))), p.name)
                           for p in paths])
    common = {raw: name for raw, name in candidates[0]
              if raw is not None and any(raw == other for other, _ in candidates[1])}
    # A current endpoint identifies its adopted delivery better than arbitrary archive order.
    selected = next((raw for raw in (source['manifest_raw'], target['manifest_raw']) if raw in common), None)
    if selected is None and len(common) == 1:
        selected = next(iter(common))
    if selected is not None:
        value = json.loads(selected)
        files = dict(hash_map(value.get('files')))
        files[MANIFEST] = digest(selected)
        return files, 'shared delivery manifest ' + common[selected]
    if common:
        return {}, 'none: multiple shared historical deliveries; reconcile or restore an adoption record'
    return {}, 'none: differing existing files require reconciliation'


def adopted_binding(root: Path, raw: bytes, version: str, catalog_hash: str) -> bool:
    """Recognize an explicit upgrade without rewriting the original project binding."""
    entries = read_state(safe_path(root, 'asdg'))['upstreams']
    if not entries:
        return False
    identity = repository_id(git(root, 'remote', 'get-url', 'origin'))
    for entry in entries.values():
        if (entry.get('operation') == 'upgrade' and entry.get('target_repository') == identity
                and entry.get('target_binding_sha256') == digest(raw) and entry.get('version') == version
                and entry['files'].get('00-governance/types/agent-catalog.json') == catalog_hash):
            return True
    return False
