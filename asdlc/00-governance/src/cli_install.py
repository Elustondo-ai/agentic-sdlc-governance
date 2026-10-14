#!/usr/bin/env python3
"""No-argument, user-local ASDLC installation. No dependencies are downloaded."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from cli_files import Conflict, apply, plan, read_bytes, safe_path
from cli_model import COMMAND, PROVIDER, REPO, SHORT_COMMAND, VERSION, catalogue, json_bytes, sha, require_python

MANIFEST = Path('.config/elustondo-asdlc/installation.json')
START = '# >>> Elustondo.ai ASDLC PATH >>>'
FINISH = '# <<< Elustondo.ai ASDLC PATH <<<'
PATH_BLOCK = f'''{START}
case ":${{PATH-}}:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin${{PATH:+:$PATH}}" ;;
esac
{FINISH}
'''


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
    if START in text or FINISH in text:
        if text.count(START) != 1 or text.count(FINISH) != 1 or PATH_BLOCK not in text:
            raise Conflict('Existing ASDLC PATH block was edited; reconcile it before reinstalling.')
        return old
    return (text + ('\n' if text and text.endswith('\n') else '\n\n' if text else '') + PATH_BLOCK).encode('utf-8')


def launcher(repo: Path, python: Path) -> bytes:
    script = repo / 'asdg'
    return (f'#!/usr/bin/env python3\n# Managed by {PROVIDER}; do not edit.\n'
            'import os\nimport sys\nfrom pathlib import Path\n'
            f'script = {str(script)!r}\npython = {str(python)!r}\n'
            'if not Path(script).is_file():\n'
            "    sys.exit('ASDLC checkout moved or is unavailable; rerun ./asdg install from its new location.')\n"
            'try:\n'
            "    os.execv(python, [python, '-B', script, *sys.argv[1:]])\n"
            'except OSError as exc:\n'
            "    sys.exit('ASDLC interpreter unavailable; rerun ./asdg install: ' + str(exc))\n").encode('utf-8')


def install(home: Path, shell: str, search_path: str, repo: Path = REPO,
            python: Path | None = None, zdotdir: str = '') -> dict:
    home, repo = home.resolve(strict=True), repo.resolve(strict=True)
    python = python or Path(sys.executable)
    catalogue(repo)  # Fail before modifying a developer environment if the provider is incomplete.
    if not (repo / 'asdg').is_file() or not (repo / 'asdlc/00-governance/src/cli.py').is_file():
        raise Conflict('CLI source is missing from this checkout.')
    launch = launcher(repo, python)
    manifest_path = safe_path(home, MANIFEST)
    old_manifest = read_bytes(manifest_path)
    previous = json.loads(old_manifest) if old_manifest is not None else {}
    if old_manifest is not None and (not isinstance(previous, dict) or previous.get('provider') != PROVIDER):
        raise Conflict('Existing installation manifest belongs to something else.')
    # Detect collisions anywhere on PATH, not just at our target path.
    for name in (COMMAND, SHORT_COMMAND):
        target = home / '.local/bin' / name
        for part in search_path.split(os.pathsep):
            found = Path(part or os.curdir) / name
            if found.exists() and os.access(found, os.X_OK) and found.resolve() != target:
                raise Conflict(f'Command name already in use: {found}. Nothing replaced.')
        path = safe_path(home, Path('.local/bin') / name)
        old = read_bytes(path)
        if old is not None and old != launch:
            if sha(old) != previous.get('launcher_sha256'):
                raise Conflict(f'Existing command is not an unchanged ASDLC launcher: {path}')
    files = shell_files(home, shell, zdotdir)
    changes = []
    for relative in files:
        old = read_bytes(safe_path(home, relative))
        updated = shell_text(old)
        if old is not None and old != updated:
            backup_name = sha(str(relative).encode())[:12] + '-' + sha(old) + '.before'
            changes.append(plan(home, Path('.config/elustondo-asdlc/backups') / backup_name,
                                old, mode=0o600))
        changes.append(plan(home, relative, updated, replace=True))
    for name in (COMMAND, SHORT_COMMAND):
        changes.append(plan(home, Path('.local/bin') / name, launch, replace=True, mode=0o755))
    manifest = {'provider': PROVIDER, 'cli_version': VERSION,
                'checkout': str(repo), 'python': str(python), 'launcher_sha256': sha(launch),
                'commands': [COMMAND, SHORT_COMMAND], 'shell_files': [str(p) for p in files],
                'mode': 'linked-development-checkout'}
    changes.append(plan(home, MANIFEST, json_bytes(manifest), replace=True, mode=0o600))
    written = apply([change for change in changes if change is not None])
    return {'files_changed': written, 'checkout': str(repo), 'home': str(home)}


def main(argv=None) -> int:
    if (sys.argv[1:] if argv is None else argv):
        print('Usage: ./asdg install (no options)', file=sys.stderr)
        return 2
    if not require_python():
        return 1
    if os.environ.get('SUDO_USER') or os.getuid() == 0:
        print('Run ./asdg install as your normal user, without sudo.', file=sys.stderr)
        return 1
    try:
        shell = os.environ.get('SHELL', '')
        if not shell:
            import pwd
            shell = pwd.getpwuid(os.getuid()).pw_shell
        install(Path.home(), shell, os.environ.get('PATH', ''),
                zdotdir=os.environ.get('ZDOTDIR', ''))
        print('ALL GOOD! Elustondo.ai ASDLC installed successfully.')
        print(f'Next: open a new terminal, cd into your project, and run: {SHORT_COMMAND} init')
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'ASDLC install: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
