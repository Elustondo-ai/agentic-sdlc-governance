"""Resolve declared snapshot evidence without fetching narrative citations."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from cli_files import Conflict, safe_path
from cli_baseline_diagnostics import ValidationDiagnostic

SNAPSHOT_FORMAT = 'Use an existing source/ or context/ snapshot file; Sources entries are separated by semicolons.'
INLINE_FORMAT = 'Use an inline source/context or authored-artifact link; put unverified external citations on Narrative citations:.'


def citation_error(message: str, code: str, target: str | None, rule: str,
                   expected: str = SNAPSHOT_FORMAT) -> ValidationDiagnostic:
    return ValidationDiagnostic(message, code='BASELINE_CITATION_' + code,
                                target=target, rule=rule, expected=expected)


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
    original = value
    value = unquote(reference_target(value))
    # Anchors and conventional line suffixes identify a passage, not another file.
    value = value.split('#', 1)[0]
    value = re.sub(r':\d+(?:-\d+)?$', '', value)
    parts = value.split('/')
    if (len(parts) < 2 or parts[0] not in {'source', 'context'}
            or any(part in {'', '.', '..'} for part in parts)
            or any(character in value for character in ('\\', ':', '?', '\x00'))):
        raise citation_error('Unsupported or unsafe evidence reference; use source/ or context/ snapshot files.',
                             'UNSAFE_REFERENCE', original, 'Evidence references must remain inside source/ or context/.')
    try:
        target = safe_path(root, value)
    except Conflict as exc:
        raise citation_error(str(exc), 'UNSAFE_PATH', original,
                             'Evidence paths cannot traverse symlinks or non-directory ancestors.') from exc
    if not target.is_file() or target.stat().st_nlink != 1:
        raise citation_error('Evidence reference is missing, linked or not a regular snapshot file.',
                             'UNRESOLVED_REFERENCE', original, 'Evidence must resolve to a regular, unlinked snapshot file.')
    return value


def validate_provenance(text: str, root: Path, *, artifact_dir: Path | None = None) -> list[str]:
    """Sources entries are files; narrative citations never satisfy this requirement.

    Accept semicolon-delimited raw paths, backticks, Markdown links, URL-encoded
    filenames and passage suffixes. Check supported local references in the body;
    reject reference-style Markdown rather than silently ignoring destinations.
    """
    if root.is_symlink() or not root.is_dir():
        raise citation_error('Provenance requires a regular isolated evidence workspace.',
                             'WORKSPACE', None, 'The evidence workspace must be a regular directory.')
    declarations = list(re.finditer(r'^Sources:[ \t]*(.+)$', text, re.M))
    if not declarations:
        raise citation_error('Missing Sources: snapshot evidence declaration.',
                             'SOURCES_REQUIRED', None, 'Every notes artifact must declare snapshot Sources:.')
    resolved, masked = set(), list(text)

    def mask(start: int, end: int) -> None:
        masked[start:end] = ' ' * (end - start)

    def located(error: ValidationDiagnostic, offset: int) -> ValidationDiagnostic:
        error.diagnostic['line'] = text.count('\n', 0, offset) + 1
        return error

    def resolve(value: str, offset: int) -> str:
        try:
            return resolve_reference(root, value)
        except ValidationDiagnostic as exc:
            raise located(exc, offset) from exc.__cause__

    for declaration in declarations:
        offset = declaration.start(1)
        for item in declaration.group(1).split(';'):
            resolved.add(resolve(item, offset))
            offset += len(item) + 1
        mask(declaration.start(), declaration.end())

    # This deliberately bounded grammar does not resolve Markdown reference labels.
    # Reject definitions (also multiline/container forms), full and collapsed
    # references, including examples and narrative lines. Rejecting definitions
    # also closes shortcut-reference links without mistaking every [word] for one.
    unsupported = re.search(r'\[(?:\\.|[^\[\]\\])+\][ \t]*:|\]\s*\[', ''.join(masked))
    if unsupported:
        excerpt = text[unsupported.start():text.find('\n', unsupported.end()) if '\n' in text[unsupported.end():] else len(text)]
        raise located(citation_error('Reference-style citations are unsupported; use inline links to snapshot files.',
                      'REFERENCE_STYLE', excerpt, 'Reference-style Markdown citations are unsupported.', INLINE_FORMAT), unsupported.start())

    # External narrative citations are explicitly unverified, never local evidence.
    for narrative in re.finditer(r'^Narrative citations:[^\n]*$', text, re.M):
        snapshot = re.search(r'(?<![\w/:])(?:source|context)/', narrative.group())
        if snapshot:
            raise located(citation_error('Snapshot references belong in Sources:, not narrative citations.',
                          'NARRATIVE_SNAPSHOT', narrative.group()[snapshot.start():],
                          'Narrative citations cannot disguise local snapshot evidence.'), narrative.start() + snapshot.start())
        mask(narrative.start(), narrative.end())

    autolink = re.search(r'<(?:[A-Za-z][A-Za-z0-9+.-]*:[^<>\s]*|[^<>\s@]+@[^<>\s@]+)>', ''.join(masked))
    if autolink:
        raise located(citation_error('External autolink; declare it as an unverified narrative citation.',
                      'AUTOLINK', autolink.group(), 'External autolinks must be explicitly unverified narrative citations.', INLINE_FORMAT), autolink.start())

    for pattern in (r'\[[^\]\n]+\]\(([^)\n]+)\)', r'`((?:source|context)/[^`\n]+)`'):
        for match in re.finditer(pattern, ''.join(masked)):
            value = reference_target(match.group(1))
            if value.startswith(('source/', 'context/')):
                resolved.add(resolve(value, match.start(1)))
                mask(match.start(), match.end())
            elif not value.startswith('#'):
                local = unquote(value).split('#', 1)[0]
                if (artifact_dir is None or Path(local).is_absolute() or '..' in Path(local).parts
                        or any(char in local for char in ('\\', ':', '?', '\x00'))):
                    raise located(citation_error('External or unsupported citation; declare it as an unverified narrative citation.',
                                  'UNSUPPORTED', match.group(1), 'Inline citations must resolve to snapshot or authored-artifact files.', INLINE_FORMAT), match.start(1))
                try:
                    target = safe_path(artifact_dir, local)
                except Conflict as exc:
                    raise located(citation_error(str(exc), 'UNSAFE_PATH', match.group(1),
                                  'Authored-artifact links cannot traverse symlinks or non-directory ancestors.', INLINE_FORMAT), match.start(1)) from exc
                if not target.is_file() or target.stat().st_nlink != 1:
                    raise located(citation_error('Citation does not resolve to a source/context file or an authored artifact.',
                                  'UNRESOLVED_ARTIFACT', match.group(1), 'Citations must resolve to a regular, unlinked authored artifact.', INLINE_FORMAT), match.start(1))
                mask(match.start(), match.end())
    # Already-declared paths with spaces may also be mentioned in plain prose.
    remaining = ''.join(masked)
    for value in sorted(resolved, key=len, reverse=True):
        if ' ' in value:
            remaining = re.sub(re.escape(value) + r'(?![\w/.-])',
                               lambda match: ' ' * len(match.group()), remaining)
    for match in re.finditer(r'(?<![\w/])(?:source|context)/[^\s;,`<>()\[\]]+', remaining):
        resolved.add(resolve(match.group().rstrip('.!?'), match.start()))
    return sorted(resolved)
