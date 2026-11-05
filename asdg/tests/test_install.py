"""ZIP and pinned-clone installations use one engine in disposable Git projects."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

CORE = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(CORE / 'scripts/lib'))
from cli_files import Conflict
from cli_install import install
from distribution_files import package_files


def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
            if p.is_file() and '.git' not in p.relative_to(root).parts}


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args]).decode().strip()


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.area = tempfile.TemporaryDirectory(prefix='asdg-two-paths-')
        self.addCleanup(self.area.cleanup)
        self.root = Path(self.area.name).resolve()
        self.source = self.root / 'canonical clone'
        self.source.mkdir()
        git(self.source, 'init', '-q')
        git(self.source, 'remote', 'add', 'origin', 'https://github.com/Elustondo-ai/agentic-sdlc-governance.git')
        for p in package_files(CORE):
            target = self.source / 'asdg' / p.relative_to(CORE)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(p.read_bytes())
        self.seal()
        # Deliberately commit provider-only material, including an unselected adapter.
        for name in ('private.txt', '.asdg/private.json', 'docs/asdg/private.md',
                     'asdg/components/private.txt', 'asdg/templates/.agents/skills/private/SKILL.md'):
            p = self.source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('Provider-only work.\n')
        self.commit = self.save()
        self.target = self.root / 'existing application'
        self.target.mkdir()
        git(self.target, 'init', '-q')
        (self.target / 'app.py').write_text('print("existing application")\n')
        (self.target / 'AGENTS.md').write_text('# Project instructions\n\nKeep application behavior.\n')
        p = self.target / 'docs/asdg/01-context-and-domain-analysis/notes.md'
        p.parent.mkdir(parents=True)
        p.write_text('Existing Context evidence; preserve it.\n')

    def seal(self):
        core = self.source / 'asdg'
        path = core / 'metadata/MANIFEST.json'
        value = json.loads(path.read_text())
        value['files'] = {p.relative_to(core).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in package_files(core) if p != path}
        path.write_text(json.dumps(value) + '\n')

    def save(self):
        git(self.source, 'add', '.')
        git(self.source, '-c', 'user.name=Disposable test', '-c', 'user.email=test@example.invalid',
            'commit', '-qm', 'Disposable test package')
        return git(self.source, 'rev-parse', 'HEAD')

    def invoke(self, route='clone', client='codex', **kw):
        options = dict(target=str(self.target), client=client)
        if route == 'clone':
            options.update(source=str(self.source), commit=self.commit, repo=self.source)
        else:
            options['repo'] = self.target
        options.update(kw)
        return install(**options)

    def extract(self):
        # Reproduce the single-folder ZIP boundary; no provider tree is extracted.
        archive = self.root / 'candidate.zip'
        with zipfile.ZipFile(archive, 'w') as stream:
            for p in package_files(self.source / 'asdg'):
                stream.write(p, 'asdg/' + p.relative_to(self.source / 'asdg').as_posix())
        with zipfile.ZipFile(archive) as stream:
            stream.extractall(self.target)

    def test_both_routes_both_clients_preview_apply_verify_and_repeat(self):
        for route in ('zip', 'clone'):
            for client in ('claude', 'codex'):
                with self.subTest(route=route, client=client):
                    original = tree(self.target)
                    if route == 'zip':
                        self.extract()
                    before = tree(self.target)
                    source_before = tree(self.source)
                    preview = self.invoke(route, client)
                    self.assertEqual(before, tree(self.target))
                    self.assertFalse(preview['installation_complete'])
                    self.assertFalse(preview['context_survey']['offered'])
                    # Approval summary inputs must describe actual pending writes, not fixture guesses.
                    self.assertEqual(preview['project_root'], str(self.target))
                    self.assertEqual(preview['clients_applied'], [client])
                    metadata = json.loads((self.source / 'asdg/metadata/distribution.json').read_text())
                    self.assertEqual(preview['source']['version'], metadata['version'])
                    self.assertEqual(preview['source']['integrity'], 'MANIFEST_MATCHED')
                    pending = [row for row in preview['files'] if row['action'] != 'unchanged']
                    self.assertEqual({row['path'] for row in pending}, set(preview['planned_files']))
                    for row in pending:
                        existed = row['path'] in before
                        self.assertEqual(row['action'], 'modified' if existed else 'added')
                        if existed:
                            self.assertEqual(row['before_sha256'], hashlib.sha256(before[row['path']]).hexdigest())
                            self.assertTrue(row['diff'])
                    # The full JSON can be retained outside the target without preview writes.
                    with tempfile.NamedTemporaryFile(mode='w+', dir=self.root, suffix='.json') as saved:
                        json.dump(preview, saved)
                        saved.flush()
                        saved.seek(0)
                        self.assertEqual(json.load(saved), preview)
                    self.assertEqual(before, tree(self.target))
                    installed = self.invoke(route, client, apply_changes=True, expected_plan=preview['plan'])
                    self.assertTrue(installed['installation_complete'])
                    skill = Path('asdg/skills/asdg-init/SKILL.md')
                    self.assertEqual((self.target / skill).read_bytes(), (CORE.parent / skill).read_bytes())
                    self.assertTrue(installed['verification']['structure_ok'])
                    self.assertFalse(installed['context_survey']['executed'])
                    self.assertTrue(installed['context_survey']['requires_separate_affirmative'])
                    self.assertEqual(installed['native_runtime_enforcement'], 'NOT_VERIFIED')
                    self.assertEqual(installed['verification']['sprint_state']['status'], 'inactive')
                    for name in ('app.py', 'docs/asdg/01-context-and-domain-analysis/notes.md'):
                        self.assertEqual(original[name], tree(self.target)[name])
                    self.assertIn(original['AGENTS.md'], (self.target / 'AGENTS.md').read_bytes())
                    self.assertEqual((self.target / '.codex/hooks.json').exists(), client == 'codex')
                    self.assertEqual((self.target / '.claude/skills').exists(), client == 'claude')
                    self.assertFalse((self.target / 'asdg/.git').exists())
                    for name in ('private.txt', '.asdg/private.json', 'docs/asdg/private.md',
                                 'asdg/components/private.txt', '.agents/skills/private/SKILL.md'):
                        self.assertFalse((self.target / name).exists(), name)
                    adopted = json.loads((self.target / '.asdg/project.json').read_text())
                    self.assertEqual(adopted['methodology_revision_at_init'], self.commit if route == 'clone' else None)
                    after = tree(self.target)
                    preview = self.invoke(route, client)
                    self.assertEqual(preview['planned_files'], [])
                    self.assertEqual(self.invoke(route, client, apply_changes=True,
                                                 expected_plan=preview['plan'])['changed_files'], [])
                    self.assertEqual(after, tree(self.target))
                    self.assertEqual(source_before, tree(self.source))
                    # Reset only this test's disposable target, preserving its empty Git repository.
                    for p in self.target.iterdir():
                        if p.name != '.git':
                            shutil.rmtree(p) if p.is_dir() else p.unlink()
                    for name, data in original.items():
                        p = self.target / name
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_bytes(data)

    def test_cli_default_is_preview_and_apply_needs_review_token(self):
        command = [sys.executable, '-B', str(self.source / 'asdg/scripts/init.py'),
                   '--source', str(self.source), '--commit', self.commit,
                   '--target', str(self.target), '--client', 'claude', '--json']
        before = tree(self.target)
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        preview = json.loads(result.stdout)
        self.assertEqual(tree(self.target), before)
        result = subprocess.run(command + ['--apply'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(tree(self.target), before)
        result = subprocess.run(command + ['--apply', '--plan', preview['plan']], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['installation_complete'])

    def test_invalid_commit_identity_and_paths_do_not_write(self):
        before = tree(self.target)
        for options in ({'commit': 'main'}, {'commit': '0' * 40}, {'commit': None},
                        {'target': str(self.root)}, {'target': str(self.root / 'absent')},
                        {'target': str(self.source)}):
            with self.subTest(options=options), self.assertRaises((Conflict, FileNotFoundError)):
                self.invoke(**options)
            self.assertEqual(tree(self.target), before)
        git(self.source, 'remote', 'set-url', 'origin', 'https://github.com/other/repo.git')
        with self.assertRaisesRegex(Conflict, 'canonical'):
            self.invoke()

    def test_stale_zip_and_dirty_selected_clone_bytes_fail(self):
        path = self.source / 'asdg/README.md'
        path.write_text(path.read_text() + '\nUncommitted change.\n')
        self.extract()
        before = tree(self.target)
        for route in ('clone', 'zip'):
            with self.assertRaisesRegex(Conflict, 'manifest is stale'):
                self.invoke(route)
        self.assertEqual(tree(self.target), before)
        self.seal()
        with self.assertRaisesRegex(Conflict, 'does not match source commit'):
            self.invoke()

    def test_stale_plan_client_change_and_collisions_preserve_target(self):
        preview = self.invoke()
        with self.assertRaisesRegex(Conflict, 'plan changed'):
            self.invoke(client='claude', apply_changes=True, expected_plan=preview['plan'])
        (self.target / 'AGENTS.md').write_text('Changed after preview.\n')
        before = tree(self.target)
        with self.assertRaisesRegex(Conflict, 'plan changed'):
            self.invoke(apply_changes=True, expected_plan=preview['plan'])
        self.assertEqual(tree(self.target), before)
        conflict = self.target / '.codex/hooks.json'
        conflict.parent.mkdir()
        conflict.write_text('{"custom": true}\n')
        before = tree(self.target)
        with self.assertRaisesRegex(Conflict, 'Refusing to overwrite'):
            self.invoke()
        self.assertEqual(tree(self.target), before)

    def test_failed_verification_rolls_back_distribution_and_integrations(self):
        preview = self.invoke()
        before = tree(self.target)
        with patch('cli_install.inspect', return_value={'structure_ok': False, 'missing': ['injected failure']}):
            with self.assertRaisesRegex(Conflict, 'Post-install verification failed'):
                self.invoke(apply_changes=True, expected_plan=preview['plan'])
        self.assertEqual(tree(self.target), before)
        self.assertFalse((self.target / 'asdg').exists())
        self.assertFalse((self.target / '.asdg').exists())

    def test_unchosen_provider_work_does_not_change_verified_package(self):
        (self.source / 'private.txt').write_text('Uncommitted provider-only work.\n')
        preview = self.invoke()
        self.assertEqual(preview['source']['commit'], self.commit)
        self.assertEqual(preview['source']['release_approval'], 'NOT_ESTABLISHED')

    def test_interrupted_package_write_removes_partial_file_and_previous_additions(self):
        preview = self.invoke()
        before = tree(self.target)
        original = os.fdopen
        opened = [0]

        class Interrupted:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.stream.close()
            def write(self, data):
                self.stream.write(data[:13])
                self.stream.flush()
                raise OSError('injected interrupted package write')

        def interrupt(fd, *args, **kwargs):
            stream = original(fd, *args, **kwargs)
            opened[0] += 1
            return Interrupted(stream) if opened[0] == 3 else stream

        with patch('cli_files.os.fdopen', side_effect=interrupt):
            with self.assertRaisesRegex(OSError, 'interrupted package write'):
                self.invoke(apply_changes=True, expected_plan=preview['plan'])
        self.assertEqual(tree(self.target), before)
        self.assertFalse((self.target / 'asdg').exists())

    def test_source_change_after_preview_requires_another_review(self):
        preview = self.invoke()
        path = self.source / 'asdg/README.md'
        path.write_text(path.read_text() + '\nNew reviewed fixture content.\n')
        self.seal()
        self.commit = self.save()
        before = tree(self.target)
        with self.assertRaisesRegex(Conflict, 'plan changed'):
            self.invoke(apply_changes=True, expected_plan=preview['plan'])
        self.assertEqual(tree(self.target), before)

    def test_symlink_and_distribution_collision_fail_without_writes(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.target / 'asdg').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(Conflict, 'symlink'):
            self.invoke()
        self.assertEqual(list(outside.iterdir()), [])
        (self.target / 'asdg').unlink()
        collision = self.target / 'asdg/README.md'
        collision.parent.mkdir()
        collision.write_text('Existing project work.\n')
        before = tree(self.target)
        with self.assertRaisesRegex(Conflict, 'Refusing to overwrite'):
            self.invoke()
        self.assertEqual(tree(self.target), before)

    def test_fixed_clock_yields_identical_preview(self):
        with patch('cli_install.now', return_value='2026-11-04T12:00:00Z'):
            self.assertEqual(self.invoke(), self.invoke())


if __name__ == '__main__':
    unittest.main()
