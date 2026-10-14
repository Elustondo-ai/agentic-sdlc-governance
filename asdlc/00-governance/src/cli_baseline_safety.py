"""Bounded evidence selection and strict specialist-output validation."""
from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from cli_files import Conflict, safe_path
from cli_baseline_provenance import validate_provenance
from cli_baseline_diagnostics import SECRET, ValidationDiagnostic, sanitize_text

VISUALS = {'.puml', '.mmd', '.svg', '.png', '.jpg', '.jpeg', '.webp'}
SKIP_DIRS = {'.git', '.asdlc', '.codex', '.ssh', '.aws', 'node_modules', '.venv', 'venv',
             '__pycache__', '.next', 'dist', 'build', '.pytest_cache', '.cache'}
SKIP_NAMES = {'.env', 'id_rsa', 'id_ed25519', 'auth.json', 'credentials.json', 'service-account.json'}
MAX_FILES, MAX_FILE, MAX_TOTAL, MAX_ARTIFACTS = 500, 2 * 1024 * 1024, 20 * 1024 * 1024, 30


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact(text: str) -> str:
    clean = SECRET.sub(b'[REDACTED]', str(text).encode('utf-8')).decode('utf-8', errors='replace')
    return re.sub(r'\s+', ' ', clean).strip()[:320]


def source_manifest(source: Path) -> tuple[list[dict], list[str]]:
    files, skipped, total = [], [], 0
    for directory, names, filenames in os.walk(source, followlinks=False):
        base = Path(directory)
        retained = []
        for name in sorted(names):
            path = base / name
            if path.is_symlink() or name in SKIP_DIRS or name.startswith('.venv'):
                skipped.append(path.relative_to(source).as_posix() + ' (excluded directory/symlink)')
            else:
                retained.append(name)
        names[:] = retained
        for name in sorted(filenames):
            path = base / name
            rel = path.relative_to(source).as_posix()
            if path.is_symlink():
                skipped.append(rel + ' (symlink)')
                continue
            if name.lower() in SKIP_NAMES or name in SKIP_DIRS or name.startswith('.env.') or path.suffix.lower() in {
                    '.key', '.pem', '.p12', '.pfx', '.sqlite', '.sqlite3', '.db'}:
                skipped.append(rel + ' (private/unsupported)')
                continue
            try:
                safe_path(source, rel)
                if not path.is_file():
                    continue
                size = path.stat().st_size
                if size > MAX_FILE or len(files) >= MAX_FILES or total + size > MAX_TOTAL:
                    skipped.append(rel + ' (resource limit)')
                    continue
                data = path.read_bytes()
                if len(data) != size or len(data) > MAX_FILE:
                    raise Conflict(f'Source changed while reading: {rel}')
                data.decode('utf-8')
            except (OSError, UnicodeError):
                skipped.append(rel + ' (unreadable/binary)')
                continue
            if b'\x00' in data or SECRET.search(data):
                skipped.append(rel + ' (binary/sensitive content)')
                continue
            total += len(data)
            files.append({'path': rel, 'size': len(data), 'sha256': digest(data)})
    if not files:
        raise Conflict('The source contains no inspectable files; cannot capture a baseline.')
    return sorted(files, key=lambda item: item['path']), sorted(skipped)


def copy_inventory(source: Path, destination: Path, manifest: list[dict]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for entry in manifest:
        relative = Path(entry['path'])
        original = safe_path(source, relative)
        data = original.read_bytes()
        if digest(data) != entry['sha256']:
            raise Conflict(f'Source changed during capture: {relative}')
        output = safe_path(destination, relative)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        output.chmod(0o400)


def validate_visual(path: Path, data: bytes) -> None:
    extension = path.suffix.lower()
    if extension == '.png':
        valid = data.startswith(b'\x89PNG\r\n\x1a\n')
    elif extension in ('.jpg', '.jpeg'):
        valid = data.startswith(b'\xff\xd8\xff')
    elif extension == '.webp':
        valid = data.startswith(b'RIFF') and data[8:12] == b'WEBP'
    else:
        text = data.decode('utf-8')
        if re.search(r'(?i)PME-APPROVED|<script|javascript:|<!ENTITY|<!DOCTYPE|!include|%load_|^\s*click\s|%%\{', text, re.M):
            raise Conflict(f'Unsafe visual content: {path}')
        if extension == '.puml':
            valid = text.strip().startswith('@startuml') and text.strip().endswith('@enduml')
        elif extension == '.mmd':
            declaration = '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('%%'))
            valid = bool(re.match(r'\s*(?:flowchart|graph|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|journey|gantt|pie|mindmap|timeline|C4Context|C4Container|C4Component|C4Dynamic|C4Deployment|quadrantChart|requirementDiagram|gitGraph|block-beta|packet-beta|architecture-beta|kanban|xychart-beta|sankey-beta|radar-beta|treemap-beta)\b', declaration))
        else:
            tree = ET.fromstring(text)
            valid = tree.tag.rsplit('}', 1)[-1] == 'svg'
            for node in tree.iter():
                tag = node.tag.rsplit('}', 1)[-1].lower()
                if tag in {'script', 'foreignobject', 'iframe', 'animate', 'animatetransform', 'set'}:
                    raise Conflict(f'Active SVG content: {path}')
                styles = [value for key, value in node.attrib.items() if key.lower() == 'style']
                if tag == 'style':
                    styles.append(''.join(node.itertext()))
                for style in styles:
                    if re.search(r'(?i)@import|url\(\s*[\"\']?(?!#)[^\s\"\')]', style):
                        raise Conflict(f'External SVG styling: {path}')
                for key, value in node.attrib.items():
                    if key.lower().startswith('on') or (key.rsplit('}', 1)[-1] in {'href', 'src'} and not value.startswith('#')):
                        raise Conflict(f'Unsafe SVG reference: {path}')
    if not valid:
        first = compact(data.decode('utf-8', errors='replace').splitlines()[0])
        raise Conflict(f'Invalid visual format: {path}; first line: {first}')


def docs_from_output(output: Path, agent: dict | None = None, *,
                     evidence_root: Path | None = None) -> list[tuple[Path, bytes]]:
    if output.is_symlink() or not output.is_dir():
        raise Conflict('Specialist failed to create a regular output/ directory.')
    entries, units = [], set()
    for directory, names, files in os.walk(output, followlinks=False):
        base = Path(directory)
        for name in names:
            if (base / name).is_symlink():
                raise Conflict('Specialist output contains symlink.')
            relative = (base / name).relative_to(output)
            if len(relative.parts) != 1 or not re.fullmatch(r'\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*', name):
                raise Conflict(f'Unexpected specialist output directory: {relative}')
            units.add(relative)
        for name in sorted(files):
            path = base / name
            rel = path.relative_to(output)
            safe_path(output, rel)
            if len(rel.parts) != 2 or not re.fullmatch(r'\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*', rel.parts[0]):
                raise Conflict(f'Unexpected specialist artifact path: {rel}')
            if name != 'speaker-notes.md' and not (path.stem == 'visual' and path.suffix in VISUALS):
                raise Conflict(f'Unexpected artifact type: {rel}')
            if not path.is_file() or path.stat().st_nlink != 1 or not 0 < path.stat().st_size <= MAX_FILE:
                raise Conflict(f'Artifact is empty, oversized, linked, or not a regular file: {rel}')
            data = path.read_bytes()
            if SECRET.search(data):
                raise Conflict(f'Sensitive content in specialist artifact: {rel}')
            if name == 'speaker-notes.md':
                text = data.decode('utf-8')
                if len(text.splitlines()) > 50:
                    raise Conflict(f'Documentation exceeds 50 physical lines: {rel}')
                stamp = re.match(r'^AI-MODIFIED - (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\n', text)
                if not stamp:
                    raise Conflict(f'Document is missing its plain AI-MODIFIED status: {rel}')
                datetime.strptime(stamp.group(1), '%Y-%m-%dT%H:%M:%SZ')
                if 'PME-APPROVED' in text:
                    raise Conflict(f'Specialist must not grant PME approval: {rel}')
                if agent:
                    if not re.search(r'^Agent: ' + re.escape(agent['role_id']) + r'\s*$', text, re.M):
                        raise Conflict(f'Stage ownership mismatch: {rel}')
                    for label in ('Sources:', 'Uncertainties:', 'Contradictions:'):
                        if label not in text:
                            raise Conflict(f'Missing {label} in {rel}')
                    try:
                        validate_provenance(text, evidence_root or output.parent, artifact_dir=path.parent)
                    except ValidationDiagnostic as exc:
                        exc.diagnostic['artifact'] = sanitize_text(rel.as_posix())
                        raise
                elif evidence_root is not None:
                    try:
                        validate_provenance(text, evidence_root, artifact_dir=path.parent)
                    except ValidationDiagnostic as exc:
                        exc.diagnostic['artifact'] = sanitize_text(rel.as_posix())
                        raise
            else:
                validate_visual(rel, data)
            entries.append((rel, data))
            if len(entries) > MAX_ARTIFACTS:
                raise Conflict('Too many specialist artifacts.')
    if not entries:
        raise Conflict('No documents produced.')
    for directory in units:
        names = [relative.name for relative, _ in entries if relative.parent == directory]
        if len(names) != 2 or 'speaker-notes.md' not in names or sum(name.startswith('visual.') for name in names) != 1:
            raise Conflict(f'Each unit needs exactly one visual and speaker-notes.md: {directory}')
    return sorted(entries)
