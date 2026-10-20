"""Shared Markdown source-line rule and hash-bound documentation review receipts.

Receipts record authorship/provenance, never infer human approval. Legacy visible
approval declarations are preserved against the old bytes, not transferred.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

MAX_NONBLANK_LINES = 50
PROVIDER_REVIEWS = Path('asdg/00-governance/types/document-reviews.json')
PROJECT_REVIEWS = Path('docs/asdg/00-governance/logs/document-reviews.json')


def nonblank_source_lines(text: str) -> int:
    """Count source lines containing a non-whitespace character, without rewriting."""
    return sum(bool(line.strip()) for line in text.splitlines())


def check_length(text: str) -> None:
    count = nonblank_source_lines(text)
    if count > MAX_NONBLANK_LINES:
        raise ValueError(f'Documentation exceeds 50 nonblank source lines ({count}).')


def review_record(path: str, before: bytes | None, after: bytes, recorded_at: str,
                  **provenance) -> dict:
    """Bind modification and retained legacy declarations to their exact states."""
    record = {'path': path, 'sha256': hashlib.sha256(after).hexdigest(),
              'event': 'AI-MODIFIED', 'recorded_at': recorded_at,
              'human_approval': None, 'provenance': provenance}
    if before is not None:
        record['previous_state'] = {
            'sha256': hashlib.sha256(before).hexdigest(),
            'visible_review_markers': re.findall(
                r'^(?:# )?(?:AI-MODIFIED|PME-APPROVED) - [^\r\n]+',
                before.decode('utf-8'), re.M),
            'approval_binding': 'Legacy declarations only; no approval inferred or transferred.'}
    return record


def recorded_document(root: Path, path: Path) -> bool:
    """A current receipt is necessary for migrated marker-free package documents."""
    file = root / PROVIDER_REVIEWS
    if file.is_symlink() or not file.is_file():
        return False
    try:
        ledger = json.loads(file.read_text())
        if ledger['schema_version'] != 1 or not isinstance(ledger['events'], list):
            return False
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        relative = path.relative_to(root).as_posix()
        return any(e.get('path') == relative and e.get('sha256') == digest
                   and e.get('event') == 'AI-MODIFIED' and e.get('recorded_at')
                   and e.get('human_approval') is None for e in ledger['events'])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False
