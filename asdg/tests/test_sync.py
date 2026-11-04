"""Local promote/upgrade integration tests in disposable Git repositories."""
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

CORE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE / 'scripts/lib'))
from cli_files import Conflict
from cli_sync import synchronize
from cli_sync_manifest import DESCRIPTOR, INDEX, MANIFEST, STATE, digest, encoded

CANONICAL = 'https://example.test/team/asdg.git'
PILOT = 'git@example.test:team/pilot.git'


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout


def tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*')
            if p.is_file() and '.git' not in p.relative_to(root).parts}


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='asdg-sync-')
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name).resolve()
        self.canonical, self.pilot = self.area / 'canonical', self.area / "pilot's project"
        for root, origin in ((self.canonical, CANONICAL), (self.pilot, PILOT)):
            root.mkdir()
            git(root, 'init', '-q')
            git(root, 'config', 'user.name', 'Fixture')
            git(root, 'config', 'user.email', 'fixture@example.test')
            git(root, 'remote', 'add', 'origin', origin)
            core = root / 'asdg'
            (core / 'metadata').mkdir(parents=True)
            (core / 'docs').mkdir()
            (core / '00-governance/types').mkdir(parents=True)
            (core / 'README.md').write_text('# Test distribution\n')
            (core / 'docs/a.md').write_text('Baseline A\n')
            (core / 'docs/b.md').write_text('Baseline B\n')
            (core / '00-governance/types/agent-catalog.json').write_bytes(
                (CORE / '00-governance/types/agent-catalog.json').read_bytes())
            (core / DESCRIPTOR).write_bytes(encoded({'schema_version': 1, 'provider': 'elustondo.ai/asdg',
                'version': '1.0.0', 'installation_mode': 'embedded-distribution', 'canonical_repository': CANONICAL}))
            names = ['README.md', 'docs/a.md', 'docs/b.md', '00-governance/types/agent-catalog.json', DESCRIPTOR, INDEX, MANIFEST]
            (core / INDEX).write_bytes(encoded({'schema_version': 1, 'files': names}))
            self.refresh(root)
            (root / 'app.py').write_text('print("client application")\n')
            (root / 'docs/asdg/02-purpose').mkdir(parents=True)
            (root / 'docs/asdg/02-purpose/purpose.md').write_text('Project-specific evidence\n')
            (root / '.asdg').mkdir()
            if root == self.pilot:
                (root / '.asdg/project.json').write_bytes(encoded({'schema_version': 1, 'provider': 'elustondo.ai/asdg',
                    'project_id': 'fixture', 'distribution_version': '1.0.0', 'distribution_root': 'asdg',
                    'artifacts_root': 'docs/asdg', 'installation_mode': 'embedded-distribution'}))
            (root / '.asdg/sprint.json').write_text('{"fixture":"preserve"}\n')
            self.commit(root)
        # Identical manifests establish the first shared baseline.

    def commit(self, root):
        git(root, 'add', '.')
        git(root, 'commit', '-qm', 'fixture', '--allow-empty')

    def refresh(self, root):
        core = root / 'asdg'
        manifest = core / MANIFEST
        if manifest.exists():
            previous = manifest.read_bytes()
            archive = core / 'metadata/deliveries' / (hashlib.sha256(previous).hexdigest() + '.json')
            archive.parent.mkdir(exist_ok=True)
            archive.write_bytes(previous)
        names = json.loads((core / INDEX).read_text())['files']
        version = json.loads((core / DESCRIPTOR).read_text())['version']
        manifest.write_bytes(encoded({'schema_version': 1, 'version': version,
            'files': {p: digest((core / p).read_bytes()) for p in names if p != MANIFEST}}))

    def edit(self, root, name, data):
        core = root / 'asdg'
        path = core / name
        listing = json.loads((core / INDEX).read_text())
        if data is None:
            path.unlink()
            listing['files'].remove(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data)
            if name not in listing['files']:
                listing['files'].append(name)
        (core / INDEX).write_bytes(encoded(listing))
        self.refresh(root)

    def preview(self, operation='promote'):
        a, b = (self.pilot, self.canonical) if operation == 'promote' else (self.canonical, self.pilot)
        return synchronize(operation, a, b)

    def apply(self, operation='promote'):
        a, b = (self.pilot, self.canonical) if operation == 'promote' else (self.canonical, self.pilot)
        report = self.preview(operation)
        return synchronize(operation, a, b, apply=True, expected_plan=report['plan_id'])

    def row(self, report, name):
        return next(r for r in report['files'] if r['path'] == 'asdg/' + name)

    def test_identical_and_repeated_execution(self):
        report = self.preview()
        self.assertEqual(report['counts']['conflicting'], 0)
        self.assertTrue(all(r['status'] == 'unchanged' for r in report['files']))
        self.apply()
        before = tree(self.canonical)
        self.assertEqual(self.apply()['written_files'], [])
        self.assertEqual(tree(self.canonical), before)

    def test_new_files_both_directions(self):
        for operation, source, target in [('promote', self.pilot, self.canonical), ('upgrade', self.canonical, self.pilot)]:
            with self.subTest(operation=operation):
                name = 'docs/new-' + operation + '.md'
                self.edit(source, name, 'New methodology\n')
                self.assertEqual(self.row(self.preview(operation), name)['status'], 'added')
                self.apply(operation)
                self.assertEqual((target / 'asdg' / name).read_text(), 'New methodology\n')

    def test_updated_file(self):
        self.edit(self.pilot, 'docs/a.md', 'Improved A\n')
        self.assertEqual(self.row(self.preview(), 'docs/a.md')['status'], 'modified')
        self.apply()
        self.assertEqual((self.canonical / 'asdg/docs/a.md').read_text(), 'Improved A\n')

    def test_deleted_tracked_file(self):
        self.edit(self.pilot, 'docs/a.md', None)
        self.assertEqual(self.row(self.preview(), 'docs/a.md')['status'], 'deleted')
        self.apply()
        self.assertFalse((self.canonical / 'asdg/docs/a.md').exists())

    def test_local_only_changes_are_preserved_and_later_conflict(self):
        (self.canonical / 'asdg/docs/a.md').write_text('Local adaptation\n')
        self.edit(self.pilot, 'docs/b.md', 'Upstream B\n')
        self.assertEqual(self.row(self.preview(), 'docs/a.md')['reason'], 'local change retained')
        self.apply()
        self.assertEqual((self.canonical / 'asdg/docs/a.md').read_text(), 'Local adaptation\n')
        self.edit(self.pilot, 'docs/a.md', 'Upstream A\n')
        self.assertEqual(self.row(self.preview(), 'docs/a.md')['status'], 'conflicting')

    def test_conflicting_modifications_block_all_writes(self):
        (self.canonical / 'asdg/docs/a.md').write_text('Target A\n')
        self.edit(self.pilot, 'docs/a.md', 'Source A\n')
        self.edit(self.pilot, 'docs/new.md', 'Safe addition\n')
        before = tree(self.canonical)
        with self.assertRaisesRegex(Conflict, 'Conflicting files'):
            self.apply()
        self.assertEqual(tree(self.canonical), before)

    def test_delete_modify_conflict_and_untracked_deletion(self):
        self.edit(self.pilot, 'docs/a.md', None)
        (self.canonical / 'asdg/docs/a.md').write_text('Local A\n')
        self.assertEqual(self.row(self.preview(), 'docs/a.md')['status'], 'conflicting')
        (self.canonical / 'asdg/docs/a.md').write_text('Baseline A\n')
        git(self.canonical, 'rm', '--cached', 'asdg/docs/a.md')
        self.assertEqual(self.row(self.preview(), 'docs/a.md')['reason'], 'refusing to delete untracked work')

    def test_unlisted_untracked_collision_is_not_overwritten(self):
        (self.canonical / 'asdg/docs/extra.md').write_text('Untracked work\n')
        self.edit(self.pilot, 'docs/extra.md', 'Incoming\n')
        self.assertEqual(self.row(self.preview(), 'docs/extra.md')['status'], 'conflicting')

    def test_dry_run_changes_neither_tree_nor_git_index(self):
        self.edit(self.pilot, 'docs/a.md', 'Incoming\n')
        before = [(tree(p), (p / '.git/index').read_bytes()) for p in (self.pilot, self.canonical)]
        self.preview()
        self.assertEqual(before, [(tree(p), (p / '.git/index').read_bytes()) for p in (self.pilot, self.canonical)])

    def test_app_and_project_state_are_preserved(self):
        self.edit(self.canonical, 'docs/a.md', 'Upgrade\n')
        protected = {p: data for p, data in tree(self.pilot).items() if not p.startswith('asdg/')}
        self.apply('upgrade')
        self.assertEqual(protected, {p: data for p, data in tree(self.pilot).items() if not p.startswith('asdg/')})

    def test_missing_invalid_and_nested_paths(self):
        nongit = self.area / 'nongit'; nongit.mkdir()
        for source in (self.area / 'missing', nongit, self.pilot / 'asdg', self.canonical):
            with self.subTest(source=source), self.assertRaises((Conflict, OSError)):
                synchronize('promote', source, self.canonical)

    def test_identity_version_and_binding_fail_closed(self):
        git(self.canonical, 'remote', 'set-url', 'origin', 'https://example.test/wrong/repo.git')
        with self.assertRaisesRegex(Conflict, 'Canonical repository'):
            self.preview()
        git(self.canonical, 'remote', 'set-url', 'origin', CANONICAL)
        descriptor = self.pilot / 'asdg' / DESCRIPTOR
        original = descriptor.read_bytes()
        descriptor.write_text('{}')
        with self.assertRaisesRegex(Conflict, 'source version'):
            self.preview()
        descriptor.write_bytes(original)
        (self.pilot / '.asdg/project.json').unlink()
        with self.assertRaisesRegex(Conflict, 'binding'):
            self.preview()

    def test_symlinks_and_escaping_manifest_are_rejected(self):
        path = self.canonical / 'asdg/docs/a.md'
        path.unlink(); path.symlink_to(self.pilot / 'app.py')
        with self.assertRaisesRegex(Conflict, 'symlink'):
            self.preview()
        path.unlink(); path.write_text('Baseline A\n')
        index = self.pilot / 'asdg' / INDEX
        value = json.loads(index.read_text()); value['files'].append('../app.py')
        index.write_bytes(encoded(value))
        with self.assertRaisesRegex(Conflict, 'scope'):
            self.preview()

    def test_apply_requires_reviewed_and_current_digest(self):
        with self.assertRaisesRegex(Conflict, '--plan'):
            synchronize('promote', self.pilot, self.canonical, apply=True)
        review = self.preview()
        (self.pilot / 'asdg/docs/a.md').write_text('Later edit\n')
        with self.assertRaisesRegex(Conflict, '--plan'):
            synchronize('promote', self.pilot, self.canonical, apply=True, expected_plan=review['plan_id'])

    def test_upgrade_requires_current_canonical_manifest(self):
        (self.canonical / 'asdg/docs/a.md').write_text('Unpackaged work\n')
        review = self.preview('upgrade')
        self.assertFalse(review['source']['manifest_matches_worktree'])
        with self.assertRaisesRegex(Conflict, 'versioned manifest'):
            self.apply('upgrade')

    def test_manifest_freshness_is_explicit_without_claiming_validation_or_approval(self):
        from cli_sync import render
        original = self.preview()['source']
        self.assertEqual(original['snapshot_kind'], 'MANIFEST_MATCHED_DISTRIBUTION')
        self.assertEqual(original['delivery_manifest']['status'], 'MATCH')
        self.assertEqual(original['validation_status'], 'NOT_ESTABLISHED')
        self.assertEqual(original['human_approval_status'], 'NOT_ESTABLISHED')
        (self.pilot / 'asdg/docs/a.md').write_text('Unpackaged pilot edit\n')
        report = self.preview()
        source = report['source']
        self.assertEqual(source['snapshot_kind'], 'WORKING_TREE_SNAPSHOT')
        self.assertEqual(source['delivery_manifest']['status'], 'STALE')
        self.assertEqual(source['delivery_manifest']['differences'], {'added': [], 'modified': ['docs/a.md'], 'deleted': []})
        self.assertEqual(source['delivery_manifest']['sha256'], original['delivery_manifest']['sha256'])
        self.assertIn('WORKING_TREE_SNAPSHOT; delivery manifest: STALE', render(report))
        self.apply()
        receipt = json.loads((self.canonical / 'asdg' / STATE).read_text())['upstreams']['example.test/team/pilot']
        self.assertEqual(receipt['source_snapshot_kind'], 'WORKING_TREE_SNAPSHOT')
        self.assertEqual(receipt['source_delivery_manifest'], source['delivery_manifest'])
        self.assertEqual(receipt['human_approval_status'], 'NOT_ESTABLISHED')

    def test_rollback_restores_deleted_files_on_write_failure(self):
        self.edit(self.pilot, 'docs/a.md', None)
        self.edit(self.pilot, 'docs/b.md', 'New B\n')
        before = tree(self.canonical)
        import cli_files
        original = cli_files.atomic_replace
        failed = False
        def failing(path, data, mode):
            nonlocal failed
            if path.name == 'b.md' and not failed:
                failed = True
                raise OSError('injected failure')
            return original(path, data, mode)
        with patch('cli_files.atomic_replace', side_effect=failing), self.assertRaises(OSError):
            self.apply()
        self.assertEqual(tree(self.canonical), before)

    def interrupted_new_file(self, *, replace_path=False):
        self.edit(self.pilot, 'docs/a.md', 'Earlier successful change\n')
        self.edit(self.pilot, 'docs/new/partial.md', 'Complete incoming content\n')
        target = self.canonical / 'asdg/docs/new/partial.md'
        before = tree(self.canonical)
        original = os.fdopen
        class InterruptedStream:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.stream.close()
            def write(self, data):
                self.stream.write(data[:4])
                self.stream.flush()
                if replace_path:
                    # A different inode at the same path is not this transaction's file.
                    target.unlink()
                    target.write_bytes(b'Unrelated replacement\n')
                raise KeyboardInterrupt('injected interrupted write')
        def interrupted(fd, *args, **kwargs):
            owned = target.exists() and os.path.samestat(os.fstat(fd), target.stat())
            stream = original(fd, *args, **kwargs)
            return InterruptedStream(stream) if owned else stream
        with patch('cli_files.os.fdopen', side_effect=interrupted), self.assertRaises(KeyboardInterrupt):
            self.apply()
        return target, before

    def test_interrupted_new_file_write_removes_partial_file_and_restores_prior_changes(self):
        target, before = self.interrupted_new_file()
        self.assertFalse(target.exists())
        self.assertFalse(target.parent.exists())
        self.assertEqual(tree(self.canonical), before)

    def test_interrupted_new_file_write_preserves_replacement_inode(self):
        target, before = self.interrupted_new_file(replace_path=True)
        self.assertEqual(target.read_bytes(), b'Unrelated replacement\n')
        before[str(target.relative_to(self.canonical))] = b'Unrelated replacement\n'
        self.assertEqual(tree(self.canonical), before)

    def test_new_file_stream_setup_failure_closes_descriptor_and_removes_file(self):
        self.edit(self.pilot, 'docs/new/partial.md', 'Complete incoming content\n')
        target = self.canonical / 'asdg/docs/new/partial.md'
        before, descriptors = tree(self.canonical), []
        original = os.fdopen
        def failing(fd, *args, **kwargs):
            if target.exists() and os.path.samestat(os.fstat(fd), target.stat()):
                descriptors.append(fd)
                raise OSError('injected stream setup failure')
            return original(fd, *args, **kwargs)
        with patch('cli_files.os.fdopen', side_effect=failing), self.assertRaisesRegex(OSError, 'stream setup'):
            self.apply()
        self.assertEqual(tree(self.canonical), before)
        self.assertEqual(len(descriptors), 1)
        with self.assertRaises(OSError):
            os.fstat(descriptors[0])

    def test_new_file_creation_failure_restores_earlier_writes(self):
        self.edit(self.pilot, 'docs/a.md', 'Earlier successful change\n')
        self.edit(self.pilot, 'docs/new/partial.md', 'Complete incoming content\n')
        before = tree(self.canonical)
        original = os.open
        def failing(path, flags, *args, **kwargs):
            if str(path).endswith('/docs/new/partial.md'):
                raise OSError('injected creation failure')
            return original(path, flags, *args, **kwargs)
        with patch('cli_files.os.open', side_effect=failing), self.assertRaisesRegex(OSError, 'creation failure'):
            self.apply()
        self.assertEqual(tree(self.canonical), before)

    def test_legacy_tracked_pilot_and_shared_delivery(self):
        original = (self.pilot / 'asdg' / MANIFEST).read_bytes()
        (self.pilot / 'asdg' / INDEX).unlink()
        git(self.pilot, 'rm', '--cached', 'asdg/' + INDEX)
        (self.pilot / 'asdg/docs/new.md').write_text('Versioned pilot addition\n')
        git(self.pilot, 'add', 'asdg/docs/new.md')
        (self.pilot / 'asdg/docs/private-untracked.md').write_text('Never selected\n')
        self.assertEqual(self.preview()['source']['selection'], 'legacy-git-tracked')
        self.assertEqual(self.row(self.preview(), 'docs/new.md')['status'], 'added')
        self.assertFalse(any('private-untracked' in r['path'] for r in self.preview()['files']))
        self.assertEqual((self.pilot / 'asdg' / MANIFEST).read_bytes(), original)

    def test_cli_both_directions_and_explicit_mode(self):
        for operation, a, b in [('promote', self.pilot, self.canonical), ('upgrade', self.canonical, self.pilot)]:
            args = [sys.executable, '-B', str(CORE / 'scripts/cli.py'), operation, '--source', str(a), '--target', str(b)]
            result = subprocess.run(args + ['--dry-run', '--json'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['operation'], operation)
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_missing_origin_corrupt_receipt_and_malformed_catalogue(self):
        git(self.pilot, 'remote', 'remove', 'origin')
        with self.assertRaisesRegex(Conflict, 'identity'):
            self.preview()
        git(self.pilot, 'remote', 'add', 'origin', PILOT)
        self.apply()
        state = self.canonical / 'asdg' / STATE
        original = state.read_bytes()
        value = json.loads(original)
        next(iter(value['upstreams'].values()))['snapshot_sha256'] = '0' * 64
        state.write_bytes(encoded(value))
        with self.assertRaisesRegex(Conflict, 'snapshot hash'):
            self.preview()
        state.write_bytes(original)
        catalog = self.pilot / 'asdg/00-governance/types/agent-catalog.json'
        catalog.write_text('{"agents":[null]}')
        with self.assertRaisesRegex(Conflict, 'lifecycle identities'):
            self.preview()

    def test_no_shared_baseline_keeps_equal_files_and_blocks_differences(self):
        self.edit(self.pilot, 'docs/a.md', 'Pilot variant\n')
        self.edit(self.canonical, 'docs/b.md', 'Canonical variant\n')
        for root in (self.pilot, self.canonical):
            shutil.rmtree(root / 'asdg/metadata/deliveries')
        report = self.preview()
        self.assertTrue(report['baseline'].startswith('none:'))
        self.assertEqual(self.row(report, 'README.md')['status'], 'unchanged')
        self.assertEqual(self.row(report, 'docs/a.md')['status'], 'conflicting')
        self.assertEqual(self.row(report, 'docs/b.md')['status'], 'conflicting')

    def test_multiple_shared_archives_do_not_guess_ancestry(self):
        for root in (self.pilot, self.canonical):
            self.edit(root, 'docs/a.md', 'Second shared version\n')
        self.edit(self.pilot, 'docs/a.md', 'Pilot variant\n')
        self.edit(self.canonical, 'docs/b.md', 'Canonical variant\n')
        report = self.preview()
        self.assertIn('multiple shared historical', report['baseline'])
        self.assertEqual(self.row(report, 'docs/a.md')['status'], 'conflicting')

    def test_real_portable_runtime_recognizes_upgrade_without_changing_project_state(self):
        from distribution_files import package_files
        for root in (self.canonical, self.pilot):
            shutil.rmtree(root / 'asdg')
            shutil.rmtree(root / '.asdg')
            for source in package_files(CORE):
                target = root / 'asdg' / source.relative_to(CORE)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            descriptor = root / 'asdg' / DESCRIPTOR
            value = json.loads(descriptor.read_text())
            value['canonical_repository'] = CANONICAL
            descriptor.write_bytes(encoded(value))
            self.refresh(root)
        command = [sys.executable, '-B', str(self.pilot / 'asdg/scripts/cli.py')]
        def run(*args):
            result = subprocess.run(command + list(args) + ['--json'], cwd=self.pilot,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)
        preview = run('init', '--client', 'both', '--dry-run')
        run('init', '--client', 'both', '--apply', '--plan', preview['plan'])
        for root in (self.canonical, self.pilot):
            self.commit(root)
        before = {p: b for p, b in tree(self.pilot).items() if not p.startswith('asdg/')}
        descriptor = self.canonical / 'asdg' / DESCRIPTOR
        value = json.loads(descriptor.read_text()); old_version = value['version']; value['version'] = '1.1.0-test'
        descriptor.write_bytes(encoded(value))
        model = self.canonical / 'asdg/scripts/lib/cli_model.py'
        model.write_text(model.read_text().replace("VERSION = '" + old_version + "'", "VERSION = '1.1.0-test'"))
        self.refresh(self.canonical)
        self.apply('upgrade')
        verification = run('verify')
        self.assertTrue(verification['structure_ok'])
        self.assertEqual(verification['distribution_version'], '1.1.0-test')
        self.assertEqual(before, {p: b for p, b in tree(self.pilot).items() if not p.startswith('asdg/')})
        self.assertEqual(self.apply('upgrade')['written_files'], [])


if __name__ == '__main__':
    unittest.main()
