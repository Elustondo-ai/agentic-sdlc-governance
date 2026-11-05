"""Test the actual ZIP boundary and install extracted clients without a provider."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

CORE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE / 'scripts'))
from build_distribution import build, refresh_manifest
from check import validate
from distribution_files import package_files


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.area = tempfile.TemporaryDirectory(prefix='asdg-zip-')
        self.addCleanup(self.area.cleanup)
        self.root = Path(self.area.name).resolve()
        self.core = self.root / 'provider/asdg'
        self.core.mkdir(parents=True)
        for source in package_files(CORE):
            target = self.core / source.relative_to(CORE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        refresh_manifest(self.core)

    def cli(self, root, *args):
        if args[0] == 'init' and '--apply' not in args and '--dry-run' not in args:
            preview = json.loads(self.cli(root, *args, '--dry-run', '--json'))
            args = (*args, '--apply', '--plan', preview['plan'])
        result = subprocess.run([sys.executable, '-B', str(root / 'asdg/scripts/cli.py'), *args],
                                cwd=root, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def rewrite_list(self, edit):
        file = self.core / 'metadata/package-files.json'
        data = json.loads(file.read_text())
        edit(data['files'])
        file.write_text(json.dumps(data))

    def test_zip_is_reproducible_and_excludes_unlisted_provider_files(self):
        private = self.core / 'provider-only.env'
        private.write_text('not a package member')
        (self.core / 'components').mkdir()
        (self.core / 'components/local.txt').write_text('retained provider tool')
        first = build(self.core, self.root / 'one')
        second = build(self.core, self.root / 'two')
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(archive.namelist(), ['asdg/' + p.relative_to(self.core).as_posix()
                                               for p in package_files(self.core)])
            self.assertNotIn('asdg/provider-only.env', archive.namelist())
            skill = 'skills/asdg-init/SKILL.md'
            self.assertEqual(archive.read('asdg/' + skill), (CORE / skill).read_bytes())
            for prompt in ('install-zip-prompt.md', 'install-clone-prompt.md'):
                self.assertEqual(archive.read('asdg/docs/' + prompt), (CORE / 'docs' / prompt).read_bytes())
        self.assertTrue(first.with_suffix('.zip.sha256').read_text().startswith(
            hashlib.sha256(first.read_bytes()).hexdigest()))

    def test_stale_bytes_fail_before_artifact_is_written(self):
        (self.core / 'README.md').write_text('Changed candidate\n')
        output = self.root / 'rejected'
        with self.assertRaisesRegex(ValueError, 'manifest differs'):
            build(self.core, output)
        self.assertFalse(output.exists())

    def test_missing_selected_file_is_rejected(self):
        (self.core / 'scripts/init.py').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing package file'):
            package_files(self.core)

    def test_traversal_and_duplicate_entries_are_rejected(self):
        index = self.core / 'metadata/package-files.json'
        original = index.read_bytes()
        for name in ('../outside', '/tmp/outside', 'scripts/../../outside', '.git/config', 'metadata/sync-state.json'):
            with self.subTest(name=name):
                self.rewrite_list(lambda files: files.append(name))
                with self.assertRaisesRegex(ValueError, 'Unsafe package path'):
                    package_files(self.core)
                index.write_bytes(original)
        self.rewrite_list(lambda files: files.append('README.md'))
        with self.assertRaisesRegex(ValueError, 'unique'):
            package_files(self.core)

    def test_symlink_member_is_rejected(self):
        path = self.core / 'README.md'
        original = path.read_text()
        path.unlink()
        other = self.root / 'outside.md'
        other.write_text(original)
        path.symlink_to(other)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            package_files(self.core)

    def test_links_to_unshipped_files_are_rejected(self):
        (self.core / 'provider-only.md').write_text('Not shipped.\n')
        with (self.core / 'README.md').open('a') as stream:
            stream.write('\n[Local dependency](provider-only.md)\n')
        self.assertTrue(any('Link missing from package' in issue for issue in validate(self.core)))

    def test_zip_installs_and_relocates_all_client_choices(self):
        archive = build(self.core, self.root / 'output')
        for choice in ('codex', 'claude', 'both'):
            with self.subTest(client=choice):
                client = self.root / (choice + ' fresh client')
                client.mkdir()
                subprocess.run(['git', 'init', '-q', str(client)], check=True)
                (client / 'app.py').write_text('print("existing app")\n')
                (client / 'AGENTS.md').write_text('# Existing project guidance\n\nPreserve this guidance.\n')
                with zipfile.ZipFile(archive) as zipped:
                    zipped.extractall(client)
                self.cli(client, 'init', '--client', choice)
                report = json.loads(self.cli(client, 'verify', '--json'))
                self.assertTrue(report['structure_ok'])
                self.assertEqual((client / '.codex/hooks.json').exists(), choice != 'claude')
                self.assertEqual((client / '.claude/skills').exists(), choice != 'codex')
                self.assertIn('Preserve this guidance.', (client / 'AGENTS.md').read_text())
                snapshot = {p.relative_to(client): p.read_bytes() for p in client.rglob('*')
                            if p.is_file() and '.git' not in p.relative_to(client).parts}
                moved = client.rename(self.root / (choice + " moved client's repo"))
                repeat = json.loads(self.cli(moved, 'init', '--client', choice, '--json'))
                self.assertEqual(repeat['changed_files'], [])
                after = {p.relative_to(moved): p.read_bytes() for p in moved.rglob('*')
                         if p.is_file() and '.git' not in p.relative_to(moved).parts}
                self.assertEqual(snapshot, after)
                self.assertTrue(json.loads(self.cli(moved, 'verify', '--json'))['structure_ok'])


if __name__ == '__main__':
    unittest.main()
