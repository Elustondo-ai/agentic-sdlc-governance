#!/usr/bin/env python3
"""Validate the portable package, not native trust or semantic compliance."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
CORE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE / 'scripts/lib'))
from agent_config import loads
from cli_model import catalogue
from cli_status import lifecycle_rules
from documentation import nonblank_source_lines
from distribution_files import MANIFEST, package_files


def validate(core=CORE, integrity=False):
    issues = []
    root = core.parent
    try:
        selected = package_files(core)
        agents, _ = catalogue(root)
        lifecycle_rules(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ['Invalid catalogue/rules: ' + str(exc)]
    for row in agents:
        for field in ('entry', 'skill'):
            if not (root / row[field]).is_file():
                issues.append('Missing role source: ' + row[field])
        adapter = core / 'templates' / row['adapter']
        try:
            obj = loads(adapter.read_text())
            if obj.get('name') != row['native_name'] or not obj.get('description'):
                issues.append('Invalid role adapter identity: ' + str(adapter))
            instructions = obj.get('developer_instructions', '')
            if row['entry'] not in instructions or 'OUT_OF_SCOPE' not in instructions or 'Do not modify files' not in instructions:
                issues.append('Incomplete role adapter boundary: ' + str(adapter))
            if 'sandbox_mode' in obj:
                issues.append('Obsolete standalone agent sandbox setting: ' + str(adapter))
        except (OSError, ValueError) as exc:
            issues.append('Invalid adapter: ' + str(exc))
    selected_set = set(selected)
    for path in selected:
        if path.suffix == '.py':
            try:
                ast.parse(path.read_text(), filename=str(path), feature_version=(3, 9))
            except SyntaxError as exc:
                issues.append('Python 3.9 syntax: ' + str(exc))
        if path.suffix != '.md':
            continue
        text = path.read_text()
        if nonblank_source_lines(text) > 50:
            issues.append('Over 50 nonblank lines: ' + str(path.relative_to(core)))
        if path.name == 'SKILL.md':
            if not re.match(r'\A---\nname: [a-z0-9-]+\ndescription: .+\n---\n', text):
                issues.append('Invalid skill front matter: ' + str(path.relative_to(core)))
        virtual = root / path.relative_to(core / 'templates') if path.is_relative_to(core / 'templates') else path
        for link in re.findall(r'\]\(([^)]+)\)', text):
            link = link.split('#')[0]
            if not link or '://' in link or link.startswith('mailto:'):
                continue
            target = (virtual.parent / link).resolve()
            if not target.is_relative_to(root):
                issues.append('Link escapes client: ' + str(path.relative_to(core)) + ': ' + link)
                continue
            template_target = core / 'templates' / target.relative_to(root)
            candidates = (target, template_target)
            if not any(candidate in selected_set or any(candidate in p.parents for p in selected)
                       for candidate in candidates):
                issues.append('Link missing from package: ' + str(path.relative_to(core)) + ': ' + link)
    if integrity:
        try:
            manifest = json.loads((core / 'metadata/MANIFEST.json').read_text())
            expected = manifest['files']
            actual = {p.relative_to(core).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in selected if p != core / MANIFEST}
            metadata = json.loads((core / 'metadata/distribution.json').read_text())
            if manifest.get('version') != metadata.get('version'):
                issues.append('Manifest version differs from distribution metadata.')
            for path in sorted(set(expected) | set(actual)):
                if expected.get(path) != actual.get(path):
                    issues.append('Package manifest differs: ' + path)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            issues.append('Unavailable/invalid delivery manifest: ' + str(exc))
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrity', action='store_true', help='also compare against delivered file hashes')
    args = parser.parse_args()
    issues = validate(integrity=args.integrity)
    if issues:
        print('\n'.join('FAIL: ' + item for item in issues))
        return 1
    print('PASS: portable package, thirteen roles, skill syntax, references and Python 3.9 syntax.')
    if args.integrity:
        print('PASS: delivered file hashes match metadata/MANIFEST.json.')
    print('Native invocation, hook trust, runtime enforcement and human approval are separate checks.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
