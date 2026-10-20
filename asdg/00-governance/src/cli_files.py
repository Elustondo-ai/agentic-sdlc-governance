"""Small conservative file transactions for the local installer and initializer."""
from __future__ import annotations

import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


class Conflict(ValueError):
    """A pre-existing resource must be reconciled, not overwritten."""


def safe_path(root: Path, relative: str | Path) -> Path:
    """Disallow traversal and symlinks within a managed destination tree."""
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise Conflict(f'Unsafe relative path: {relative}')
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise Conflict(f'Refusing a symlink in a managed path: {path}')
        if path != root / relative and path.exists() and not path.is_dir():
            raise Conflict(f'Expected a directory: {path}')
    return path


def read_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > 4 * 1024 * 1024:
        raise Conflict(f'Expected a regular file of at most 4 MiB: {path}')
    return path.read_bytes()


@dataclass(frozen=True)
class Change:
    root: Path
    relative: Path
    before: bytes | None
    after: bytes
    mode: int = 0o644

    @property
    def path(self) -> Path:
        return safe_path(self.root, self.relative)


def plan(root: Path, relative: str | Path, data: bytes, *, replace: bool = False,
         mode: int = 0o644) -> Change | None:
    path = safe_path(root, relative)
    old = read_bytes(path)
    if old == data:
        if old is not None and stat.S_IMODE(path.stat().st_mode) != mode and mode == 0o755:
            raise Conflict(f'Executable permission missing: chmod +x {path}')
        return None
    if old is not None and not replace:
        raise Conflict(f'Refusing to overwrite existing file: {path}')
    actual_mode = stat.S_IMODE(path.stat().st_mode) if old is not None else mode
    return Change(root, Path(relative), old, data, actual_mode)


def atomic_replace(path: Path, data: bytes, mode: int) -> None:
    fd, temporary = tempfile.mkstemp(prefix='.asdg-tmp-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(changes: list[Change]) -> list[str]:
    """Preflight all files; roll back only our own changes on ordinary failures.

    Not a transaction against concurrent hostile writers or machine crashes.
    Existing unrelated files are never removed by rollback.
    """
    for change in changes:
        if read_bytes(change.path) != change.before:
            raise Conflict(f'File changed since inspection: {change.path}')
    made_dirs: list[Path] = []
    applied: list[Change] = []
    try:
        for change in changes:
            path = change.path
            pending = []
            parent = path.parent
            while not parent.exists():
                pending.append(parent)
                parent = parent.parent
            for directory in reversed(pending):
                directory.mkdir()
                made_dirs.append(directory)
            if read_bytes(path) != change.before:
                raise Conflict(f'File changed since inspection: {path}')
            if change.before is None:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, change.mode)
                applied.append(change)
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(change.after)
                    stream.flush()
                    os.fsync(stream.fileno())
            else:
                atomic_replace(path, change.after, change.mode)
                applied.append(change)
    except BaseException:
        for change in reversed(applied):
            path = change.path
            if read_bytes(path) == change.after:
                if change.before is None:
                    path.unlink()
                else:
                    atomic_replace(path, change.before, change.mode)
        for directory in reversed(made_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise
    return [str(change.path) for change in changes]
