"""Authoritative sprint state and fail-closed, path-based implementation gate."""
from __future__ import annotations

import json
from pathlib import Path

from cli_files import Conflict, apply, plan, read_bytes, safe_path
from cli_model import json_bytes

SPRINT = Path('.asdg/sprint.json')
INACTIVE = {'status': 'inactive', 'sprint_id': None, 'objective': None,
            'scope': [], 'acceptance_criteria': []}
NO_SPRINT = 'No active ASDG sprint is defined.'


def relative_path(root: Path, value: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip() or '\\' in value:
        raise Conflict('A non-empty repository-relative path is required.')
    path = Path(value)
    if path.is_absolute():
        try:
            path = path.relative_to(root)
        except ValueError as exc:
            raise Conflict('Path is outside this project.') from exc
    if not path.parts or '..' in path.parts or any(c in value for c in '*?[]\n\r'):
        raise Conflict('Scope uses exact files or directories ending in /; traversal and globs are forbidden.')
    if any(part in ('.asdg', '.codex', '.git', '.agents', '.claude', 'AGENTS.md') for part in path.parts):
        raise Conflict('Governance and agent policy paths cannot be implementation scope.')
    safe_path(root, path)
    return path.as_posix()


def validate(root: Path, value: object) -> dict:
    if not isinstance(value, dict) or set(value) != set(INACTIVE):
        raise Conflict('Invalid .asdg/sprint.json fields.')
    if value['status'] == 'inactive':
        if value != INACTIVE:
            raise Conflict('Inactive sprint must have null identity/objective and empty scope/criteria.')
        return value
    if value['status'] != 'active':
        raise Conflict('Sprint status must be active or inactive.')
    for field in ('sprint_id', 'objective'):
        if not isinstance(value[field], str) or not value[field].strip() or '\n' in value[field]:
            raise Conflict(f'Active sprint requires a non-empty {field}.')
    for field in ('scope', 'acceptance_criteria'):
        if not isinstance(value[field], list) or not value[field] or any(
                not isinstance(item, str) or not item.strip() for item in value[field]):
            raise Conflict(f'Active sprint requires a non-empty {field} list.')
    for item in value['scope']:
        normalized = relative_path(root, item) + ('/' if item.endswith('/') else '')
        if normalized != item:
            raise Conflict('Scope paths must be normalized and repository-relative.')
    return value


def read_state(root: Path) -> dict:
    raw = read_bytes(safe_path(root, SPRINT))
    if raw is None:
        raise Conflict(NO_SPRINT)
    return validate(root, json.loads(raw))


def check_implementation(root: Path, paths: list[str], repo: Path | None = None,
                         guidance: bool = False) -> tuple[bool, str]:
    try:
        from cli_model import REPO
        from cli_status import project_status
        status = project_status(root, repo or REPO, paths)
        permission = status['implementation']
        reason = permission['reason']
        if guidance and permission['allowed'] is not True:
            reason += '\n\nRecommended next action:\n' + status['recommendation']['action']
        return permission['allowed'] is True, reason
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return False, str(exc)


def start(root: Path, sprint_id: str, objective: str, scope: list[str], criteria: list[str]) -> dict:
    if read_state(root)['status'] == 'active':
        raise Conflict('A sprint is already active. Stop it before starting another.')
    value = validate(root, {'status': 'active', 'sprint_id': sprint_id,
                           'objective': objective, 'scope': scope, 'acceptance_criteria': criteria})
    apply([change for change in [plan(root, SPRINT, json_bytes(value), replace=True)] if change])
    return value


def stop(root: Path) -> dict:
    read_state(root)
    apply([change for change in [plan(root, SPRINT, json_bytes(INACTIVE), replace=True)] if change])
    return dict(INACTIVE)
