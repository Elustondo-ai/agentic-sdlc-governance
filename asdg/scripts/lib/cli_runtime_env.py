"""Bounded runtime environment, extracted unchanged from the source baseline runner."""
from __future__ import annotations
import json
import os
from pathlib import Path
from cli_files import Conflict

ENV_NAMES = ('PATH', 'HOME', 'USER', 'LOGNAME', 'TMPDIR', 'TMP', 'TEMP',
             'LANG', 'LC_ALL', 'LC_CTYPE', 'SystemRoot', 'WINDIR',
             'SSL_CERT_FILE', 'CODEX_CA_CERTIFICATE')


def subprocess_environment(parent: dict | None = None) -> dict[str, str]:
    """Only execution/location/locale/public-CA settings; auth uses persisted login.

    Env-only API keys/tokens are intentionally unsupported rather than forwarding
    arbitrary provider credentials to model-controlled tools.
    """
    parent = os.environ if parent is None else parent
    values = {name: parent[name] for name in ENV_NAMES if parent.get(name)}
    values.setdefault('PATH', os.defpath)
    values.setdefault('HOME', str(Path.home()))
    values['PYTHONDONTWRITEBYTECODE'] = '1'
    if parent.get('CODEX_HOME'):
        path = Path(parent['CODEX_HOME'])
        if not path.is_absolute() or not path.is_dir():
            raise Conflict('Configured Codex state directory is unavailable.')
        values['CODEX_HOME'] = str(path.resolve())
    return values


def shell_environment_policy() -> str:
    # Replace the whole table: user-config set entries cannot reintroduce secrets.
    values = subprocess_environment()
    values.pop('CODEX_HOME', None)  # The broker's state location is unnecessary to tools.
    settings = '{' + ','.join(json.dumps(k) + '=' + json.dumps(v) for k, v in values.items()) + '}'
    return ('shell_environment_policy={inherit="none",ignore_default_excludes=false,'
            'set=' + settings + ',include_only=' + json.dumps(list(values)) + ',exclude=[]}')

