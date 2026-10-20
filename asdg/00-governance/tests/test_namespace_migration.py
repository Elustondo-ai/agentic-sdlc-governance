"""Bounded legacy migration tests using neutral disposable projects only."""
import json
from pathlib import Path
import stat
from unittest.mock import patch

from test_cli_bootstrap import Fixture
from cli_files import Conflict
from cli_model import catalogue, json_bytes, sha
from cli_namespace import (LEGACY_CATALOG, LEGACY_DOCS, LEGACY_STATE, DOCS, STATE,
                           RECEIPT, consumer_path, migrate_project)
from cli_project import BRIDGE, HOOK_CONFIG, hook_config, initialize
from cli_sprint import INACTIVE, read_state


class NamespaceMigrationTests(Fixture):
    def legacy(self, active=False):
        raw = LEGACY_CATALOG.read_bytes()
        legacy = json.loads(raw)
        state = self.project / LEGACY_STATE
        state.mkdir()
        binding = {'schema_version': 1, 'provider': 'elustondo.ai/asdlc',
                   'project_id': 'neutral-project', 'cli_version': '0.1.3',
                   'artifacts_root': str(LEGACY_DOCS), 'catalog_sha256': sha(raw),
                   'methodology_revision_at_init': 'retained-revision',
                   'installation_mode': 'linked-development-checkout',
                   'initialized_at': '2026-01-01T00:00:00Z',
                   'stages': [Path(a['folder']).name for a in legacy['agents']]}
        (state / 'project.json').write_bytes(json_bytes(binding))
        sprint = (dict(status='active', sprint_id='existing-neutral-sprint',
                       objective='Preserve the existing objective', scope=['app.py'],
                       acceptance_criteria=['Existing criterion unchanged']) if active else INACTIVE)
        (state / 'sprint.json').write_bytes(json_bytes(sprint))
        (state / 'sprint.json').chmod(0o640)
        lifecycle = {'schema_version': 1, 'project_status': 'defining', 'release': None,
                     'stages': {}}
        (state / 'lifecycle.json').write_bytes(json_bytes(lifecycle))
        (state / '.gitignore').write_text('backups/\n')
        (self.project / LEGACY_DOCS).mkdir(parents=True)
        (self.project / LEGACY_DOCS / 'README.md').write_text('# Neutral documentation\n\nExisting project.\n')
        for stage in binding['stages']:
            folder = self.project / LEGACY_DOCS / stage
            folder.mkdir()
            (folder / 'README.md').write_text('# Stage\n\nExisting evidence and decisions.\n')
        topic = self.project / LEGACY_DOCS / '02-intent/01-evidence'
        topic.mkdir()
        (topic / 'speaker-notes.md').write_text('# Historical capture\n\nASDLC-02 evidence, not new observations.\n')
        advice = self.project / LEGACY_DOCS / '07-planning/advice'
        advice.mkdir()
        (advice / 'status-historical.md').write_text('# Historical advice\n\nASDLC-07 recorded recommendation.\n')
        (self.project / '.codex').mkdir()
        (self.project / '.codex/config.toml').write_bytes(HOOK_CONFIG)
        hook = hook_config(self.project, self.provider).decode().replace('ASDG', 'ASDLC').replace('/asdg/', '/asdlc/')
        (self.project / '.codex/hooks.json').write_text(hook)
        bridge = BRIDGE.replace('ASDG', 'ASDLC').replace('asdg/', 'asdlc/').replace('.asdg', '.asdlc')
        (self.project / 'AGENTS.md').write_text('# Project agent instructions\n\n' + bridge)
        return raw, binding, sprint, lifecycle

    def snapshot(self):
        return {str(p.relative_to(self.project)): (p.read_bytes(), stat.S_IMODE(p.stat().st_mode))
                for p in self.project.rglob('*') if p.is_file() and '.git' not in p.parts}

    def test_dry_run_is_non_mutating(self):
        raw, *_ = self.legacy()
        before = self.snapshot()
        self.assertEqual(migrate_project(self.project, self.provider, legacy_catalog=raw)['status'], 'DRY_RUN')
        self.assertEqual(self.snapshot(), before)

    def test_migration_preserves_active_state_history_permissions_and_application(self):
        raw, binding, sprint, lifecycle = self.legacy(active=True)
        before = self.snapshot()
        result = migrate_project(self.project, self.provider, apply=True, legacy_catalog=raw)
        self.assertEqual(result['status'], 'MIGRATED')
        self.assertFalse((self.project / LEGACY_STATE).exists())
        self.assertFalse((self.project / LEGACY_DOCS).exists())
        self.assertEqual(read_state(self.project), sprint)
        self.assertEqual(json.loads((self.project / STATE / 'lifecycle.json').read_text()), lifecycle)
        self.assertEqual(json.loads((self.project / STATE / 'project.json').read_text())['project_id'], binding['project_id'])
        for p, (data, mode) in before.items():
            dest = self.project / consumer_path(Path(p))
            self.assertEqual(stat.S_IMODE(dest.stat().st_mode), mode, str(dest))
            if p.endswith(('speaker-notes.md', 'status-historical.md')) or p == 'app.py':
                self.assertEqual(dest.read_bytes(), data)
        for stage in catalogue(self.provider)[0]:
            for view in ('intended', 'current', 'planned'):
                self.assertTrue((self.project / DOCS / Path(stage['folder']).name / view).is_dir())
        self.assertEqual((self.project / '.codex/hooks.json').read_bytes(), hook_config(self.project, self.provider))
        self.assertIsNone(json.loads((self.project / RECEIPT).read_text())['human_approval'])

    def test_repeat_migration_and_initialization_preserve_state_and_never_recreate_legacy(self):
        raw, _, sprint, _ = self.legacy(active=True)
        migrate_project(self.project, self.provider, apply=True, legacy_catalog=raw)
        self.assertEqual(migrate_project(self.project, self.provider, apply=True)['status'], 'ALREADY_MIGRATED')
        initialize(self.project, self.provider)
        self.assertEqual(initialize(self.project, self.provider)['changed_files'], [])
        self.assertEqual(read_state(self.project), sprint)
        self.assertFalse((self.project / LEGACY_STATE).exists())
        self.assertFalse((self.project / LEGACY_DOCS).exists())

    def test_conflicting_state_trees_fail_before_writes(self):
        raw, *_ = self.legacy()
        (self.project / STATE).mkdir()
        before = self.snapshot()
        with self.assertRaisesRegex(Conflict, 'Conflicting'):
            migrate_project(self.project, self.provider, apply=True, legacy_catalog=raw)
        self.assertEqual(self.snapshot(), before)

    def test_unknown_binding_and_initialization_of_legacy_are_rejected(self):
        raw, *_ = self.legacy()
        with self.assertRaisesRegex(Conflict, 'migrate-namespace'):
            initialize(self.project, self.provider)
        p = self.project / LEGACY_STATE / 'project.json'
        value = json.loads(p.read_text()); value['catalog_sha256'] = 'unknown'
        p.write_bytes(json_bytes(value))
        before = self.snapshot()
        with self.assertRaisesRegex(Conflict, 'reviewed'):
            migrate_project(self.project, self.provider, apply=True, legacy_catalog=raw)
        self.assertEqual(self.snapshot(), before)

    def test_write_failure_restores_original_paths_and_state(self):
        raw, *_ = self.legacy()
        before = self.snapshot()
        with patch('cli_namespace.atomic_replace', side_effect=OSError('Synthetic storage failure')):
            with self.assertRaises(OSError):
                migrate_project(self.project, self.provider, apply=True, legacy_catalog=raw)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue((self.project / LEGACY_STATE).exists())
        self.assertFalse((self.project / STATE).exists())

    def test_lifecycle_and_scope_references_follow_evidence_without_losing_decisions(self):
        raw, _, sprint, lifecycle = self.legacy(active=True)
        sprint['scope'] = ['docs/asdlc/02-intent/01-evidence/']
        lifecycle['stages'] = {'02': {'artifacts': ['docs/asdlc/02-intent/01-evidence/speaker-notes.md'],
                                     'not_applicable_reason': None}}
        (self.project / LEGACY_STATE / 'sprint.json').write_bytes(json_bytes(sprint))
        (self.project / LEGACY_STATE / 'lifecycle.json').write_bytes(json_bytes(lifecycle))
        migrate_project(self.project, self.provider, apply=True, legacy_catalog=raw)
        updated = read_state(self.project)
        self.assertEqual(updated['scope'], ['docs/asdg/02-purpose/current/01-evidence/'])
        for field in ('sprint_id', 'objective', 'acceptance_criteria', 'status'):
            self.assertEqual(updated[field], sprint[field])
        current = json.loads((self.project / STATE / 'lifecycle.json').read_text())
        evidence = current['stages']['02']['artifacts'][0]
        self.assertEqual(evidence, 'docs/asdg/02-purpose/current/01-evidence/speaker-notes.md')
        self.assertTrue((self.project / evidence).is_file())

    def test_conflicting_current_evidence_fails_before_writes(self):
        raw, *_ = self.legacy()
        conflict = self.project / LEGACY_DOCS / '02-intent/current/01-evidence'
        conflict.mkdir(parents=True)
        (conflict / 'decision.md').write_text('# Retained decision\n\nDo not overwrite.\n')
        before = self.snapshot()
        with self.assertRaisesRegex(Conflict, 'Conflicting current'):
            migrate_project(self.project, self.provider, apply=True, legacy_catalog=raw)
        self.assertEqual(self.snapshot(), before)

    def test_symlink_source_is_rejected_before_writes(self):
        raw, *_ = self.legacy()
        (self.project / LEGACY_DOCS / 'linked-evidence').symlink_to(self.project / 'app.py')
        before = self.snapshot()
        with self.assertRaisesRegex(Conflict, 'linked migration source'):
            migrate_project(self.project, self.provider, apply=True, legacy_catalog=raw)
        self.assertEqual(self.snapshot(), before)
