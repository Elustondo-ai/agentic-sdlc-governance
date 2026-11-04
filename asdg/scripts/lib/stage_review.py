"""Read-only validation of hash-bound documentation acceptance outside Purpose.

The human-facing skill supplies the decision; these helpers neither authenticate
the human nor write state. Purpose retains its stronger existing criteria.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from cli_files import Conflict, read_bytes, safe_path


def validate_reviews(reviews: list, number: str, prefix: Path) -> None:
    if not isinstance(reviews, list):
        raise Conflict('Stage reviews must be an append-only list.')
    ready = []
    for event in reviews:
        if not isinstance(event, dict):
            raise Conflict('Invalid stage review event.')
        decision = event.get('decision')
        extra = {'criteria'} if decision == 'READY_FOR_ACCEPTANCE' else {'statement'}
        if (decision not in ('READY_FOR_ACCEPTANCE', 'ACCEPTED') or
                set(event) != {'decision', 'actor', 'recorded_at', 'artifacts'} | extra):
            raise Conflict('Unsupported stage review decision or fields.')
        if not isinstance(event['recorded_at'], str) or not event['recorded_at'].strip():
            raise Conflict('Stage reviews require a recorded time.')
        hashes = event['artifacts']
        if not isinstance(hashes, dict) or not hashes:
            raise Conflict('Stage reviews require exact artifact hashes.')
        for name, digest in hashes.items():
            if not isinstance(name, str):
                raise Conflict('Stage review paths must be strings.')
            path = Path(name)
            if (path.is_absolute() or '..' in path.parts or path.as_posix() != name
                    or not path.is_relative_to(prefix)):
                raise Conflict('Stage review paths must stay inside their evidence folder.')
            if not isinstance(digest, str) or not re.fullmatch(r'[a-f0-9]{64}', digest):
                raise Conflict('Stage reviews require SHA-256 hashes.')
        if decision == 'READY_FOR_ACCEPTANCE':
            criteria = event['criteria']
            if (event['actor'] != f'ASDG-{number}' or not isinstance(criteria, dict) or not criteria
                    or any(not isinstance(k, str) or not k.strip() or
                           not isinstance(v, str) or not v.strip() for k, v in criteria.items())):
                raise Conflict('Readiness requires stage-specific criterion evidence and the owning role.')
            ready.append(hashes)
        elif (event['actor'] != 'User' or not isinstance(event['statement'], str)
              or not event['statement'].strip() or hashes not in ready):
            raise Conflict('Acceptance requires a User statement and matching prior readiness hashes.')


def bundle_hashes(root: Path, files: list[str], prefix: Path) -> dict[str, str]:
    """Bind named artifacts, navigation and transitively linked local stage assets.

    Outgoing local source links must resolve, but do not pull other stages into
    this approval. Only relative inline Markdown links are traversed.
    """
    if not files or len(files) != len(set(files)):
        raise Conflict('Register a nonempty, unique stage artifact list before review.')
    names = set(files)
    navigation = prefix / 'README.md'
    if safe_path(root, navigation).is_file():
        names.add(navigation.as_posix())
    pending, hashes = list(names), {}
    while pending:
        name = pending.pop()
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or not path.is_relative_to(prefix):
            raise Conflict('Stage artifacts must stay inside their evidence folder.')
        data = read_bytes(safe_path(root, path))
        if not data or not data.strip():
            raise Conflict(f'Missing or empty stage artifact: {name}')
        hashes[name] = hashlib.sha256(data).hexdigest()
        if path.suffix.lower() != '.md':
            continue
        for match in re.finditer(r'(!?)\[([^\]]*)\]\(([^)]+)\)', data.decode('utf-8')):
            image, alt, target = match.groups()
            target = target.strip().removeprefix('<').removesuffix('>')
            url = urlsplit(target)
            if image and (not alt.strip() or url.scheme or url.netloc):
                raise Conflict('Reviewed images require alt text and local relative files.')
            if url.scheme or url.netloc or not url.path:
                if image:
                    raise Conflict('Reviewed images require a local file.')
                continue
            relative = Path(unquote(url.path))
            if relative.is_absolute():
                raise Conflict('Reviewed local links must be relative to the document.')
            dependency = Path(os.path.normpath(path.parent / relative))
            if not safe_path(root, dependency).is_file():
                raise Conflict(f'Broken stage link in {name}: {target}')
            if image and not dependency.is_relative_to(prefix):
                raise Conflict('Reviewed images must stay inside the stage evidence folder.')
            dep = dependency.as_posix()
            if dependency.is_relative_to(prefix) and dep not in names:
                names.add(dep)
                pending.append(dep)
    return dict(sorted(hashes.items()))


def completion_status(root: Path, entry: dict, number: str, prefix: Path) -> dict:
    reviews = entry.get('reviews', [])
    validate_reviews(reviews, number, prefix)
    result = {'status': 'IN_PROGRESS', 'agent_ready': False, 'user_accepted': False,
              'review_stale': False, 'reason': 'No stage readiness assessment is recorded.'}
    if not reviews:
        return result
    latest = reviews[-1]
    try:
        current = bundle_hashes(root, entry.get('artifacts', []), prefix)
    except (OSError, ValueError) as exc:
        return dict(result, review_stale=True, reason=str(exc))
    if current != latest['artifacts']:
        return dict(result, review_stale=True,
                    reason='Reviewed artifacts changed; reassess and obtain User acceptance again.')
    accepted = latest['decision'] == 'ACCEPTED'
    return dict(result, status='ACCEPTED' if accepted else 'READY_FOR_ACCEPTANCE',
                agent_ready=True, user_accepted=accepted, recorded_at=latest['recorded_at'],
                reason='User accepted this exact documentation baseline, done for now.' if accepted
                else 'Stage criteria passed; explicit User acceptance is pending.')
