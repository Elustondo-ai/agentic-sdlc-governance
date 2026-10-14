"""One implementation permission calculation shared by status, CLI and hooks."""
from __future__ import annotations

from pathlib import Path
from cli_sprint import NO_SPRINT, relative_path


def implementation_permission(root: Path, sprint: dict | None,
                              errors: list[str], paths: list[str] | None = None) -> dict:
    result = {'permission': 'BLOCKED', 'allowed': False, 'reason': '',
              'requested_paths': paths, 'scope': (sprint or {}).get('scope', [])}
    if errors:
        result['reason'] = 'ERROR: ' + errors[0]
    elif not sprint or sprint['status'] != 'active':
        result['reason'] = NO_SPRINT
    elif paths is None:
        result.update(permission='ALLOWED_WITHIN_SCOPE', allowed=None,
                      reason='Implementation is restricted to the active sprint scope.')
    elif not paths:
        result['reason'] = 'Specify every implementation target with --path.'
    else:
        try:
            for value in paths:
                path = relative_path(root, value)
                if not any(path == scope or (scope.endswith('/') and path.startswith(scope))
                           for scope in sprint['scope']):
                    result['reason'] = f'Requested path is outside active sprint scope: {path}'
                    return result
            result.update(permission='ALLOWED', allowed=True, reason='Implementation allowed.')
        except (OSError, ValueError, TypeError) as exc:
            result['reason'] = str(exc)
    return result
