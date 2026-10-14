"""Validate folder-based ASDLC agent packages without executing agents or writing files."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from agent_config import loads

REQUIRED_DIRS = ('docs', 'types', 'src', 'tests', 'skills')
REQUIRED_FILES = ('README.md', 'AGENTS.md', 'types/contract.md', 'tests/acceptance.md')


def skill_fields(front: str) -> dict[str, str]:
    """Validate the flat string-only role-skill YAML subset without dependencies."""
    fields = {}
    for line in front.splitlines():
        if not line.strip():
            continue
        key, value = line.split(': ', 1)
        if key not in {'name', 'description'} or key in fields:
            raise ValueError('Unsupported or duplicate role-skill metadata field')
        if value.startswith('"'):
            value = json.loads(value)
        elif ': ' in value or ' #' in value or value[:1] in "'[{!&*":
            raise ValueError('Role-skill YAML values with reserved syntax must be double quoted')
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Role-skill metadata must contain nonempty strings')
        fields[key] = value
    return fields


def inside(root: Path, value: str) -> Path:
    """Resolve repository-relative references, refusing absolute/escaping paths."""
    relative = Path(value)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'Unsafe repository path: {value}')
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'Path escapes repository: {value}')
    return path


def validate(root: Path) -> list[str]:
    """Return all detectable structural defects, not a behavioral certification."""
    root = root.resolve(strict=True)
    issues: list[str] = []
    catalogue = root / 'asdlc/00-governance/types/agent-catalog.json'
    try:
        data = json.loads(catalogue.read_text(encoding='utf-8'))
        rows = data['agents']
        if not isinstance(rows, list):
            raise ValueError('agents must be a list')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f'Invalid catalogue: {exc}']
    if data.get('mode') != 'read-only-evaluation':
        issues.append('Catalogue mode must remain read-only-evaluation')
    expected_names = {'asdlc_coordinator'} | {f'asdlc_{i:02d}' for i in range(1, 13)}
    if len(rows) != 13:
        issues.append('Expected exactly 13 catalogue entries')
    names, stages, folders = [], [], []
    markdown: set[Path] = set()
    for relative in ('AGENTS.md', 'asdlc/README.md', '.codex/README.md',
                     'asdlc/00-governance/docs/runtime-contract.md',
                     'asdlc/00-governance/types/interaction-contract.md'):
        path = root / relative
        if not path.is_file():
            issues.append(f'Missing shared file: {relative}')
        else:
            markdown.add(path)
    baseline = root / 'docs/status/lifecycle-baseline.md'
    if not baseline.is_file():
        issues.append('Missing authoritative lifecycle baseline')
    else:
        found = re.findall(r'^\| (\d{2}) \|', baseline.read_text(encoding='utf-8'), re.M)
        if found != [f'{i:02d}' for i in range(1, 13)]:
            issues.append('Lifecycle baseline must retain the twelve ordered stages')
    for row in rows:
        try:
            stage, name, folder = row['stage'], row['native_name'], row['folder']
            names.append(name); stages.append(stage); folders.append(folder)
            home = inside(root, folder)
            entry = inside(root, row['entry'])
            skill = inside(root, row['skill'])
            adapter = inside(root, row['adapter'])
            if not isinstance(stage, int) or isinstance(stage, bool) or stage not in range(13):
                raise ValueError('stage must be an integer from 0 through 12')
            expected_name = 'asdlc_coordinator' if stage == 0 else f'asdlc_{stage:02d}'
            if name != expected_name:
                issues.append(f'Native identity changed: {name}')
            if home.parent != root / 'asdlc' or not home.name.startswith(f'{stage:02d}-'):
                issues.append(f'Incorrect numbered home: {folder}')
            if entry != home / 'AGENTS.md':
                issues.append(f'Entry is not package AGENTS.md: {name}')
            if skill.name != 'SKILL.md' or not skill.is_relative_to(home / 'skills'):
                issues.append(f'Skill outside owner package: {name}')
            if adapter != root / '.codex/agents' / f'{name}.toml':
                issues.append(f'Incorrect native adapter path: {name}')
            for directory in REQUIRED_DIRS:
                if not (home / directory).is_dir():
                    issues.append(f'Missing directory: {folder}/{directory}')
            for filename in REQUIRED_FILES:
                if not (home / filename).is_file():
                    issues.append(f'Missing package file: {folder}/{filename}')
            if home.is_dir():
                markdown.update(home.rglob('*.md'))
            role_text = entry.read_text(encoding='utf-8')
            for phrase in (row['role_id'], name, '## Activation and maintenance',
                           '## Owned responsibility', '## Explicit exclusions',
                           '## Self-explanation', 'OUT_OF_SCOPE', 'READ_ONLY_EVALUATION'):
                if phrase not in role_text:
                    issues.append(f'Missing role contract element {phrase}: {name}')
            for link in re.findall(r'\]\(([^)]+)\)', role_text):
                target = (entry.parent / link.split('#')[0]).resolve()
                if not target.is_relative_to(root) or not target.exists():
                    issues.append(f'Broken role link: {name}: {link}')
            skill_text = skill.read_text(encoding='utf-8')
            if not skill_text.startswith('---\n'):
                issues.append(f'Missing YAML-first skill header: {name}')
            else:
                front, body = skill_text[4:].split('\n---\n', 1)
                fields = skill_fields(front)
                if fields.get('name') != row['skill_name'] or not fields.get('description'):
                    issues.append(f'Invalid skill discovery metadata: {name}')
                if not body.lstrip().startswith('AI-MODIFIED - '):
                    issues.append(f'Missing skill review marker: {name}')
            obj = loads(adapter.read_text(encoding='utf-8'))
            if obj.get('name') != name or not obj.get('description'):
                issues.append(f'Invalid adapter identity/description: {name}')
            if obj.get('sandbox_mode') != 'read-only':
                issues.append(f'Adapter is not read-only: {name}')
            instructions = obj.get('developer_instructions', '')
            if row['entry'] not in instructions or 'OUT_OF_SCOPE' not in instructions:
                issues.append(f'Adapter bootstrap incomplete: {name}')
            if 'asdlc/agents/' in instructions:
                issues.append(f'Adapter still loads flat role path: {name}')
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            issues.append(f'Invalid entry {row.get("native_name", "?") if isinstance(row, dict) else "?"}: {exc}')
    if set(names) != expected_names or len(set(names)) != len(names):
        issues.append('Native names must be thirteen distinct preserved identifiers')
    if sorted(stages, key=str) != sorted(range(13), key=str):
        issues.append('Stages must be exactly 00 through 12 without duplicates')
    if len(set(folders)) != len(folders):
        issues.append('Two agents share a canonical package')
    actual = {p.stem for p in (root / '.codex/agents').glob('*.toml')}
    if actual != expected_names:
        issues.append('Unexpected or missing native agent TOML files')
    flat = list((root / 'asdlc/agents').glob('[0-9][0-9]-*.md'))
    if flat:
        issues.append('Old flat role definitions still present')
    for path in sorted(markdown):
        text = path.read_text(encoding='utf-8')
        relative = path.relative_to(root)
        if len(text.splitlines()) > 50:
            issues.append(f'Markdown exceeds 50 physical lines: {relative}')
        if path.name != 'SKILL.md' and not text.startswith('AI-MODIFIED - '):
            issues.append(f'Missing first-line review marker: {relative}')
    return issues


def main(root: Path | None = None) -> int:
    root = root or Path(__file__).resolve().parents[3]
    issues = validate(root)
    if issues:
        print('\n'.join('FAIL: ' + issue for issue in issues))
        return 1
    print('PASS: 13 folder-based agent packages and read-only Codex adapters; local skills and links valid.')
    print('Structural validation only. Native invocation, role behavior and enforcement are not certified.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
