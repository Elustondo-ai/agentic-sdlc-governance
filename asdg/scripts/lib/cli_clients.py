"""Choose client integrations and render Claude skill adapters from the shared adapter templates."""
from __future__ import annotations

import json
import re
from pathlib import Path

from cli_files import Conflict, read_bytes, safe_path
from cli_model import json_bytes

CLIENTS = ('codex', 'claude')
CHOICES = {'codex': ('codex',), 'claude': ('claude',), 'both': ('codex', 'claude')}
INTEGRATIONS = Path('.asdg/integrations.json')
SKILL_TEMPLATES = Path('asdg/templates/.agents/skills')
CLAUDE_SKILLS = Path('.claude/skills')
# Any of these, in the project or a parent folder, makes Claude Code skip its native AGENTS.md read.
SUPPRESSORS = ('CLAUDE.md', '.claude/CLAUDE.md', 'CLAUDE.local.md')
BRIDGE_BEGIN, BRIDGE_END = '<!-- ASDG:BEGIN claude-bridge-v1 -->', '<!-- ASDG:END claude-bridge -->'


def read_integrations(root: Path) -> dict | None:
    """Return the recorded client selection, or None when none was ever recorded."""
    raw = read_bytes(safe_path(root, INTEGRATIONS))
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except ValueError as exc:
        raise Conflict(f'Invalid {INTEGRATIONS}: {exc}') from exc
    clients = value.get('clients') if isinstance(value, dict) else None
    if (not isinstance(value, dict) or set(value) != {'schema_version', 'clients'} or value['schema_version'] != 1
            or not isinstance(clients, dict) or not set(clients) <= set(CLIENTS)
            or not all(isinstance(entry, dict) and set(entry) == {'recorded_from'}
                       and isinstance(entry['recorded_from'], str) for entry in clients.values())):
        raise Conflict(f'Invalid {INTEGRATIONS}; repair it before setup or verification.')
    return value


def integrations_bytes(recorded: dict) -> bytes:
    return json_bytes({'schema_version': 1, 'clients': {name: recorded[name] for name in sorted(recorded)}})


def resolve_clients(root: Path, choice: str | None, installed: bool) -> tuple[dict, list[str], list[str]]:
    """Return the clients recorded after this run, the clients whose files this run plans, and notes.

    Selection is additive and never removes a client. Without a choice, repeat setup covers the
    recorded clients; a fresh or legacy installation with nothing recorded gets Codex, as before.
    """
    if choice is not None and choice not in CHOICES:
        raise Conflict(f'Unsupported client: {choice}')
    current = read_integrations(root)
    recorded = dict(current['clients']) if current else {}
    notes = []
    if current is None and installed:
        recorded['codex'] = {'recorded_from': 'legacy installation'}
        notes.append('Recorded the existing Codex integration from a legacy installation without client tracking.')
    if choice is None:
        if not recorded:
            recorded['codex'] = {'recorded_from': 'default'}
        return recorded, sorted(recorded), notes
    for client in CHOICES[choice]:
        recorded.setdefault(client, {'recorded_from': f'--client {choice}'})
    return recorded, list(CHOICES[choice]), notes


def skill_names(repo: Path) -> list[str]:
    """Public skills: shared adapter templates that contain a SKILL.md."""
    return sorted(path.parent.name for path in safe_path(repo, SKILL_TEMPLATES).glob('*/SKILL.md'))


def explicit_only(repo: Path, name: str) -> bool:
    """True when the Codex policy forbids implicit invocation; Claude then gets its own native control."""
    policy = read_bytes(safe_path(repo, SKILL_TEMPLATES / name / 'agents/openai.yaml')) or b''
    return re.search(rb'^\s+allow_implicit_invocation:\s*false\s*$', policy, re.MULTILINE) is not None


def claude_adapter(repo: Path, name: str) -> bytes:
    """Render a Claude adapter: the shared template's name, description and body, plus Claude's control."""
    text = read_bytes(safe_path(repo, SKILL_TEMPLATES / name / 'SKILL.md')).decode('utf-8')
    match = re.match(r'---\n(.*?)\n---\n', text, re.DOTALL)
    fields = dict(line.split(': ', 1) for line in match.group(1).splitlines() if ': ' in line) if match else {}
    if not match or set(fields) != {'name', 'description'} or fields['name'] != name:
        raise Conflict(f'Skill adapter template needs exactly name and description front matter: {name}')
    head = f"---\nname: {name}\ndescription: {fields['description']}\n"
    if explicit_only(repo, name):
        head += 'disable-model-invocation: true\n'
    return (head + '---\n' + text[match.end():]).encode('utf-8')


def claude_files(repo: Path) -> list[tuple[Path, bytes]]:
    return [(CLAUDE_SKILLS / name / 'SKILL.md', claude_adapter(repo, name)) for name in skill_names(repo)]


def suppressors(root: Path) -> list[str]:
    """Instruction files that would make Claude skip AGENTS.md, here or in any parent folder."""
    found = []
    for directory in (root, *root.resolve().parents):
        for name in SUPPRESSORS:
            path = directory / name
            if path.is_file() or path.is_symlink():
                found.append(name if directory == root else str(path))
    return found


def _imports_agents(text: str, line: str) -> bool:
    """True when the file already imports the root AGENTS.md outside code, so no second import is added."""
    prose = re.sub(r'```.*?```|~~~.*?~~~', '', text, flags=re.DOTALL)
    prose = re.sub(r'`[^`\n]*`', '', prose)
    forms = [line] + (['@./AGENTS.md'] if line == '@AGENTS.md' else [])
    pattern = r'(?<![\w/@])(?:' + '|'.join(re.escape(form) for form in forms) + r')(?!\.?[\w\-/])'
    return re.search(pattern, prose) is not None


def claude_bridge(root: Path) -> tuple[str, bytes] | None:
    """Return (path, new bytes) that keep Claude loading AGENTS.md, or None when nothing is needed."""
    if not suppressors(root):
        return None
    target = '.claude/CLAUDE.md' if not (root / 'CLAUDE.md').exists() and (root / '.claude/CLAUDE.md').exists() else 'CLAUDE.md'
    line = '@AGENTS.md' if target == 'CLAUDE.md' else '@../AGENTS.md'
    path = root / target
    if path.is_symlink():
        if path.resolve() == (root / 'AGENTS.md').resolve():
            return None
        raise Conflict(f'{target} is a symlink; add {line} to its target manually.')
    block = f'{BRIDGE_BEGIN}\n{line}\n{BRIDGE_END}\n'
    old = read_bytes(safe_path(root, target))
    if old is None:
        return target, block.encode()
    text = old.decode('utf-8')
    markers = (text.count(BRIDGE_BEGIN), text.count(BRIDGE_END))
    if markers == (1, 1) and text.startswith(block):
        return None
    if markers != (0, 0):
        raise Conflict(f'Edited, moved or duplicated ASDG Claude bridge in {target}; reconcile it manually.')
    if _imports_agents(text, line):
        return None
    return target, (block + '\n' + text).encode()


def claude_bridge_problems(root: Path) -> list[str]:
    try:
        change = claude_bridge(root)
    except Conflict as exc:
        return [str(exc)]
    if change is None:
        return []
    return [f"{change[0]}: Claude would skip AGENTS.md because of {', '.join(suppressors(root))}; "
            'run setup with --client claude to add the @AGENTS.md import']
