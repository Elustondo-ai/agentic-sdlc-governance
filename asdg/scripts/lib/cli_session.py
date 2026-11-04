"""Check the default 00 Governance bootstrap and the separate ASDG Admin package."""
from __future__ import annotations

import json
from pathlib import Path

from cli_files import Conflict, read_bytes, safe_path
from cli_model import REPO, catalogue

DEFAULT_ROLE = 'ASDG-COORDINATOR'
SHARED_SOURCES = (
    'asdg/AGENTS.md',
    'asdg/skills/asdg-focus/session-policy.md',
    'asdg/skills/asdg-focus/session-state.md',
    'asdg/00-governance/docs/runtime-contract.md',
    'asdg/00-governance/types/interaction-contract.md',
)


def entry_point_loads_distribution(agents: bytes | None) -> bool:
    """True when an ASDG-managed block, of any version, references asdg/AGENTS.md; project text does not count."""
    if agents is None:
        return False
    begin = agents.find(b'<!-- ASDG:BEGIN')
    end = agents.find(b'<!-- ASDG:END -->', begin)
    return begin >= 0 and end > begin and b'asdg/AGENTS.md' in agents[begin:end]


def governance_bootstrap(root: Path, repo: Path = REPO) -> dict:
    """Report whether a new session can start under the default role; never select a role itself."""
    missing = []
    if not entry_point_loads_distribution(read_bytes(safe_path(root, 'AGENTS.md'))):
        missing.append('AGENTS.md: client entry point does not load asdg/AGENTS.md')
    try:
        entries, _ = catalogue(repo)
        role = next(a for a in entries if a.get('role_id') == DEFAULT_ROLE)
        sources = [role['entry'], f"{role['folder']}/types/contract.md", role['skill']]
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        role, sources = {}, []
        missing.append(f'catalogue: {DEFAULT_ROLE} entry unavailable ({exc})')
    for relative in (*SHARED_SOURCES, *sources):
        if read_bytes(safe_path(repo, relative)) is None:
            missing.append(f'{relative}: required governance source missing')
    return {'default_role': DEFAULT_ROLE, 'native_name': role.get('native_name'),
            'label': '00 Governance', 'role_none_permitted': False,
            'status': 'BLOCKED' if missing else 'READY',
            'blocked_code': 'GOVERNANCE_BOOTSTRAP' if missing else None, 'missing': missing,
            'enforcement': 'INSTRUCTIONAL_ONLY'}


ADMIN_REGISTRATION = 'asdg/admin/types/admin-role.json'
ADMIN_FIXED = {'schema_version': 1, 'role_id': 'ASDG-ADMIN', 'short_label': 'Admin', 'title': 'ASDG Admin',
               'lifecycle_stage': None, 'folder': 'asdg/admin', 'activation': 'explicit-human-selection-only',
               'default': False, 'native_adapter': None}
ADMIN_SOURCES = ('entry', 'contract', 'skill')


def validate_admin(repo: Path = REPO) -> dict:
    """Validate the Admin package kept outside the lifecycle catalogue; raise Conflict naming the first problem."""
    raw = read_bytes(safe_path(repo, ADMIN_REGISTRATION))
    if raw is None:
        raise Conflict(f'Admin registration missing: {ADMIN_REGISTRATION}')
    try:
        value = json.loads(raw)
    except ValueError as exc:
        raise Conflict(f'Admin registration is not valid JSON: {exc}') from exc
    if not isinstance(value, dict) or set(value) != {*ADMIN_FIXED, *ADMIN_SOURCES, 'selectors'}:
        raise Conflict('Admin registration has missing or unexpected fields.')
    for key, expected in ADMIN_FIXED.items():
        if value[key] != expected or type(value[key]) is not type(expected):
            raise Conflict(f'Admin registration field {key} must be {json.dumps(expected)}.')
    selectors = value['selectors']
    if (not isinstance(selectors, list) or not selectors
            or not all(isinstance(s, str) and s.strip() == s and s for s in selectors)):
        raise Conflict('Admin registration selectors must be a non-empty list of explicit names.')
    for key in ADMIN_SOURCES:
        relative = value[key]
        if (not isinstance(relative, str) or not relative.startswith(ADMIN_FIXED['folder'] + '/')
                or '..' in Path(relative).parts):
            raise Conflict(f'Admin registration {key} must be a path inside asdg/admin/.')
        if read_bytes(safe_path(repo, relative)) is None:
            raise Conflict(f'Admin {key} source missing: {relative}')
    return value
