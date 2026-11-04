"""Resolve the reviewed portable file list without including repository-only tools."""
import json
from pathlib import Path, PurePosixPath

FILE_LIST = 'metadata/package-files.json'
MANIFEST = 'metadata/MANIFEST.json'


def package_files(core: Path) -> list[Path]:
    """Return sorted regular files; reject missing, duplicate or escaping entries."""
    index = core / FILE_LIST
    if index.is_symlink():
        raise ValueError('Package file list cannot be a symlink.')
    value = json.loads(index.read_text(encoding='utf-8'))
    names = value.get('files') if isinstance(value, dict) else None
    if (not isinstance(value, dict) or value.get('schema_version') != 1
            or not isinstance(names, list) or not all(isinstance(n, str) for n in names)):
        raise ValueError('Invalid package file list.')
    if len(names) != len(set(names)) or not {FILE_LIST, MANIFEST} <= set(names):
        raise ValueError('Package list must be unique and include its index and manifest.')
    files = []
    for name in sorted(names):
        relative = PurePosixPath(name)
        if (not name or relative.is_absolute() or '..' in relative.parts or '\\' in name
                or relative.as_posix() != name or name == 'metadata/sync-state.json'
                or any(part in {'.git', '__pycache__', '.asdg', 'build', 'logs'} for part in relative.parts)
                or relative.suffix == '.pyc'):
            raise ValueError('Unsafe package path: ' + name)
        path = core.joinpath(*relative.parts)
        if any((core.joinpath(*relative.parts[:i])).is_symlink()
               for i in range(1, len(relative.parts) + 1)):
            raise ValueError('Symlink in package path: ' + name)
        if not path.is_file():
            raise ValueError('Missing package file: ' + name)
        files.append(path)
    return files
