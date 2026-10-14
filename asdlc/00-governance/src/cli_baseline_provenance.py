"""Resolve declared snapshot evidence without fetching narrative citations."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from cli_files import Conflict, safe_path


def reference_target(value: str) -> str:
    value = value.strip()
    link = re.fullmatch(r'\[[^\]\n]+\]\((.+)\)', value)
    if link:
        value = link.group(1).strip()
    if value.startswith('<') and value.endswith('>'):
        value = value[1:-1]
    if value.startswith('`') and value.endswith('`'):
        value = value[1:-1]
    return value


def resolve_reference(root: Path, value: str) -> str:
    value = unquote(reference_target(value))
    # Anchors and conventional line suffixes identify a passage, not another file.
    value = value.split('#', 1)[0]
    value = re.sub(r':\d+(?:-\d+)?$', '', value)
    parts = value.split('/')
    if (len(parts) < 2 or parts[0] not in {'source', 'context'}
            or any(part in {'', '.', '..'} for part in parts)
            or any(character in value for character in ('\\', ':', '?', '\x00'))):
        raise Conflict('Unsupported or unsafe evidence reference; use source/ or context/ snapshot files.')
    target = safe_path(root, value)
    if not target.is_file() or target.stat().st_nlink != 1:
        raise Conflict('Evidence reference is missing, linked or not a regular snapshot file.')
    return value


def validate_provenance(text: str, root: Path, *, artifact_dir: Path | None = None) -> list[str]:
    """Sources entries are files; narrative citations never satisfy this requirement.

    Accept semicolon-delimited raw paths, backticks, Markdown links, URL-encoded
    filenames and passage suffixes. Check supported local references in the body;
    reject reference-style Markdown rather than silently ignoring destinations.
    """
    if root.is_symlink() or not root.is_dir():
        raise Conflict('Provenance requires a regular isolated evidence workspace.')
    declarations = list(re.finditer(r'^Sources:[ \t]*(.+)$', text, re.M))
    if not declarations:
        raise Conflict('Missing Sources: snapshot evidence declaration.')
    resolved, masked = set(), list(text)

    def mask(start: int, end: int) -> None:
        masked[start:end] = ' ' * (end - start)

    for declaration in declarations:
        for item in declaration.group(1).split(';'):
            resolved.add(resolve_reference(root, item))
        mask(declaration.start(), declaration.end())

    # This deliberately bounded grammar does not resolve Markdown reference labels.
    # Reject definitions (also multiline/container forms), full and collapsed
    # references, including examples and narrative lines. Rejecting definitions
    # also closes shortcut-reference links without mistaking every [word] for one.
    if re.search(r'\[(?:\\.|[^\[\]\\])+\][ \t]*:|\]\s*\[', ''.join(masked)):
        raise Conflict('Reference-style citations are unsupported; use inline links to snapshot files.')

    # External narrative citations are explicitly unverified, never local evidence.
    for narrative in re.finditer(r'^Narrative citations:[^\n]*$', text, re.M):
        if re.search(r'(?<![\w/:])(?:source|context)/', narrative.group()):
            raise Conflict('Snapshot references belong in Sources:, not narrative citations.')
        mask(narrative.start(), narrative.end())

    if re.search(r'<(?:[A-Za-z][A-Za-z0-9+.-]*:[^<>\s]*|[^<>\s@]+@[^<>\s@]+)>', ''.join(masked)):
        raise Conflict('External autolink; declare it as an unverified narrative citation.')

    for pattern in (r'\[[^\]\n]+\]\(([^)\n]+)\)', r'`((?:source|context)/[^`\n]+)`'):
        for match in re.finditer(pattern, ''.join(masked)):
            value = reference_target(match.group(1))
            if value.startswith(('source/', 'context/')):
                resolved.add(resolve_reference(root, value))
                mask(match.start(), match.end())
            elif not value.startswith('#'):
                local = unquote(value).split('#', 1)[0]
                if (artifact_dir is None or Path(local).is_absolute() or '..' in Path(local).parts
                        or any(char in local for char in ('\\', ':', '?', '\x00'))):
                    raise Conflict('External or unsupported citation; declare it as an unverified narrative citation.')
                target = safe_path(artifact_dir, local)
                if not target.is_file() or target.stat().st_nlink != 1:
                    raise Conflict('Citation does not resolve to a source/context file or an authored artifact.')
                mask(match.start(), match.end())
    # Already-declared paths with spaces may also be mentioned in plain prose.
    remaining = ''.join(masked)
    for value in sorted(resolved, key=len, reverse=True):
        if ' ' in value:
            remaining = re.sub(re.escape(value) + r'(?![\w/.-])',
                               lambda match: ' ' * len(match.group()), remaining)
    for match in re.finditer(r'(?<![\w/])(?:source|context)/[^\s;,`<>()\[\]]+', remaining):
        resolved.add(resolve_reference(root, match.group().rstrip('.!?')))
    return sorted(resolved)
