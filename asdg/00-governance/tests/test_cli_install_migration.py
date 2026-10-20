"""Installed-upgrade regressions using isolated HOME directories only."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from test_cli_bootstrap import Fixture
from cli_files import Conflict, atomic_replace
from cli_install import MANIFEST, PATH_BLOCK, install, launcher
from cli_model import PROVIDER, sha


# Frozen from e40152c:asdlc/00-governance/src/cli_install.py, not derived from
# the migration implementation. This is the installed 0.1.3 launcher's format.
HISTORICAL_LAUNCHER = """#!/usr/bin/env python3
# Managed by elustondo.ai/asdlc; do not edit.
import os
import sys
from pathlib import Path
script = {script!r}
python = {python!r}
if not Path(script).is_file():
    sys.exit('ASDLC checkout moved or is unavailable; rerun ./asdg install from its new location.')
try:
    os.execv(python, [python, '-B', script, *sys.argv[1:]])
except OSError as exc:
    sys.exit('ASDLC interpreter unavailable; rerun ./asdg install: ' + str(exc))
"""
HISTORICAL_PATH_BLOCK = b'''# >>> Elustondo.ai ASDLC PATH >>>
case ":${PATH-}:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin${PATH:+:$PATH}" ;;
esac
# <<< Elustondo.ai ASDLC PATH <<<
'''
HISTORICAL_MANIFEST = Path('.config/elustondo-asdlc/installation.json')
PREFIX = '# developer setting: caf\u00e9\nexport EDITOR=vim\n\n'.encode('utf-8')
SUFFIX = b'\n# unrelated configuration\nexport KEEP_THIS=yes\n'


class MigrationTests(Fixture):
    def legacy_install(self, files=('.zprofile', '.zshrc')):
        """Recreate real legacy bytes without invoking the old launcher."""
        raw = HISTORICAL_LAUNCHER.format(
            script=str(self.provider / 'asdg'), python=str(Path(sys.executable))).encode()
        for name in ('elustondo-asdlc', 'asdg'):
            path = self.home / '.local/bin' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            path.chmod(0o755)
        record = {
            'provider': 'elustondo.ai/asdlc', 'cli_version': '0.1.3',
            'checkout': str(self.provider), 'python': str(Path(sys.executable)),
            'launcher_sha256': sha(raw), 'commands': ['elustondo-asdlc', 'asdg'],
            'shell_files': list(files), 'mode': 'linked-development-checkout',
        }
        path = self.home / HISTORICAL_MANIFEST
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(record, indent=2) + '\n')
        for relative in files:
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(PREFIX + HISTORICAL_PATH_BLOCK + SUFFIX)
        return raw, record

    def snapshot(self):
        return {str(p.relative_to(self.home)):
                (p.lstat().st_mode, p.read_bytes() if p.is_file() else None,
                 p.stat().st_mtime_ns if p.is_file() else None)
                for p in self.home.rglob('*')}

    def migrate(self, shell='/bin/zsh', zdotdir=''):
        return install(self.home, shell, str(self.home / '.local/bin') + ':' + self.env['PATH'],
                       self.provider, Path(sys.executable), zdotdir)

    def assert_refused_without_writes(self):
        before = self.snapshot()
        with self.assertRaises((Conflict, ValueError)):
            self.migrate()
        self.assertEqual(self.snapshot(), before)

    def test_real_legacy_upgrade_via_python_entry_point_and_repeat(self):
        old, _ = self.legacy_install()
        original_record = (self.home / HISTORICAL_MANIFEST).read_bytes()
        # Reproduces the rename: the former root entry point is now a directory.
        self.assertTrue((self.provider / 'asdg').is_dir())
        result = subprocess.run([sys.executable, 'bin/asdg', 'install'], cwd=self.provider,
                                env=dict(self.env, SHELL='/bin/zsh'),
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.home / '.local/bin/asdg').read_bytes(),
                         launcher(self.provider, Path(sys.executable)))
        self.assertEqual(self.run_cli('--version').returncode, 0)
        record = json.loads((self.home / MANIFEST).read_bytes())
        self.assertEqual(record['provider'], PROVIDER)
        self.assertEqual(record['commands'], ['asdg'])
        self.assertEqual(record['launcher_sha256'], sha((self.home / '.local/bin/asdg').read_bytes()))
        for relative in ('.zprofile', '.zshrc'):
            self.assertEqual((self.home / relative).read_bytes(), PREFIX + PATH_BLOCK.encode() + SUFFIX)
        backups = [p.read_bytes() for p in (self.home / '.config/asdg/backups').glob('*.before')]
        for original in (old, original_record, PREFIX + HISTORICAL_PATH_BLOCK + SUFFIX):
            self.assertIn(original, backups)
        self.assertEqual((self.home / HISTORICAL_MANIFEST).read_bytes(), original_record)
        self.assertEqual((self.home / '.local/bin/elustondo-asdlc').read_bytes(), old)
        before = self.snapshot()
        self.assertEqual(self.migrate()['files_changed'], [])
        self.assertEqual(self.snapshot(), before)

    def test_current_install_repeat_is_no_op(self):
        self.setup_install()
        before = self.snapshot()
        self.assertEqual(self.setup_install()['files_changed'], [])
        self.assertEqual(self.snapshot(), before)

    def test_changed_legacy_launcher_is_refused_and_never_executed(self):
        old, _ = self.legacy_install()
        sentinel = self.base / 'must-not-exist'
        path = self.home / '.local/bin/asdg'
        path.write_bytes(old + f'Path({str(sentinel)!r}).touch()\n'.encode())
        self.assert_refused_without_writes()
        self.assertFalse(sentinel.exists())

    def test_unrelated_launcher_with_matching_recorded_hash_is_refused(self):
        _, record = self.legacy_install()
        foreign = b'#!/usr/bin/env python3\nprint("unrelated")\n'
        (self.home / '.local/bin/asdg').write_bytes(foreign)
        record['launcher_sha256'] = sha(foreign)
        (self.home / HISTORICAL_MANIFEST).write_text(json.dumps(record))
        self.assert_refused_without_writes()

    def test_legacy_launcher_without_record_is_refused(self):
        self.legacy_install()
        (self.home / HISTORICAL_MANIFEST).unlink()
        self.assert_refused_without_writes()

    def test_stale_or_unrecognized_legacy_metadata_is_refused(self):
        _, record = self.legacy_install()
        cases = (
            {'launcher_sha256': '0' * 64}, {'provider': 'someone-else'},
            {'checkout': 'relative'}, {'python': 'python3'},
            {'commands': ['asdg']}, {'mode': 'unknown'}, {'cli_version': 'unknown'},
            {'shell_files': ['../.zshrc']}, {'shell_files': ['/tmp/.zshrc']},
            {'shell_files': ['.ssh/config']}, {'shell_files': []},
        )
        for values in cases:
            with self.subTest(values=values):
                (self.home / HISTORICAL_MANIFEST).write_text(json.dumps(dict(record, **values)))
                self.assert_refused_without_writes()

    def test_malformed_legacy_json_is_refused(self):
        self.legacy_install()
        (self.home / HISTORICAL_MANIFEST).write_text('{broken')
        self.assert_refused_without_writes()

    def test_current_record_conflict_cannot_fall_back_to_legacy(self):
        self.legacy_install()
        path = self.home / MANIFEST
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'provider': PROVIDER, 'launcher_sha256': '0' * 64}))
        self.assert_refused_without_writes()

    def test_foreign_current_record_cannot_fall_back_to_legacy(self):
        self.legacy_install()
        path = self.home / MANIFEST
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'provider': 'foreign'}))
        self.assert_refused_without_writes()

    def test_modified_current_launcher_is_refused_after_migration(self):
        self.legacy_install()
        self.migrate()
        path = self.home / '.local/bin/asdg'
        path.write_bytes(path.read_bytes() + b'# altered\n')
        self.assert_refused_without_writes()

    def test_known_old_and_new_blocks_collapse_without_touching_surroundings(self):
        self.legacy_install()
        path = self.home / '.zshrc'
        before = PREFIX + HISTORICAL_PATH_BLOCK + SUFFIX + PATH_BLOCK.encode()
        path.write_bytes(before)
        self.migrate()
        self.assertEqual(path.read_bytes(), PREFIX + SUFFIX + PATH_BLOCK.encode())
        self.assertIn(before, [p.read_bytes() for p in (self.home / '.config/asdg/backups').glob('*')])

    def test_edited_duplicate_or_incomplete_legacy_path_block_is_refused(self):
        self.legacy_install()
        for block in (HISTORICAL_PATH_BLOCK.replace(b'export PATH=', b'export OTHER='),
                      HISTORICAL_PATH_BLOCK * 2,
                      HISTORICAL_PATH_BLOCK.replace(b'# <<< Elustondo.ai ASDLC PATH <<<\n', b'')):
            with self.subTest(block=block):
                (self.home / '.zshrc').write_bytes(PREFIX + block + SUFFIX)
                self.assert_refused_without_writes()

    def test_recorded_shells_migrate_after_switching_to_bash(self):
        self.legacy_install()
        self.migrate('/bin/bash')
        for relative in ('.zshrc', '.zprofile', '.bash_profile', '.bashrc'):
            self.assertIn(PATH_BLOCK.encode(), (self.home / relative).read_bytes())
        self.assertEqual(self.migrate('/bin/bash')['files_changed'], [])

    def test_legacy_zdotdir_is_preserved(self):
        self.legacy_install(('shell settings/.zprofile', 'shell settings/.zshrc'))
        directory = self.home / 'shell settings'
        self.migrate(zdotdir=str(directory))
        self.assertEqual((directory / '.zshrc').read_bytes(), PREFIX + PATH_BLOCK.encode() + SUFFIX)
        self.assertFalse((self.home / '.zshrc').exists())
        self.assertEqual(self.migrate(zdotdir=str(directory))['files_changed'], [])

    def test_all_backups_exist_before_first_replacement(self):
        old, _ = self.legacy_install()
        required = {old, (self.home / HISTORICAL_MANIFEST).read_bytes(),
                    PREFIX + HISTORICAL_PATH_BLOCK + SUFFIX}
        def checked_replace(path, data, mode):
            backups = {p.read_bytes() for p in (self.home / '.config/asdg/backups').glob('*')}
            self.assertTrue(required <= backups)
            atomic_replace(path, data, mode)
        with patch('cli_files.atomic_replace', side_effect=checked_replace) as operation:
            self.migrate()
        self.assertTrue(operation.called)

    def test_backup_write_failure_leaves_managed_files_unchanged(self):
        import os
        self.legacy_install()
        before = self.snapshot()
        actual = os.open
        def fail_backup(path, *args, **kwargs):
            if str(path).endswith('.before'):
                raise OSError('simulated backup failure')
            return actual(path, *args, **kwargs)
        with patch('cli_files.os.open', side_effect=fail_backup), self.assertRaises(OSError):
            self.migrate()
        self.assertEqual(self.snapshot(), before)

    def test_symlinked_legacy_manifest_is_refused(self):
        self.legacy_install()
        path = self.home / HISTORICAL_MANIFEST
        outside = self.base / 'legacy-record.json'
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
        self.assert_refused_without_writes()


if __name__ == '__main__':
    import unittest
    unittest.main()
