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
from cli_model import REPO, catalogue
from cli_project import binding


def advice_destination(root: Path, repo: Path = REPO) -> Path:
    """Resolve the planning capability through the catalogue and project binding."""
    if not root.is_absolute() or root.is_symlink() or root != root.resolve(strict=True):
        raise Conflict('Advice requires the canonical absolute project root.')
    agents, digest = catalogue(repo)
    project = binding(root, digest)
    planning = [a for a in agents if a.get('skill_name') == 'asdlc-prepare-plan']
    if project is None or len(planning) != 1:
        raise Conflict('Canonical planning capability or project binding is missing.')
    slug = Path(planning[0]['folder']).name
    if slug not in project.get('stages', []):
        raise Conflict('Planning folder is not declared by the project binding.')
    relative = Path(project['artifacts_root']) / slug
    folder = safe_path(root, relative)
    if not folder.is_dir() or not safe_path(root, relative / 'README.md').is_file():
        raise Conflict('Canonical project planning folder is missing; no report saved.')
    return safe_path(root, relative / 'advice')


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
    lines = [f'AI-MODIFIED - {saved_at}', '', '# ASDG coordinator advice', '',
             f"Project: {clean(status['project_name'])}", f'Project root: {clean(root)}',
             f"Evaluation time: {clean(status['evaluated_at'])}",
             f"Recorded project: {clean(status['project_status'])}; release: {clean(release)}; sprint: {clean(sprint)}.",
             f"Implementation permission: {clean(status['implementation_permission'])}.", '']
    lines += _wrapped('Advisory output only. This is not an approved plan, registered lifecycle evidence, '
                      'or authorization to execute work. No approval or handoff is recorded by this report.')
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
    lines += ['', '## Observed runtime', '',
              f"SDK {clean(runtime['sdk_version'])}; Codex {clean(runtime['cli_version'])}; provider {clean(runtime['model_provider'])}.",
              f"Configured model: {clean(runtime['model'] or 'unknown')} (thread configuration, not per-turn telemetry).",
              f"Thread: {clean(runtime['thread_id'])}; turn: {clean(runtime['turn_id'])}.",
              f"Sandbox: {clean(runtime['sandbox'])}; approvals: {clean(runtime['approval_mode'])}; ephemeral: {clean(runtime['ephemeral'])}."]
    document = '\n'.join(lines) + '\n'
    if len(lines) > 50:
        raise Conflict(f'Advisory report exceeds 50 readable lines ({len(lines)}); no report saved.')
    if 'PME-APPROVED' in document:
        raise Conflict('Approval markers are forbidden in advisory reports.')
    return document


def save_advice(root: Path, status: dict, advice: dict, repo: Path = REPO) -> Path:
    destination = advice_destination(root, repo)
    instant = datetime.now(timezone.utc)
    saved_at = instant.isoformat(timespec='seconds').replace('+00:00', 'Z')
    document = render_report(root, status, advice, saved_at)
    relative = destination.relative_to(root)
    created = not destination.exists()
    destination.mkdir(exist_ok=True)
    temporary = None
    try:
        # Stage a complete report, then link it exclusively: no partial final file
        # and no overwrite, including when another process wins a name collision.
        safe_path(root, relative)
        fd, temporary = tempfile.mkstemp(prefix='.asdg-advice-', dir=destination)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(document)
            stream.flush()
            os.fsync(stream.fileno())
        for _ in range(3):
            name = f"status-{instant.strftime('%Y%m%dT%H%M%S%fZ')}-{uuid4().hex[:12]}.md"
            target = safe_path(root, relative / name)
            try:
                os.link(temporary, target, follow_symlinks=False)
                return target
            except FileExistsError:
                continue
        raise Conflict('Could not create a unique advisory report; no report saved.')
    finally:
        if temporary is not None:
            Path(temporary).unlink()
        if created:
            try:
                destination.rmdir()
            except OSError:
                pass
