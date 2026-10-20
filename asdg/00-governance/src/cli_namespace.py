"""Explicit, bounded legacy namespace migration; never initialization or approval.

Legacy spellings in this module and its fixtures are intentional migration input.
No command installs launchers, changes trust, starts a sprint or touches app code.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat

from cli_files import Conflict, atomic_replace, read_bytes, safe_path
from cli_model import catalogue, json_bytes, now, sha, PERSPECTIVES
from documentation import review_record

LEGACY_STATE, STATE = Path('.asdlc'), Path('.asdg')
LEGACY_DOCS, DOCS = Path('docs/asdlc'), Path('docs/asdg')
RECEIPT = DOCS / '00-governance/logs/namespace-migration.json'
LEGACY_CATALOG = Path(__file__).resolve().parents[1] / 'types/migrations/legacy-catalog-v0.2.json'


def rename_text(text: str) -> str:
    """Project-owned active namespace substitution; historical records are excluded."""
    text = text.replace('elustondo-asdlc', 'asdg')
    text = re.sub('asdlc', lambda m: 'ASDG' if m[0].isupper() else 'asdg', text, flags=re.I)
    return text.replace('02-intent', '02-purpose').replace('elicit-intent', 'elicit-purpose')


def rename_path(path: str | Path) -> Path:
    return Path(rename_text(Path(path).as_posix()))


def consumer_path(path: Path) -> Path:
    dest = rename_path(path)
    parts = dest.parts
    if (len(parts) >= 4 and parts[:2] == ('docs', 'asdg')
            and (re.match(r'^\d{2}-', parts[3]) or parts[3] in ('advice', 'baselines'))):
        return Path(*parts[:3], 'current', *parts[3:])
    return dest


def history(path: Path) -> bool:
    """Bounded immutable evidence areas, not active definitions or source examples."""
    return (any(x in path.parts for x in ('build', 'baselines', 'sessions', 'diagnostics', 'backups'))
            or ('advice' in path.parts and path.name != 'README.md')
            or ('logs' in path.parts and path.name != 'README.md')
            or path.as_posix().startswith('docs/reviews/')
            or (path.as_posix().startswith('docs/status/')
                and path.name not in ('README.md', 'lifecycle-baseline.md'))
            or '_NEW.' in path.name or path.name == 'document-reviews.json'
            or path.name.startswith('installation-') or path.suffix == '.patch'
            or path.name in ('CODEX-SDK-PILOT.md', 'narration-review.md',
                             'baseline-review.md', 'baseline-checkpoint-plan-r01.md',
                             'baseline-validation-r01.md')
            or (path.suffix == '.md' and ('verification' in path.name
                                         or 'correction-report' in path.name)))


def require_current_namespace(root: Path) -> None:
    if safe_path(root, LEGACY_STATE).exists() or safe_path(root, LEGACY_DOCS).exists():
        raise Conflict('Legacy namespace exists; use asdg migrate-namespace, never reinitialize it.')


def provider_files(root: Path) -> list[Path]:
    files = []
    for folder, dirs, names in os.walk(root):
        dirs[:] = [n for n in dirs if n not in ('.git', '.venv', '__pycache__', 'node_modules', 'build')]
        for name in names:
            p = Path(folder) / name
            if p.is_symlink():
                raise Conflict(f'Namespace migration refuses symlink: {p}')
            if p.is_file() and name != '.DS_Store':
                files.append(p.relative_to(root))
    return sorted(files)


def provider_relocations(root: Path) -> list[tuple[Path, Path]]:
    """Move the colliding launcher first, then names at their original depth."""
    if (root / 'asdg').is_dir():
        if (root / 'asdlc').exists():
            raise Conflict('Both provider namespace trees exist; reconcile before migration.')
        return []
    if not (root / 'asdg').is_file() or not (root / 'asdlc').is_dir():
        raise Conflict('Expected the legacy provider tree and root source launcher.')
    if (root / 'bin/asdg').exists():
        raise Conflict('Root and bin/asdg launchers conflict.')
    moves = [(Path('asdg'), Path('bin/asdg'))]
    entries = sorted((p for p in root.rglob('*') if '.git' not in p.parts
                      and 'build' not in p.parts and '__pycache__' not in p.parts),
                     key=lambda p: len(p.parts), reverse=True)
    for p in entries:
        rel = p.relative_to(root)
        if rel == Path('asdlc'):
            continue
        if rel.parts[0] in ('.venv', 'node_modules'):
            continue
        new_name = rename_path(rel.name).name
        if new_name != p.name:
            dest = rel.with_name(new_name)
            if (root / dest).exists():
                raise Conflict(f'Namespace destination exists: {dest}')
            moves.append((rel, dest))
    # The root directory must move after its children and the colliding launcher.
    moves = [m for m in moves if m[0] != Path('asdlc')]
    moves.append((Path('asdlc'), Path('asdg')))
    return moves


def relocate_provider(root: Path) -> dict:
    moves = provider_relocations(root)
    moved = []
    try:
        for old, new in moves:
            (root / new).parent.mkdir(parents=True, exist_ok=True)
            os.rename(root / old, root / new)
            moved.append((old, new))
    except BaseException:
        for old, new in reversed(moved):
            os.rename(root / new, root / old)
        raise
    return {'operation': 'provider-namespace-relocation',
            'moves': [[str(a), str(b)] for a, b in moves]}


def _references(value):
    if isinstance(value, str):
        if value.startswith('docs/asdlc/'):
            return str(consumer_path(Path(value))) + ('/' if value.endswith('/') else '')
        return value.replace('docs/asdlc', 'docs/asdg').replace('.asdlc/', '.asdg/').replace('02-intent', '02-purpose')
    if isinstance(value, list):
        return [_references(x) for x in value]
    if isinstance(value, dict):
        return {_references(k): _references(v) for k, v in value.items()}
    return value


def migrate_project(root: Path, repo: Path, *, apply: bool = False,
                    legacy_catalog: bytes | None = None) -> dict:
    """Preserve one authority and exact history; refuse conflicts before any write."""
    root, repo = root.resolve(strict=True), repo.resolve(strict=True)
    if root == repo or root.is_relative_to(repo) or repo.is_relative_to(root):
        raise Conflict('Consumer migration requires a separate project root.')
    old_state, new_state = safe_path(root, LEGACY_STATE), safe_path(root, STATE)
    old_docs, new_docs = safe_path(root, LEGACY_DOCS), safe_path(root, DOCS)
    if old_state.exists() and new_state.exists() or old_docs.exists() and new_docs.exists():
        raise Conflict('Conflicting old/new state or documentation trees; nothing changed.')
    if new_state.exists():
        if old_state.exists() or old_docs.exists() or not safe_path(root, RECEIPT).is_file():
            raise Conflict('Unverified partial migration; reconcile it before proceeding.')
        binding = json.loads(safe_path(root, STATE / 'project.json').read_bytes())
        _, digest = catalogue(repo)
        if binding.get('provider') != 'elustondo.ai/asdg' or binding.get('catalog_sha256') != digest:
            raise Conflict('Migrated binding does not match the selected provider.')
        return {'operation': 'migrate-namespace', 'status': 'ALREADY_MIGRATED', 'changed': []}
    if not old_state.is_dir() or not old_docs.is_dir():
        raise Conflict('Legacy state and documentation must both exist; migration never initializes.')
    originals = {}
    for base in (LEGACY_STATE, LEGACY_DOCS):
        for p in (root / base).rglob('*'):
            if p.is_symlink():
                raise Conflict(f'Refusing linked migration source: {p}')
            if p.is_file():
                originals[p.relative_to(root)] = (p.read_bytes(), stat.S_IMODE(p.stat().st_mode))
    for p in (Path('AGENTS.md'), Path('.codex/hooks.json')):
        source = safe_path(root, p)
        if not source.is_file():
            raise Conflict(f'Missing governed project integration: {p}')
        originals[p] = (source.read_bytes(), stat.S_IMODE(source.stat().st_mode))
    binding = json.loads(originals[LEGACY_STATE / 'project.json'][0])
    raw_catalog = legacy_catalog if legacy_catalog is not None else LEGACY_CATALOG.read_bytes()
    legacy = json.loads(raw_catalog)
    agents, digest = catalogue(repo)
    expected = json.loads(rename_text(raw_catalog.decode('utf-8')))
    expected['agents'][2]['title'] = 'Purpose Agent'
    if (binding.get('provider') != 'elustondo.ai/asdlc'
            or binding.get('schema_version') != 1
            or binding.get('catalog_sha256') != sha(raw_catalog)
            or expected.get('agents') != agents
            or binding.get('stages') != [Path(a['folder']).name for a in legacy['agents']]):
        raise Conflict('Legacy binding/catalogue is not the reviewed identity-only migration baseline.')
    if binding.get('artifacts_root') != str(LEGACY_DOCS):
        raise Conflict('Unexpected legacy artifact root.')
    for stage in binding['stages']:
        folder = safe_path(root, LEGACY_DOCS / stage)
        for view in PERSPECTIVES.values():
            target = safe_path(root, LEGACY_DOCS / stage / view)
            if target.exists() and not target.is_dir():
                raise Conflict(f'Conflicting perspective destination: {target}')
        for child in folder.iterdir():
            if child.is_dir() and (re.match(r'^\d{2}-', child.name) or child.name in ('advice', 'baselines')):
                if (folder / 'current' / child.name).exists():
                    raise Conflict(f'Conflicting current evidence destination: {child.name}')
    updates, events = {}, []
    stamp = now()
    for path, (data, mode) in originals.items():
        dest = consumer_path(path)
        after = data
        if path == LEGACY_STATE / 'project.json':
            current = dict(binding, provider='elustondo.ai/asdg', artifacts_root=str(DOCS),
                           stages=[Path(a['folder']).name for a in agents], catalog_sha256=digest)
            after = json_bytes(current)
        elif path in (LEGACY_STATE / 'sprint.json', LEGACY_STATE / 'lifecycle.json'):
            old = json.loads(data)
            current = _references(old)
            if current != old:
                after = json_bytes(current)
        elif path == Path('.codex/hooks.json'):
            after = rename_text(data.decode('utf-8')).encode('utf-8')
        elif not history(path) and path.name.endswith('.md') and path.name != 'speaker-notes.md':
            text = rename_text(data.decode('utf-8'))
            if path == Path('AGENTS.md'):
                text = re.sub(r'^(?:AI-MODIFIED|PME-APPROVED) - [^\n]*\n*', '', text)
            if path.name == 'README.md' and len(path.parts) == 4:
                text = re.sub(r'\]\(((?:\d{2}-[^/)]+|advice)/[^)]+)\)', r'](current/\1)', text)
                text += ('\n## Perspectives\n\n'
                         '- [Intended](intended/): desired outcomes, constraints and accepted targets.\n'
                         '- [Current](current/): substantiated evidence and its limitations.\n'
                         '- [Planned](planned/): selected work and links to the integrated Stage 07 plan.\n')
            after = text.encode('utf-8')
        if after != data:
            updates[dest] = (after, mode)
            if path.suffix == '.md':
                events.append(review_record(str(dest), data, after, stamp, previous_path=str(path)))
    receipt = {'schema_version': 1, 'operation': 'migrate-namespace', 'recorded_at': stamp,
               'identity_map': {'ASDLC-NN': 'ASDG-NN', 'ASDLC-COORDINATOR': 'ASDG-COORDINATOR',
                                'asdlc_NN': 'asdg_NN', 'asdlc_coordinator': 'asdg_coordinator',
                                'asdlc/': 'asdg/', 'docs/asdlc/': 'docs/asdg/',
                                '.asdlc/': '.asdg/', '02-intent': '02-purpose'},
               'project_id': binding['project_id'], 'original_binding': binding,
               'original_integration': {str(p): b.decode('utf-8') for p, (b, _) in originals.items()
                                        if p in (Path('AGENTS.md'), Path('.codex/hooks.json'))},
               'original_state': {str(p): json.loads(b) for p, (b, _) in originals.items()
                                  if p in (LEGACY_STATE / 'sprint.json', LEGACY_STATE / 'lifecycle.json')},
               'files': [{'before_path': str(p), 'after_path': str(consumer_path(p)),
                          'before_sha256': sha(b), 'after_sha256': sha(updates.get(consumer_path(p), (b, m))[0]),
                          'mode': m} for p, (b, m) in originals.items()],
               'review_events': events, 'human_approval': None,
               'trust': 'Not modified or inferred; renamed commands require native review.'}
    if safe_path(root, RECEIPT).exists():
        raise Conflict('Migration receipt already exists without a completed state migration.')
    if not apply:
        return {'operation': 'migrate-namespace', 'status': 'DRY_RUN', 'receipt': receipt,
                'writes': [str(p) for p in updates], 'moves': [[str(LEGACY_STATE), str(STATE)],
                            [str(LEGACY_DOCS), str(DOCS)], ['02-intent', '02-purpose']]}
    moves, written, made_dirs = [], [], []
    receipt_created = False
    try:
        for p, (data, mode) in originals.items():
            if read_bytes(root / p) != data or stat.S_IMODE((root / p).stat().st_mode) != mode:
                raise Conflict(f'Migration source changed since inspection: {p}')
        for old, new in ((LEGACY_STATE, STATE), (LEGACY_DOCS, DOCS),
                         (DOCS / '02-intent', DOCS / '02-purpose')):
            if (root / old).exists():
                os.rename(root / old, root / new)
                moves.append((old, new))
        for stage in agents:
            folder = DOCS / Path(stage['folder']).name
            for view in PERSPECTIVES.values():
                target = safe_path(root, folder / view)
                if not target.exists():
                    target.mkdir()
                    made_dirs.append(target)
            for child in list((root / folder).iterdir()):
                if child.is_dir() and (re.match(r'^\d{2}-', child.name) or child.name in ('advice', 'baselines')):
                    dest = child.parent / 'current' / child.name
                    if dest.exists():
                        raise Conflict(f'Conflicting current evidence destination: {dest}')
                    os.rename(child, dest)
                    moves.append((child.relative_to(root), dest.relative_to(root)))
        for path, (after, mode) in updates.items():
            atomic_replace(safe_path(root, path), after, mode)
            written.append(path)
        target = safe_path(root, RECEIPT)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            receipt_created = True
            stream.write(json_bytes(receipt))
    except BaseException:
        if receipt_created:
            target.unlink()
        for path in reversed(written):
            original = next((b, m) for p, (b, m) in originals.items() if consumer_path(p) == path)
            atomic_replace(root / path, *original)
        for old, new in reversed(moves):
            if old in (LEGACY_DOCS, DOCS / '02-intent'):
                for directory in reversed(made_dirs):
                    directory.rmdir()
                made_dirs = []
            os.rename(root / new, root / old)
        raise
    return {'operation': 'migrate-namespace', 'status': 'MIGRATED',
            'project_id': binding['project_id'], 'receipt': str(RECEIPT),
            'sprint_preserved': True, 'trust_changed': False}
