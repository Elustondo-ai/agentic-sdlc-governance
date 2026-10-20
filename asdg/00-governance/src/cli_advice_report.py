"""Bounded advisory report writes, owned by deterministic Python, never the LLM."""
from __future__ import annotations

import os
import json
import tempfile
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cli_advice import FIELDS, validate_advice
from cli_files import Conflict, safe_path
from documentation import nonblank_source_lines, review_record
from cli_model import REPO, catalogue
from cli_project import binding


def advice_destination(root: Path, repo: Path = REPO) -> Path:
    """Resolve the planning capability through the catalogue and project binding."""
    if not root.is_absolute() or root.is_symlink() or root != root.resolve(strict=True):
        raise Conflict('Advice requires the canonical absolute project root.')
    agents, digest = catalogue(repo)
    project = binding(root, digest)
    planning = [a for a in agents if a.get('skill_name') == 'asdg-prepare-plan']
    if project is None or len(planning) != 1:
        raise Conflict('Canonical planning capability or project binding is missing.')
    slug = Path(planning[0]['folder']).name
    if slug not in project.get('stages', []):
        raise Conflict('Planning folder is not declared by the project binding.')
    relative = Path(project['artifacts_root']) / slug
    folder = safe_path(root, relative)
    if not folder.is_dir() or not safe_path(root, relative / 'README.md').is_file():
        raise Conflict('Canonical project planning folder is missing; no report saved.')
    return safe_path(root, relative / 'current' / 'advice')


def _wrapped(value: str, prefix: str = '') -> list[str]:
    return textwrap.wrap(' '.join(value.split()), width=100, initial_indent=prefix,
                         subsequent_indent='  ' if prefix else '',
                         break_long_words=False, break_on_hyphens=False) or [prefix + 'None recorded.']


def render_report(root: Path, status: dict, advice: dict, saved_at: str) -> str:
    if advice.get('status') != 'available':
        raise Conflict('Coordinator advice is unavailable; no report saved.')
    validate_advice(json.dumps({k: advice[k] for k in FIELDS}))
    runtime = advice.get('runtime')
    if not isinstance(runtime, dict):
        raise Conflict('Observed coordinator runtime information is missing.')
    def clean(value):
        return ' '.join(str(value).split())
    release = status['release_status'] + (f" ({status['release_id']})" if status['release_id'] else '')
    sprint = status['sprint_status'] + (f" ({status['sprint_id']})" if status['sprint_id'] else '')
    lines = ['# ASDG coordinator advice', '',
             f"This advice concerns {clean(status['project_name'])}, based on the evaluation on {clean(status['evaluated_at'][:10])}.", '',
             f"Recorded project: {clean(status['project_status'])}; release: {clean(release)}; sprint: {clean(sprint)}.",
             f"Implementation permission: {clean(status['implementation_permission'])}.", '']
    lines += _wrapped('This recommendation is proposed work, not an approved plan or delivery commitment.')
    lines += ['', '## Recommendation', ''] + _wrapped(advice['action'])
    lines += [''] + _wrapped(advice['reason'], 'Reason: ')
    for heading, items in (
        ('Supporting evidence', advice['evidence']),
        ('Uncertainties and essential questions',
         ['Uncertainty: ' + x for x in advice['uncertainties']] +
         ['Question: ' + x for x in advice['questions']]),
        ('Approval and routing requirements', advice['requirements']),
    ):
        lines += ['', f'## {heading}', '']
        for item in items or ['None recorded by the coordinator.']:
            lines += _wrapped(item, '- ')
    document = '\n'.join(lines) + '\n'
    if nonblank_source_lines(document) > 50:
        raise Conflict(f'Advisory report exceeds 50 nonblank source lines ({nonblank_source_lines(document)}); no report saved.')
    if 'PME-APPROVED' in document:
        raise Conflict('Approval markers are forbidden in advisory reports.')
    return document


def save_advice(root: Path, status: dict, advice: dict, repo: Path = REPO) -> Path:
    destination = advice_destination(root, repo)
    instant = datetime.now(timezone.utc)
    saved_at = instant.isoformat(timespec='seconds').replace('+00:00', 'Z')
    document = render_report(root, status, advice, saved_at)
    relative = destination.relative_to(root)
    created_directory = not destination.exists()
    destination.mkdir(exist_ok=True)
    try:
        for _ in range(3):
            name = f"status-{instant.strftime('%Y%m%dT%H%M%S%fZ')}-{uuid4().hex[:12]}.md"
            target = safe_path(root, relative / name)
            receipt = safe_path(root, relative / Path(name).with_suffix('.json'))
            if target.exists() or receipt.exists():
                continue
            metadata = {'schema_version': 1,
                        'document_review': review_record((relative / name).as_posix(), None,
                                                         document.encode('utf-8'), saved_at),
                        'status': status, 'advice': advice}
            temporary, published = [], []
            try:
                # Stage complete bytes, then publish the receipt before its document.
                for final, content in ((receipt, json.dumps(metadata, indent=2) + '\n'),
                                       (target, document)):
                    fd, staging = tempfile.mkstemp(prefix='.asdg-advice-', dir=destination)
                    temporary.append(Path(staging))
                    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                        stream.write(content)
                        stream.flush()
                        os.fsync(stream.fileno())
                for staging, final in zip(temporary, (receipt, target)):
                    safe_path(root, final.relative_to(root))
                    os.link(staging, final, follow_symlinks=False)
                    published.append(final)
                return target
            except FileExistsError:
                for final in reversed(published):
                    final.unlink()
            except BaseException:
                for final in reversed(published):
                    final.unlink()
                raise
            finally:
                for staging in temporary:
                    staging.unlink(missing_ok=True)
        raise Conflict('Could not create a unique advisory report; no report saved.')
    finally:
        if created_directory:
            try:
                destination.rmdir()
            except OSError:
                pass
