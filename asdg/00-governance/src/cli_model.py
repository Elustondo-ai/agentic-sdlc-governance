"""Read the existing ASDG catalogue; never invent lifecycle folder names."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from cli_files import Conflict, safe_path

PROVIDER = 'elustondo.ai/asdg'
COMMAND = 'asdg'
SHORT_COMMAND = 'asdg'
VERSION = '0.1.4'
REPO = Path(__file__).resolve().parents[3]
CATALOG = Path('asdg/00-governance/types/agent-catalog.json')
ARTIFACTS = Path('docs/asdg')
BINDING = Path('.asdg/project.json')
PERSPECTIVES = {'Intended': 'intended', 'Actual': 'current', 'Planned': 'planned'}


def require_python() -> bool:
    """One minimum-version policy shared by the CLI and installer."""
    if sys.version_info < (3, 9):
        print('Python 3.9 or newer is required.', file=sys.stderr)
        return False
    return True


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def catalogue(repo: Path = REPO) -> tuple[list[dict], str]:
    raw = safe_path(repo, CATALOG).read_bytes()
    value = json.loads(raw)
    agents = value.get('agents')
    if value.get('version') != '0.2' or not isinstance(agents, list) or len(agents) != 13:
        raise Conflict('Unsupported or incomplete ASDG agent catalogue; expected v0.2, 13 roles.')
    if sorted(a.get('stage', -1) for a in agents) != list(range(13)):
        raise Conflict('Catalogue must contain governance 00 and the twelve existing stages.')
    names, folders = set(), set()
    for agent in agents:
        stage = agent['stage']
        expected_native = 'asdg_coordinator' if stage == 0 else f'asdg_{stage:02d}'
        expected_role = 'ASDG-COORDINATOR' if stage == 0 else f'ASDG-{stage:02d}'
        if agent.get('native_name') != expected_native or agent.get('role_id') != expected_role:
            raise Conflict('Catalogue identity does not use the canonical ASDG namespace.')
        folder = Path(agent.get('folder', ''))
        if (len(folder.parts) != 2 or folder.parts[0] != 'asdg'
                or not re.fullmatch(rf'{stage:02d}-[a-z0-9]+(?:-[a-z0-9]+)*', folder.name)):
            raise Conflict('Invalid catalogue stage path')
        if (folder.as_posix() in folders or agent.get('native_name') in names
                or agent.get('entry') != (folder / 'AGENTS.md').as_posix()):
            raise Conflict('Duplicate catalogue identity or invalid entry point')
        if not isinstance(agent.get('title'), str) or '\n' in agent['title']:
            raise Conflict('Invalid role title')
        names.add(agent['native_name'])
        folders.add(folder.as_posix())
    return sorted(agents, key=lambda a: a['stage']), sha(raw)


def git_value(root: Path, *arguments: str) -> str | None:
    try:
        result = subprocess.run(['git', '-C', str(root), *arguments],
                                capture_output=True, text=True, timeout=10, check=False)
    except subprocess.TimeoutExpired as exc:
        raise Conflict('Git inspection timed out; no initialization was attempted.') from exc
    except FileNotFoundError as exc:
        raise Conflict('Git must be installed; this tool never runs git init for you.') from exc
    return result.stdout.strip() if result.returncode == 0 else None


def project_root(cwd: Path | None = None, repo: Path = REPO) -> Path:
    cwd = (cwd or Path.cwd()).resolve(strict=True)
    detected = git_value(cwd, 'rev-parse', '--show-toplevel')
    if not detected:
        raise Conflict('Run this command inside an existing Git working repository.')
    root = Path(detected).resolve(strict=True)
    repo = repo.resolve(strict=True)
    if root == repo or root.is_relative_to(repo) or repo.is_relative_to(root):
        raise Conflict('Initialize a separate application repository, not the ASDG provider checkout.')
    return root


def agent_by_name(name: str, repo: Path = REPO) -> dict:
    agents, _ = catalogue(repo)
    alias = {'architect': 'asdg_05', 'coordinator': 'asdg_coordinator'}
    name = alias.get(name, name)
    for agent in agents:
        if name in (agent['native_name'], agent['role_id'], f"{agent['stage']:02d}"):
            return agent
    raise Conflict(f'Unknown agent: {name}; run {SHORT_COMMAND} agent list.')
