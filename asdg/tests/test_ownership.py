"""Ownership and hook regressions in disposable initialized client repositories."""
import json
import os
import subprocess
import unittest
from unittest.mock import patch
import test_portable as portable
from cli_ownership import owned_directory, ownership_decision
from cli_hook import decision


class OwnershipTests(unittest.TestCase):
    setUp = portable.PortableTests.setUp
    seal_package = portable.PortableTests.seal_package
    run_cli = portable.PortableTests.run_cli
    init = portable.PortableTests.init
    active = portable.PortableTests.active
    hook = portable.PortableTests.hook
    payload = portable.PortableTests.payload

    def check(self, role, paths, **extra):
        return ownership_decision(self.root, paths, dict(role_id=role, **extra))

    def test_all_catalogue_destinations_and_no_sprint(self):
        self.init('--client', 'both')
        rows = json.loads((self.root / 'asdg/00-governance/types/agent-catalog.json').read_text())['agents']
        for row in rows:
            own = owned_directory(row['role_id'])
            target = str(own / '03-proposal.md')
            self.assertTrue(self.check(row['role_id'], [target])[0])
            self.assertEqual(self.hook(self.payload([target]), role=row['role_id']), {})
        self.run_cli('verify')
        before = portable.snapshot(self.root)
        self.init('--client', 'both')
        self.assertEqual(portable.snapshot(self.root), before)

    def test_architecture_reads_purpose_but_cannot_update_delete_or_move_it(self):
        self.init()
        source = 'docs/asdg/02-purpose/README.md'
        payload = {'tool_name': 'Bash', 'tool_input': {'command': 'cat ' + source}}
        self.assertEqual(self.hook(payload, role='ASDG-05'), {})
        own = 'docs/asdg/05-high-level-design-and-architecture/03-proposal.md'
        self.assertEqual(self.hook(self.payload([own]), role='ASDG-05'), {})
        for header in ('Update File', 'Delete File'):
            bad = self.payload([])
            bad['tool_input']['command'] = '*** Begin Patch\n*** ' + header + ': ' + source + '\n*** End Patch'
            result = self.hook(bad, role='ASDG-05')
            self.assertIn('proposal', result['hookSpecificOutput']['permissionDecisionReason'])
        bad['tool_input']['command'] = '*** Begin Patch\n*** Update File: ' + source + '\n*** Move to: ' + own + '\n*** End Patch'
        self.assertIn('deny', str(self.hook(bad, role='ASDG-05')))
        self.assertFalse(self.check('ASDG-09', [source])[0])

    def test_openspec_custom_resolved_store_exact_artifacts(self):
        self.init()
        targets = ['planning/spec-store/changes/example/proposal.md', 'planning/spec-store/specs/example/spec.md']
        context = {'role_id': 'ASDG-08', 'workflow': 'openspec', 'openspec_store': 'planning/spec-store', 'targets': targets}
        self.assertEqual(self.hook(self.payload(targets), context=context), {})
        self.assertFalse(self.check('ASDG-05', targets, **{k:v for k,v in context.items() if k != 'role_id'})[0])
        self.assertFalse(self.check('ASDG-08', targets)[0])
        self.assertFalse(self.check('ASDG-08', ['planning/spec-store/other.md'], **{k:v for k,v in context.items() if k != 'role_id'})[0])
        context.update(openspec_store='docs/asdg/02-purpose', targets=['docs/asdg/02-purpose/spec.md'])
        self.assertIn('deny', str(self.hook(self.payload(context['targets']), context=context)))
        # Actual native OpenSpec validation is intentionally not simulated here.

    def test_coding_role_and_sprint_are_independent(self):
        self.init()
        self.assertIn('deny', str(self.hook(self.payload(['app.js']))))
        self.active()
        self.assertEqual(self.hook(self.payload(['app.js'])), {})
        self.assertIn('deny', str(self.hook(self.payload(['app.js']), role='ASDG-05')))
        self.assertIn('deny', str(self.hook(self.payload(['index.html']))))
        self.assertIn('deny', str(self.hook(self.payload(['docs/asdg/02-purpose/README.md']))))

    def test_governance_admin_and_shared_workflows(self):
        self.init()
        shared = 'docs/shared/coordination.md'
        self.assertFalse(self.check('ASDG-COORDINATOR', [shared])[0])
        self.assertTrue(self.check('ASDG-COORDINATOR', [shared], workflow='shared-record', targets=[shared])[0])
        self.assertFalse(self.check('ASDG-05', [shared], workflow='shared-record', targets=[shared])[0])
        target = 'asdg/skills/asdg-documentation/SKILL.md'
        self.assertTrue(self.check('ASDG-ADMIN', [target], workflow='admin', targets=[target])[0])
        self.assertFalse(self.check('ASDG-ADMIN', [target])[0])
        self.assertFalse(self.check('ASDG-ADMIN', ['app.js'], workflow='admin', targets=['app.js'])[0])
        for role in ('ASDG-COORDINATOR', 'ASDG-05', 'ASDG-ADMIN'):
            self.assertTrue(self.check(role, ['.asdg/document-reviews.json'], workflow='review-receipt')[0])
            self.assertTrue(self.check(role, ['.asdg/lifecycle.json'], workflow='approve', targets=['.asdg/lifecycle.json'])[0])
            self.assertFalse(self.check(role, ['.asdg/lifecycle.json'])[0])
        close = '.asdg/sprint-closeouts/12345678-1234-5678-1234-567812345678.json'
        self.assertTrue(self.check('ASDG-05', [close, '.asdg/sprint.json'], workflow='sprint-close', targets=[close, '.asdg/sprint.json'])[0])

    def test_unknown_stale_or_tool_supplied_identity_never_grants_writes(self):
        self.init()
        payload = dict(self.payload(['docs/asdg/05-high-level-design-and-architecture/03-proposal.md']), session_id='actual')
        payload['tool_input']['role_id'] = 'ASDG-05'
        for context in ({}, {'role_id': 'ASDG-05', 'session_id': 'other'}, {'role_id': 'unknown', 'session_id': 'actual'}):
            with patch.dict(os.environ, ASDG_WRITE_CONTEXT=json.dumps(context)):
                self.assertFalse(decision(self.root, payload)[0])
        self.assertFalse(self.check(None, ['docs/shared/a.md'])[0])
        self.assertFalse(self.check('ASDG-05', ['docs/asdg/02-purpose/a.md'], workflow='admin', targets=['docs/asdg/02-purpose/a.md'])[0])

    def test_cli_preflight_reports_handoff_and_preserves_state(self):
        self.init()
        before = portable.snapshot(self.root)
        ctx = json.dumps({'role_id': 'ASDG-05'})
        self.run_cli('check-write', '--context', ctx, '--path', 'docs/asdg/05-high-level-design-and-architecture/03-proposal.md')
        result = self.run_cli('check-write', '--context', ctx, '--path', 'docs/asdg/02-purpose/README.md', expect=1)
        self.assertIn('handoff', result.stdout)
        self.assertEqual(portable.snapshot(self.root), before)

    @unittest.skipUnless(__import__('shutil').which('openspec'), 'OpenSpec CLI not installed')
    def test_native_openspec_artifacts_validate_after_ownership_preflight(self):
        # This fixture initializes its own store; never changes the real project or global config.
        self.root = self.root.resolve()
        home = self.root.parent / 'openspec-home'
        home.mkdir()
        env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / 'config'),
                   OPENSPEC_TELEMETRY='0', DO_NOT_TRACK='1')
        def native(*args):
            result = subprocess.run(['openspec', *args], cwd=self.root, env=env,
                                    text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout) if '--json' in args else result.stdout
        native('init', '--tools', 'none', '--no-animation')
        change = native('new', 'change', 'ownership-fixture', '--json')
        change_dir = __import__('pathlib').Path(change['change']['path'])
        artifacts = {
            'proposal': ('proposal.md', '# Proposal\n\n## Why\nPrevent accidental cross-owner edits.\n\n## What Changes\nAdd role write checks.\n\n## Capabilities\n### New Capabilities\n- `write-ownership`: Check acting-role destinations.\n\n### Modified Capabilities\nNone.\n\n## Impact\nAgent documentation workflows.\n'),
            'specs': ('specs/write-ownership/spec.md', '## ADDED Requirements\n\n### Requirement: Own documentation writes\nThe system SHALL deny cross-owner documentation writes.\n\n#### Scenario: Architecture proposes a Purpose edit\n- **WHEN** Architecture targets Purpose documentation\n- **THEN** the check denies the write and requests a handoff\n'),
            'design': ('design.md', '## Context\nAgents share project knowledge.\n\n## Goals / Non-Goals\nPrevent accidental writes; no security boundary.\n\n## Decisions\nUse catalogue ownership.\n\n## Risks / Trade-offs\nIdentity is declared, not authenticated.\n'),
            'tasks': ('tasks.md', '## 1. Ownership checks\n\n- [ ] 1.1 Check ownership before documentation writes.\n'),
        }
        for artifact, (relative, content) in artifacts.items():
            instructions = native('instructions', artifact, '--change', 'ownership-fixture', '--json')
            # Store is derived from native output, not assumed in the policy.
            planning = __import__('pathlib').Path(instructions['planningHome']['changesDir']).parent
            target = change_dir / relative
            if artifact != 'specs':
                self.assertEqual(str(target), instructions['resolvedOutputPath'])
            paths = [str(target)]
            self.assertTrue(self.check('ASDG-08', paths, workflow='openspec',
                                       openspec_store=str(planning), targets=paths)[0])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        result = native('validate', 'ownership-fixture', '--type', 'change', '--strict', '--json')
        self.assertTrue(result)
