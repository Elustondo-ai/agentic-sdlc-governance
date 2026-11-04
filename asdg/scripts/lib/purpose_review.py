"""Hash-bound Purpose readiness and explicit User acceptance; no file writes."""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

from cli_files import Conflict, read_bytes, safe_path

PREFIX = Path('docs/asdg/02-purpose')
DOCUMENTS = ('01-purpose.md', '02-current-capabilities.md', '03-planned-improvements.md')
LEGACY_DOCUMENTS = ('01-purpose.md', 'current/02-current-capabilities.md',
                    'planned-release/03-planned-improvements.md')
CRITERIA = ('purpose', 'outcomes', 'boundaries', 'current_evidence', 'next_improvement',
            'acceptance_questions', 'visual', 'documentation')


def validate_reviews(reviews: list) -> None:
    """Validate history, actor separation and acceptance of an earlier ready bundle."""
    if not isinstance(reviews, list):
        raise Conflict('Purpose reviews must be an append-only list.')
    ready = []
    for event in reviews:
        if not isinstance(event, dict):
            raise Conflict('Invalid Purpose review event.')
        decision = event.get('decision')
        common = {'decision', 'actor', 'recorded_at', 'artifacts'}
        extra = {'criteria'} if decision == 'READY_FOR_ACCEPTANCE' else {'statement'}
        if decision not in ('READY_FOR_ACCEPTANCE', 'ACCEPTED') or set(event) != common | extra:
            raise Conflict('Unsupported Purpose review decision or fields.')
        if not isinstance(event['recorded_at'], str) or not event['recorded_at'].strip():
            raise Conflict('Purpose reviews require a recorded time.')
        hashes = event['artifacts']
        if not isinstance(hashes, dict) or not hashes:
            raise Conflict('Purpose reviews require exact artifact hashes.')
        layouts = (DOCUMENTS, LEGACY_DOCUMENTS)
        if not any({str(PREFIX / name) for name in (*layout, 'README.md')} <= hashes.keys()
                   for layout in layouts):
            raise Conflict('Purpose review omits a required document.')
        for name, digest in hashes.items():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or not path.is_relative_to(PREFIX):
                raise Conflict('Purpose review paths must stay inside the Purpose evidence folder.')
            if not isinstance(digest, str) or not re.fullmatch(r'[a-f0-9]{64}', digest):
                raise Conflict('Purpose reviews require SHA-256 hashes.')
        if not any(Path(name).is_relative_to(PREFIX / 'images') for name in hashes):
            raise Conflict('Purpose review omits the explanatory image.')
        if decision == 'READY_FOR_ACCEPTANCE':
            criteria = event['criteria']
            if (event['actor'] != 'ASDG-02' or not isinstance(criteria, dict)
                    or set(criteria) != set(CRITERIA)
                    or any(not isinstance(v, str) or not v.strip() for v in criteria.values())):
                raise Conflict('Agent readiness requires evidence for every Purpose criterion.')
            ready.append(hashes)
        elif (event['actor'] != 'User' or not isinstance(event['statement'], str)
              or not event['statement'].strip() or hashes not in ready):
            raise Conflict('Acceptance requires an explicit User statement and a matching prior agent review.')


def bundle_hashes(root: Path, files: list[str]) -> dict[str, str]:
    """Read the reviewed documents, navigation and their local image dependencies."""
    required = {str(PREFIX / name) for name in DOCUMENTS}
    if not required <= set(files):
        raise Conflict('Register all three Purpose concept documents before review.')
    names = set(files) | {str(PREFIX / 'README.md')}
    image_found = False
    for name in sorted(names.copy()):
        path = safe_path(root, name)
        data = read_bytes(path)
        if not data or not data.strip():
            raise Conflict(f'Missing or empty Purpose artifact: {name}')
        if path.suffix != '.md':
            continue
        text = data.decode('utf-8')
        for alt, target in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', text):
            relative = Path(target)
            dependency = Path(os.path.normpath(path.parent.relative_to(root) / relative))
            if (not alt.strip() or relative.is_absolute()
                    or not dependency.is_relative_to(PREFIX / 'images')):
                raise Conflict('Purpose images require alt text and a path inside the stage images/ folder.')
            safe_path(root, dependency)
            names.add(dependency.as_posix())
            if name == str(PREFIX / DOCUMENTS[0]):
                image_found = True
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                continue
            dependency = Path(os.path.normpath(path.parent.relative_to(root) / target.split('#')[0]))
            if not safe_path(root, dependency).is_file():
                raise Conflict(f'Broken Purpose link in {name}: {target}')
    if not image_found:
        raise Conflict('Purpose document requires an embedded explanatory image.')
    hashes = {}
    for name in sorted(names):
        data = read_bytes(safe_path(root, name))
        if not data:
            raise Conflict(f'Missing or empty Purpose artifact: {name}')
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def completion_status(root: Path, entry: dict) -> dict:
    reviews = entry.get('reviews', [])
    validate_reviews(reviews)
    result = {'status': 'IN_PROGRESS', 'agent_ready': False, 'user_accepted': False,
              'review_stale': False, 'reason': 'No agent readiness assessment is recorded.'}
    if not reviews:
        return result
    latest = reviews[-1]
    try:
        current = bundle_hashes(root, entry['artifacts'])
    except (OSError, ValueError) as exc:
        return dict(result, review_stale=True, reason=str(exc))
    if current != latest['artifacts']:
        return dict(result, review_stale=True,
                    reason='Reviewed documents or images changed; reassess and obtain User acceptance again.')
    accepted = latest['decision'] == 'ACCEPTED'
    return dict(result, status='ACCEPTED' if accepted else 'READY_FOR_ACCEPTANCE',
                agent_ready=True, user_accepted=accepted, recorded_at=latest['recorded_at'],
                reason='User accepted this exact baseline, done for now.' if accepted
                else 'Agent criteria passed; explicit User acceptance is pending.')
