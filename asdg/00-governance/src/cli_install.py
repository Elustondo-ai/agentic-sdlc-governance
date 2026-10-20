#!/usr/bin/env python3
"""No-argument, user-local ASDG installation. No dependencies are downloaded."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from cli_files import Conflict, apply, plan, read_bytes, safe_path
from cli_model import COMMAND, PROVIDER, REPO, SHORT_COMMAND, VERSION, catalogue, json_bytes, sha, require_python

MANIFEST = Path('.config/asdg/installation.json')
LEGACY_MANIFEST = Path('.config/elustondo-asdlc/installation.json')
LEGACY_PROVIDER = 'elustondo.ai/asdlc'
START = '# >>> Elustondo.ai ASDG PATH >>>'
FINISH = '# <<< Elustondo.ai ASDG PATH <<<'
PATH_BLOCK = f'''{START}
case ":${{PATH-}}:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin${{PATH:+:$PATH}}" ;;
esac
{FINISH}
'''
LEGACY_START = '# >>> Elustondo.ai ASDLC PATH >>>'
LEGACY_FINISH = '# <<< Elustondo.ai ASDLC PATH <<<'
LEGACY_PATH_BLOCK = PATH_BLOCK.replace(START, LEGACY_START).replace(FINISH, LEGACY_FINISH)


def shell_files(home: Path, shell: str, zdotdir: str = '') -> list[Path]:
    name = Path(shell).name
    if name == 'zsh':
        base = Path(zdotdir).expanduser() if zdotdir else home
        if not base.is_absolute():
            raise Conflict('ZDOTDIR must be absolute for this installer.')
        base = base.resolve()
        try:
            rel = base.relative_to(home)
        except ValueError as exc:
            raise Conflict('ZDOTDIR outside HOME requires manual PATH setup; no files changed.') from exc
        return [rel / '.zprofile', rel / '.zshrc']
    if name == 'bash':
        login = next((Path(p) for p in ('.bash_profile', '.bash_login', '.profile')
                      if (home / p).exists()), Path('.bash_profile'))
        return [login, Path('.bashrc')]
    raise Conflict('This installer supports zsh and bash. No shell setup was changed.')


def shell_text(old: bytes | None) -> bytes:
    text = '' if old is None else old.decode('utf-8')
    for start, finish, block in ((START, FINISH, PATH_BLOCK),
                                 (LEGACY_START, LEGACY_FINISH, LEGACY_PATH_BLOCK)):
        if start in text or finish in text:
            if text.count(start) != 1 or text.count(finish) != 1 or block not in text:
                raise Conflict('Existing ASDG/ASDLC PATH block was edited; reconcile it before reinstalling.')
    if LEGACY_PATH_BLOCK in text:
        # Preserve all bytes outside the recognized block, including user settings.
        text = text.replace(LEGACY_PATH_BLOCK, '' if PATH_BLOCK in text else PATH_BLOCK, 1)
    if PATH_BLOCK in text:
        return text.encode('utf-8')
    return (text + ('\n' if text and text.endswith('\n') else '\n\n' if text else '') + PATH_BLOCK).encode('utf-8')


def launcher(repo: Path, python: Path) -> bytes:
    script = repo / 'bin/asdg'
    return (f'#!/usr/bin/env python3\n# Managed by {PROVIDER}; do not edit.\n'
            'import os\nimport sys\nfrom pathlib import Path\n'
            f'script = {str(script)!r}\npython = {str(python)!r}\n'
            'if not Path(script).is_file():\n'
            "    sys.exit('ASDG checkout moved or is unavailable; rerun ./bin/asdg install from its new location.')\n"
            'try:\n'
            "    os.execv(python, [python, '-B', script, *sys.argv[1:]])\n"
            'except OSError as exc:\n'
            "    sys.exit('ASDG interpreter unavailable; rerun ./bin/asdg install: ' + str(exc))\n").encode('utf-8')


def recorded_shell_files(record: dict) -> list[Path]:
    files = record.get('shell_files', [])
    if (not isinstance(files, list)
            or any(not isinstance(p, str) or Path(p).is_absolute() or '..' in Path(p).parts
                   or Path(p).name not in ('.zprofile', '.zshrc', '.bash_profile',
                                          '.bash_login', '.profile', '.bashrc') for p in files)):
        raise Conflict('Invalid installation shell files; nothing replaced.')
    return [Path(p) for p in files]


def legacy_launcher(record: dict) -> bytes:
    """Reconstruct the historical format, never execute an installed launcher.

    Source: e40152c, asdlc/00-governance/src/cli_install.py. A recorded hash
    alone is insufficient: both the record and installed bytes must match
    this exact template. Historical checkout/interpreter paths may have moved.
    """
    if (record.get('provider') != LEGACY_PROVIDER
            or record.get('cli_version') not in ('0.1.3', '0.1.4')
            or record.get('mode') != 'linked-development-checkout'
            or record.get('commands') != ['elustondo-asdlc', 'asdg']):
        raise Conflict('Unrecognized legacy ASDG installation record; nothing replaced.')
    for key in ('checkout', 'python'):
        value = record.get(key)
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise Conflict(f'Invalid legacy installation {key}; nothing replaced.')
    if not recorded_shell_files(record):
        raise Conflict('Invalid legacy installation shell files; nothing replaced.')
    script = Path(record['checkout']) / 'asdg'
    python = Path(record['python'])
    expected = (f'#!/usr/bin/env python3\n# Managed by {LEGACY_PROVIDER}; do not edit.\n'
                'import os\nimport sys\nfrom pathlib import Path\n'
                f'script = {str(script)!r}\npython = {str(python)!r}\n'
                'if not Path(script).is_file():\n'
                "    sys.exit('ASDLC checkout moved or is unavailable; rerun ./asdg install from its new location.')\n"
                'try:\n'
                "    os.execv(python, [python, '-B', script, *sys.argv[1:]])\n"
                'except OSError as exc:\n'
                "    sys.exit('ASDLC interpreter unavailable; rerun ./asdg install: ' + str(exc))\n").encode('utf-8')
    if sha(expected) != record.get('launcher_sha256'):
        raise Conflict('Legacy launcher record does not match the known format; nothing replaced.')
    return expected


def installation_record(home: Path, relative: Path, provider: str) -> tuple[bytes | None, dict]:
    raw = read_bytes(safe_path(home, relative))
    record = json.loads(raw) if raw is not None else {}
    if raw is not None and (not isinstance(record, dict) or record.get('provider') != provider):
        raise Conflict(f'Existing installation manifest belongs to something else: {relative}')
    return raw, record


def backup(home: Path, relative: Path, data: bytes):
    name = sha(str(relative).encode())[:12] + '-' + sha(data) + '.before'
    return plan(home, Path('.config/asdg/backups') / name, data, mode=0o600)


def install(home: Path, shell: str, search_path: str, repo: Path = REPO,
            python: Path | None = None, zdotdir: str = '') -> dict:
    home, repo = home.resolve(strict=True), repo.resolve(strict=True)
    python = python or Path(sys.executable)
    catalogue(repo)  # Fail before modifying a developer environment if the provider is incomplete.
    if not (repo / 'bin/asdg').is_file() or not (repo / 'asdg/00-governance/src/cli.py').is_file():
        raise Conflict('CLI source is missing from this checkout.')
    launch = launcher(repo, python)
    old_manifest, previous = installation_record(home, MANIFEST, PROVIDER)
    old_legacy, legacy, expected_legacy = None, {}, None
    # A current record is authoritative. Never use legacy metadata to bypass a
    # conflicting current record, including after a successful migration.
    if old_manifest is None:
        old_legacy, legacy = installation_record(home, LEGACY_MANIFEST, LEGACY_PROVIDER)
        if old_legacy is not None:
            expected_legacy = legacy_launcher(legacy)
    # Detect collisions anywhere on PATH, not just at our target path.
    for name in dict.fromkeys((COMMAND, SHORT_COMMAND)):
        target = home / '.local/bin' / name
        for part in search_path.split(os.pathsep):
            found = Path(part or os.curdir) / name
            if found.exists() and os.access(found, os.X_OK) and found.resolve() != target:
                raise Conflict(f'Command name already in use: {found}. Nothing replaced.')
        path = safe_path(home, Path('.local/bin') / name)
        old = read_bytes(path)
        if old is not None and old != launch:
            if expected_legacy is not None:
                if old != expected_legacy:
                    raise Conflict(f'Existing command is not the verified legacy ASDG launcher: {path}')
            elif sha(old) != previous.get('launcher_sha256'):
                raise Conflict(f'Existing command is not an unchanged ASDG launcher: {path}')
    files = shell_files(home, shell, zdotdir)
    # Retain existing recorded startup files when the user switches shells.
    # This also keeps the migrated manifest stable on subsequent installs.
    for relative in recorded_shell_files(previous if old_manifest is not None else legacy):
        if relative not in files and read_bytes(safe_path(home, relative)) is not None:
            files.append(relative)
    changes, backups = [], []
    for relative in files:
        old = read_bytes(safe_path(home, relative))
        updated = shell_text(old)
        if old is not None and old != updated:
            backups.append(backup(home, relative, old))
        changes.append(plan(home, relative, updated, replace=True))
    for name in dict.fromkeys((COMMAND, SHORT_COMMAND)):
        relative = Path('.local/bin') / name
        old = read_bytes(safe_path(home, relative))
        if old is not None and old != launch:
            backups.append(backup(home, relative, old))
        changes.append(plan(home, relative, launch, replace=True, mode=0o755))
    manifest = {'provider': PROVIDER, 'cli_version': VERSION,
                'checkout': str(repo), 'python': str(python), 'launcher_sha256': sha(launch),
                'commands': list(dict.fromkeys((COMMAND, SHORT_COMMAND))), 'shell_files': [str(p) for p in files],
                'mode': 'linked-development-checkout'}
    if old_manifest is not None and old_manifest != json_bytes(manifest):
        backups.append(backup(home, MANIFEST, old_manifest))
    if old_legacy is not None:
        backups.append(backup(home, LEGACY_MANIFEST, old_legacy))
    changes.append(plan(home, MANIFEST, json_bytes(manifest), replace=True, mode=0o600))
    # All recoverable originals are written before replacing any managed file.
    written = apply([change for change in backups + changes if change is not None])
    return {'files_changed': written, 'checkout': str(repo), 'home': str(home)}


def main(argv=None) -> int:
    if (sys.argv[1:] if argv is None else argv):
        print('Usage: ./bin/asdg install (no options)', file=sys.stderr)
        return 2
    if not require_python():
        return 1
    if os.environ.get('SUDO_USER') or os.getuid() == 0:
        print('Run ./bin/asdg install as your normal user, without sudo.', file=sys.stderr)
        return 1
    try:
        shell = os.environ.get('SHELL', '')
        if not shell:
            import pwd
            shell = pwd.getpwuid(os.getuid()).pw_shell
        install(Path.home(), shell, os.environ.get('PATH', ''),
                zdotdir=os.environ.get('ZDOTDIR', ''))
        print('ALL GOOD! Elustondo.ai ASDG installed successfully.')
        print(f'Next: open a new terminal, cd into your project, and run: {SHORT_COMMAND} init')
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'ASDG install: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
