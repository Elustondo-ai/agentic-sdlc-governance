"""Offline tests for the brownfield runner; real Codex calls require a local trial."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from unittest.mock import patch

from cli_baseline import capture, docs_from_output, parse_plan, source_manifest
from cli_files import Conflict
from cli_sprint import INACTIVE

CATALOG_SOURCE = Path(__file__).resolve().parents[1] / 'types' / 'agent-catalog.json'
SKILL_SOURCE = Path(__file__).resolve().parents[2] / 'skills' / 'asdlc-documentation' / 'SKILL.md'

MOCK_CODEX = r'''#!/usr/bin/env python3
import json, os, pathlib, re, sys, uuid
args = sys.argv[1:]
workspace = pathlib.Path(args[args.index('--cd') + 1]).parent
last = pathlib.Path(args[args.index('--output-last-message') + 1])
prompt = sys.stdin.read()
print(json.dumps({'type': 'thread.started', 'thread_id': 'offline-' + uuid.uuid4().hex}))
if 'read-only brownfield baseline planning' in prompt:
    message = {'selected_stages': list(range(1,13)) if os.environ.get('ASDLC_TEST_ROUTE_ALL') == '1' else [1,2,5], 'reason':'source code and plan', 'questions':[], 'assignments':[{'stage':n,'task':'Capture stage evidence','evidence':['source/Plan.md']} for n in (list(range(1,13)) if os.environ.get('ASDLC_TEST_ROUTE_ALL') == '1' else [1,2,5])]}
else:
    role = re.search(r'(ASDLC-\d\d|ASDLC-COORDINATOR)', prompt)
    assert role, prompt[:300]
    rid = role.group(1)
    unit = workspace / 'output' / '01-topic'
    unit.mkdir(parents=True, exist_ok=True)
    stamp = re.findall(r'AI-MODIFIED - (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)', prompt)
    assert stamp
    (unit / 'speaker-notes.md').write_text('AI-MODIFIED - '+stamp[-1]+'\n\n# Observed\n\nAgent: '+rid+'\nSources: source/Plan.md\nUncertainties: Runtime not observed.\nContradictions: None observed in this fixture.\n')
    (unit / 'visual.mmd').write_text('flowchart LR\nA[Observed] --> B[Baseline]\n')
    if os.environ.get('ASDLC_TEST_BAD_OUTPUT') == '1' and rid == 'ASDLC-02':
        (unit / 'unexpected.txt').write_text('wrong output')
    if os.environ.get('ASDLC_TEST_SOURCE_MOD') == '1' and rid == 'ASDLC-02':
        (workspace / 'source' / 'index.html').chmod(0o600)
        (workspace / 'source' / 'index.html').write_text('modified snapshot')
    if os.environ.get('ASDLC_TEST_STATE_MOD') and rid == 'ASDLC-02':
        pathlib.Path(os.environ['ASDLC_TEST_STATE_MOD']).write_text('{"status":"tampered"}')
    message = {'role_id':rid,'result':'Created an evidence-based visual and notes.'}
last.write_text(json.dumps(message))
'''


class BaselineFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.repo = self.path / 'provider'
        self.root = self.path / 'consumer'
        self.source = self.path / 'legacy'
        self.repo.mkdir()
        self.root.mkdir()
        self.source.mkdir()
        (self.root / '.asdlc').mkdir()
        (self.root / '.asdlc/sprint.json').write_text(json.dumps(INACTIVE))
        (self.source / 'index.html').write_text('<div>GOOD</div>\n')
        (self.source / 'Plan.md').write_text('Timer: 45s and 75s\n')
        (self.source / '.env').write_text('SECRET=not_imported\n')
        (self.source / '.git').mkdir()
        (self.source / '.git' / 'config').write_text('not copied')
        catalogue = json.loads(CATALOG_SOURCE.read_text())
        target = self.repo / 'asdlc/00-governance/types/agent-catalog.json'
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps(catalogue))
        skill = self.repo / 'asdlc/skills/asdlc-documentation/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_bytes(SKILL_SOURCE.read_bytes())
        for role in catalogue['agents']:
            item = self.repo / role['entry']
            item.parent.mkdir(parents=True, exist_ok=True)
            item.write_text(f'Role: {role["role_id"]}\nOwns stage {role["stage"]}\n')
            (self.root / 'docs/asdlc' / Path(role['folder']).name).mkdir(parents=True)
            for relative in (Path(role['folder']) / 'types/contract.md', Path(role['skill'])):
                file = self.repo / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('Synthetic offline role material, not native invocation evidence.\n')
        for relative in ('AGENTS.md', 'docs/status/lifecycle-baseline.md',
                         'asdlc/00-governance/docs/runtime-contract.md',
                         'asdlc/00-governance/types/interaction-contract.md'):
            file = self.repo / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('Synthetic offline shared material.\n')
        self.fake = self.path / 'fake-codex'
        self.fake.write_text(MOCK_CODEX)
        self.fake.chmod(0o755)

    def call_capture(self, **options):
        with patch('cli_baseline.inspect', return_value={'structure_ok':True,'missing':[]}):
            return capture(self.root, self.source, repo=self.repo,
                           codex=str(self.fake), timeout=60, **options)


class BaselineTests(BaselineFixture):
    def test_dry_run_no_agent_or_files(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*'))
        result = self.call_capture(dry_run=True)
        self.assertEqual(result['status'], 'DRY_RUN_ONLY')
        self.assertTrue(result['no_agents_invoked'])
        self.assertEqual(result['source_files'], 2)
        self.assertEqual(before, sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*')))
        self.assertIn('SECRET=not_imported', (self.source / '.env').read_text())

    def test_simulated_distinct_roles_and_tiny_logs(self):
        original = (self.source / 'index.html').read_bytes()
        result = self.call_capture(max_agents=2)
        self.assertEqual(result['status'], 'PARTIAL_CAPTURE_NEEDS_HUMAN_REVIEW')
        self.assertEqual(result['selected_stages'], [1,2])
        self.assertTrue(result['agent_sessions']['01'].startswith('offline-'))
        self.assertEqual(len(set(result['agent_sessions'].values())), 4)
        self.assertEqual((self.source / 'index.html').read_bytes(), original)
        self.assertEqual(len(result['written_artifacts']), 6)
        self.assertEqual(list(self.root.rglob('*.pptx')), [])
        self.assertEqual(json.loads((self.root / '.asdlc/sprint.json').read_text()), INACTIVE)
        for stage in ['00-governance','01-context-and-domain-analysis','02-intent']:
            root = self.root / 'docs/asdlc' / stage
            log = list((root / 'logs').glob('*.md'))
            self.assertEqual(len(log), 2 if stage == '00-governance' else 1)
            data = log[0].read_text()
            self.assertIn('Status: OK', data)
            self.assertIn('Started:', data)
            self.assertIn('Finished:', data)
            self.assertIn('Codex session:', data)
            self.assertLessEqual(len(data.splitlines()), 16)
            units = list((root / 'baselines').rglob('speaker-notes.md'))
            self.assertEqual(len(units), 1)
            self.assertTrue((units[0].parent / 'visual.mmd').is_file())

    def test_full_thirteen_roles_have_distinct_outputs_and_logs(self):
        with patch.dict(os.environ, {'ASDLC_TEST_ROUTE_ALL':'1'}):
            result = self.call_capture()
        self.assertEqual(result['status'], 'CAPTURED_NEEDS_HUMAN_REVIEW')
        self.assertEqual(result['selected_stages'], list(range(1,13)))
        catalogue = json.loads(CATALOG_SOURCE.read_text())
        for role in catalogue['agents']:
            folder = self.root / 'docs/asdlc' / Path(role['folder']).name
            self.assertEqual(len(list((folder / 'logs').glob('*.md'))), 2 if role['stage'] == 0 else 1)
            notes = list((folder / 'baselines').rglob('speaker-notes.md'))
            self.assertEqual(len(notes), 1)
            self.assertIn('Agent: ' + role['role_id'], notes[0].read_text())
        self.assertEqual(len(result['agent_sessions']), 14)  # Coordinator twice, 12 specialists.
        self.assertEqual(len(result['written_artifacts']), 26)

    def test_invalid_artifact_is_rejected_and_logged(self):
        with patch.dict(os.environ, {'ASDLC_TEST_BAD_OUTPUT':'1'}):
            with self.assertRaisesRegex(Conflict, 'Unexpected artifact type'):
                self.call_capture(max_agents=2)
        stage = self.root / 'docs/asdlc/02-intent'
        self.assertFalse(list((stage / 'baselines').rglob('speaker-notes.md')) if (stage/'baselines').exists() else [])
        log = next((stage / 'logs').glob('*.md')).read_text()
        self.assertIn('Status: ERROR', log)

    def test_source_snapshot_mutation_rejected(self):
        with patch.dict(os.environ, {'ASDLC_TEST_SOURCE_MOD':'1'}):
            with self.assertRaisesRegex(Conflict, 'outside output/'):
                self.call_capture(max_agents=2)
        self.assertEqual((self.source / 'index.html').read_text(), '<div>GOOD</div>\n')

    def test_missing_runner_fails_before_creating_logs(self):
        with patch('cli_baseline.inspect', return_value={'structure_ok':True,'missing':[]}):
            with self.assertRaisesRegex(Conflict, 'Codex CLI is unavailable'):
                capture(self.root, self.source, repo=self.repo, codex='not-existing-exec-test')
        self.assertFalse(list(self.root.rglob('logs/*.md')))

    def test_invalid_routing(self):
        with self.assertRaises(Conflict):
            parse_plan(json.dumps({'selected_stages':[5], 'reason':'no context'}))
        with self.assertRaises(Conflict):
            parse_plan(json.dumps({'selected_stages':[1,1], 'reason':'repeat'}))


class BaselineSafetyTests(BaselineFixture):
    def test_invalid_limits_are_rejected_even_during_dry_run(self):
        for options in ({'max_agents': 0}, {'max_agents': 13}, {'timeout': 59}, {'timeout': 3601}):
            with patch('cli_baseline.inspect', return_value={'structure_ok': True, 'missing': []}):
                with self.assertRaises(Conflict):
                    capture(self.root, self.source, repo=self.repo, dry_run=True, **options)
        self.assertFalse(list(self.root.rglob('*.md')))

    def test_sensitive_binary_and_symlink_evidence_are_excluded(self):
        (self.source / 'leaked.txt').write_text('sk-proj-' + 'X' * 30)
        (self.source / 'binary.png').write_bytes(b'\x89PNG\x00not-text')
        (self.source / 'private').symlink_to(self.source / '.git', target_is_directory=True)
        files, excluded = source_manifest(self.source)
        self.assertEqual({entry['path'] for entry in files}, {'Plan.md', 'index.html'})
        self.assertTrue(any('sensitive' in item for item in excluded))
        self.assertTrue(any('symlink' in item for item in excluded))
        self.assertTrue(any('binary' in item for item in excluded))
        self.assertTrue(any('.git' in item for item in excluded))

    def test_changed_source_snapshot_is_rejected(self):
        from cli_baseline import copy_inventory
        files, _ = source_manifest(self.source)
        (self.source / 'Plan.md').write_text('changed')
        with self.assertRaisesRegex(Conflict, 'Source changed'):
            copy_inventory(self.source, self.path / 'snapshot', files)

    def test_output_only_profile_does_not_bypass_hook_trust(self):
        from cli_baseline import codex_options
        args = codex_options(self.path)
        self.assertEqual(args[args.index('--cd') + 1], str(self.path / 'output'))
        self.assertIn('default_permissions="asdg_baseline"', args)
        self.assertIn('permissions.asdg_baseline.network.enabled=false', args)
        self.assertFalse(any('bypass' in item for item in args))
        self.assertIn('mcp_servers={}', args)
        self.assertIn('agents.enabled=false', args)
        self.assertTrue(any('":root"="deny"' in item for item in args))
        self.assertTrue(any('":slash_tmp"="deny"' in item for item in args))

    def test_empty_directory_outside_output_is_detected(self):
        from cli_baseline import workspace_snapshot
        work = self.path / 'workspace'
        work.mkdir()
        (work / 'output').mkdir()
        before = workspace_snapshot(work)
        (work / 'unauthorized').mkdir()
        self.assertNotEqual(workspace_snapshot(work), before)

    def test_bad_output_retains_failure_session_and_previous_success(self):
        with patch.dict(os.environ, {'ASDLC_TEST_BAD_OUTPUT': '1'}):
            with self.assertRaises(Conflict):
                self.call_capture(max_agents=2)
        report = json.loads(next(self.root.rglob('*__baseline-run.json')).read_text())
        self.assertEqual(report['status'], 'ERROR')
        self.assertEqual([item['status'] for item in report['invocations']], ['OK', 'OK', 'ERROR'])
        failed = report['invocations'][-1]
        self.assertTrue(failed['session_id'].startswith('offline-'))
        self.assertIn(failed['session_id'], Path(failed['log_path']).read_text())
        self.assertIn('Finished:', Path(failed['log_path']).read_text())
        self.assertFalse(report['source_modified'])
        self.assertFalse(report['sprint_changed'])

    def test_canonical_sprint_mutation_is_detected_and_reported(self):
        # Deliberately unsandboxed offline double exercises the runner's postcondition.
        with patch.dict(os.environ, {'ASDLC_TEST_STATE_MOD': str(self.root / '.asdlc/sprint.json')}):
            with self.assertRaisesRegex(Conflict, 'Canonical sprint'):
                self.call_capture(max_agents=2)
        report = json.loads(next(self.root.rglob('*__baseline-run.json')).read_text())
        self.assertTrue(report['sprint_changed'])
        self.assertEqual(report['invocations'][-1]['status'], 'ERROR')
        self.assertEqual(report['sprint_state_at_start'], INACTIVE)
        self.assertFalse(list((self.root / 'docs/asdlc/02-intent').rglob('speaker-notes.md')))

    def test_output_ownership_format_approval_and_line_limit(self):
        agent = {'role_id': 'ASDLC-01'}
        output = self.path / 'outputs'
        unit = output / '01-test'
        unit.mkdir(parents=True)
        visual = unit / 'visual.mmd'
        visual.write_text('flowchart LR\nA --> B\n')
        from cli_model import now
        good = ('AI-MODIFIED - ' + now() + '\nAgent: ASDLC-01\nSources: source/Plan.md\n'
                'Uncertainties: Unverified runtime.\nContradictions: None observed.\n')
        notes = unit / 'speaker-notes.md'
        for text in (good.replace('ASDLC-01', 'ASDLC-05'), good + 'PME-APPROVED - fake\n',
                     good + '\n' * 51, good.replace('Sources:', 'Missing:')):
            notes.write_text(text)
            with self.assertRaises((Conflict, ValueError)):
                docs_from_output(output, agent)
        notes.write_text(good)
        self.assertEqual(len(docs_from_output(output, agent)), 2)
        visual.write_text('flowchart LR\nclick A "javascript:alert(1)"\n')
        with self.assertRaises(Conflict):
            docs_from_output(output, agent)
        visual.unlink()
        visual.symlink_to(self.source / 'Plan.md')
        with self.assertRaises(Conflict):
            docs_from_output(output, agent)

    def test_valid_mermaid_comments_and_dialects_are_preserved(self):
        from cli_baseline_safety import validate_visual
        for data in (b"%% authored diagram\nflowchart LR\nA --> B\n",
                     b"requirementDiagram\nrequirement goal { id: 1 text: concise risk: low verifymethod: inspection }\n"):
            validate_visual(Path("visual.mmd"), data)
        with self.assertRaises(Conflict):
            validate_visual(Path("visual.mmd"), b"%%{init: {'securityLevel': 'loose'}}%%\nflowchart LR\nA --> B")

    def test_svg_active_and_external_content_is_rejected(self):
        from cli_baseline_safety import validate_visual
        for body in ('<style>@import "https://example.invalid/style.css";</style>',
                     '<rect style="fill:url(https://example.invalid/image)"/>',
                     '<image href="https://example.invalid/image"/>',
                     '<foreignObject><iframe src="https://example.invalid/"/></foreignObject>',
                     '<set attributeName="href" to="https://example.invalid/image"/>'):
            with self.subTest(body=body), self.assertRaises(Conflict):
                validate_visual(Path('visual.svg'), ('<svg>' + body + '</svg>').encode())
        validate_visual(Path('visual.svg'), b'<svg><rect style="fill:url(#local)"/></svg>')

    def test_empty_topic_directory_is_rejected(self):
        output = self.path / 'outputs'
        unit = output / '01-topic'
        unit.mkdir(parents=True)
        (unit / 'visual.mmd').write_text('flowchart LR\nA --> B\n')
        from cli_model import now
        (unit / 'speaker-notes.md').write_text('AI-MODIFIED - ' + now() + '\nEvidence notes.\n')
        (output / '02-empty-topic').mkdir()
        with self.assertRaisesRegex(Conflict, 'exactly one visual'):
            docs_from_output(output)

    def test_non_object_and_unjustified_plan_rejected(self):
        for value in ('[]', '{}', '{"selected_stages":[true],"reason":"bad"}',
                      '{"selected_stages":[1],"reason":"missing assignments"}'):
            with self.assertRaises(Conflict):
                parse_plan(value)

    def test_distinct_invocation_logs_and_byte_authorship_manifest(self):
        result = self.call_capture(max_agents=2)
        self.assertEqual(len(result['invocations']), 4)
        self.assertEqual(len({item['log_path'] for item in result['invocations']}), 4)
        from cli_baseline import digest
        self.assertEqual(result['source_inventory_sha256'], digest(json.dumps(
            result['source_inventory'], indent=2, ensure_ascii=False).encode() + b'\n'))
        self.assertEqual(result['source'], str(self.source.resolve()))
        self.assertEqual(result['methodology'], str(self.repo.resolve()))
        self.assertEqual(result['max_agents'], 2)
        self.assertEqual(result['sprint_state_at_start'], INACTIVE)
        for item in result['invocations']:
            for artifact in item['artifacts']:
                self.assertEqual(artifact['owner'], item['role_id'])
                self.assertEqual(artifact['session_id'], item['session_id'])
                self.assertEqual(artifact['sha256'], digest((self.root / artifact['path']).read_bytes()))

    def test_timeout_preserves_emitted_session(self):
        from cli_baseline import codex_run, InvocationError
        fake = self.path / 'sleep-codex'
        fake.write_text('#!/usr/bin/env python3\nimport json,time\n'
                        'print(json.dumps({"type":"thread.started","thread_id":"offline-timeout"}),flush=True)\n'
                        'time.sleep(5)\n')
        fake.chmod(0o755)
        work = self.path / 'sleep-work'
        (work / 'output').mkdir(parents=True)
        with self.assertRaises(InvocationError) as context:
            codex_run(str(fake), work, 'test', 1)
        self.assertEqual(context.exception.session, 'offline-timeout')


from test_cli_bootstrap import Fixture, REPO


class BaselineCliTests(Fixture):
    def setUp(self):
        super().setUp()
        self.setup_install()
        (self.provider / 'asdlc/skills/asdlc-documentation').mkdir(parents=True)
        shutil.copyfile(SKILL_SOURCE, self.provider / 'asdlc/skills/asdlc-documentation/SKILL.md')
        catalog = json.loads(CATALOG_SOURCE.read_text())
        required = ['AGENTS.md', 'asdlc/00-governance/docs/runtime-contract.md',
                    'asdlc/00-governance/types/interaction-contract.md']
        for agent in catalog['agents'][:2]:
            required += [agent['entry'], agent['skill'], str(Path(agent['folder']) / 'types/contract.md')]
        for relative in required:
            path = self.provider / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, path)
        self.assertEqual(self.run_cli('init').returncode, 0)
        self.legacy = self.base / 'legacy source'
        self.legacy.mkdir()
        (self.legacy / 'app.txt').write_text('Documented legacy evidence')

    def test_real_cli_registration_dry_run_json_and_state_preservation(self):
        state = {p: (self.project / p).read_bytes() for p in ('.asdlc/sprint.json', '.asdlc/project.json',
                                                           '.codex/hooks.json', '.asdlc/lifecycle.json')}
        result = self.run_cli('baseline', 'capture', '--source', str(self.legacy), '--dry-run', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'DRY_RUN_ONLY')
        self.assertTrue(report['no_agents_invoked'])
        self.assertEqual(report['source_files'], 1)
        self.assertFalse(list(self.project.rglob('*__baseline-capture*.md')))
        for path, before in state.items():
            self.assertEqual((self.project / path).read_bytes(), before)
        for command in (('verify',), ('status', '--json'), ('sprint', 'status')):
            self.assertEqual(self.run_cli(*command).returncode, 0)

    def test_invalid_cli_arguments_exit_nonzero(self):
        for arguments in (('baseline', 'capture'), ('baseline', 'capture', '--source', str(self.legacy),
                                                   '--max-agents', '0', '--dry-run')):
            self.assertNotEqual(self.run_cli(*arguments).returncode, 0)


if __name__ == '__main__':
    unittest.main()
