"""End-to-end portable installation/guard regressions in disposable repositories."""
import copy
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
sys.dont_write_bytecode = True
sys.path.insert(0, str(CORE / 'scripts/lib'))
from cli_files import apply, plan
from cli_runtime_env import subprocess_environment
from cli_advice import build_prompt
from cli_advice_report import save_advice


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.area = tempfile.TemporaryDirectory(prefix='asdg-portable-')
        self.addCleanup(self.area.cleanup)
        self.root = Path(self.area.name) / 'client project'
        self.root.mkdir()
        shutil.copytree(CORE, self.root / 'asdg', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / 'app.js').write_text('console.log("existing application");\n')
        (self.root / 'index.html').write_text('<script src="app.js"></script>\n')
        self.app = (self.root / 'app.js').read_bytes()

    def run_cli(self, *args, entry='cli.py', expect=0, cwd=None):
        result = subprocess.run([sys.executable, '-B', str(self.root / 'asdg/scripts' / entry), *args],
                                cwd=cwd or self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        return result

    def init(self, *args, **kw):
        return self.run_cli(*args, entry='init.py', **kw)

    def active(self):
        self.run_cli('sprint', 'start', '--id', 'S1', '--objective', 'One bounded behavior',
                     '--scope', 'app.js', '--acceptance', 'Existing behavior is retained')

    def hook(self, payload, event='PreToolUse', cwd=None):
        config = json.loads((self.root / '.codex/hooks.json').read_text())
        command = config['hooks'][event][0]['hooks'][0]['command']
        result = subprocess.run(command, shell=True, input=json.dumps(payload), text=True,
                                cwd=cwd or self.root, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def payload(self, paths):
        command = '*** Begin Patch\n' + '\n'.join('*** Update File: ' + p + '\n@@\n-old\n+new' for p in paths) + '\n*** End Patch'
        return {'tool_name': 'apply_patch', 'cwd': str(self.root), 'tool_input': {'command': command}}

    def denied(self, payload):
        self.assertEqual(self.hook(payload)['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_dry_run_then_init_repeat_is_byte_identical(self):
        before = snapshot(self.root)
        self.init('--project-status', 'defining', '--dry-run')
        self.assertEqual(snapshot(self.root), before)
        self.init('--project-status', 'defining')
        after = snapshot(self.root)
        report = json.loads(self.init('--json').stdout)
        self.assertEqual(report['changed_files'], [])
        self.assertEqual(snapshot(self.root), after)
        self.assertEqual((self.root / 'app.js').read_bytes(), self.app)
        status = json.loads(self.run_cli('status', '--json').stdout)
        self.assertEqual((status['project_status'], status['release_status'], status['sprint_status']), ('defining', 'none', 'inactive'))
        self.assertEqual(status['implementation_permission'], 'BLOCKED')
        self.assertEqual(status['guard']['runtime_trust'], 'UNKNOWN')
        self.assertEqual(len(status['lifecycle_stages']), 12)
        self.assertEqual(status['current_stage']['number'], 1)

    def test_default_initial_state_new_and_no_later_redeclaration(self):
        self.init()
        before = snapshot(self.root)
        self.init('--project-status', 'defined', expect=1)
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual(json.loads(self.run_cli('status', '--json').stdout)['project_status'], 'new')

    def test_advice_report_creates_planning_parents_without_changing_state(self):
        self.init('--project-status', 'defining')
        before = snapshot(self.root)
        status = json.loads(self.run_cli('status', '--json').stdout)
        advice = dict(status='available',
            summary=dict(action='Review the existing context.',
                         reason='Its evidence is not registered.', question=None),
            action='Review the existing context and propose evidence references.',
            reason='Existing files need provenance review.',
            evidence=['.asdg/lifecycle.json'], questions=[],
            uncertainties=['Human acceptance is not recorded.'],
            requirements=['Human review remains pending.'],
            runtime=dict(sdk_version='0.163.0', cli_version='0.163.0', model='fixture',
                         model_provider='openai', model_basis='THREAD_CONFIGURATION',
                         thread_id='fixture-thread', turn_id='fixture-turn',
                         sandbox='read-only', approval_mode='deny-all', ephemeral=True))
        report = save_advice(self.root.resolve(), status, advice, repo=self.root)
        self.assertEqual(report.parent, self.root / 'docs/asdg/07-planning/current/advice')
        receipt = json.loads(report.with_suffix('.json').read_text())
        self.assertIsNone(receipt['document_review']['human_approval'])
        self.assertLessEqual(sum(bool(x.strip()) for x in report.read_text().splitlines()), 50)
        after = snapshot(self.root)
        self.assertEqual({k: after[k] for k in before}, before)
        self.assertEqual(set(after) - set(before),
                         {p.relative_to(self.root).as_posix() for p in (report, report.with_suffix('.json'))})

    def test_preserves_client_instructions_documents_and_ignore(self):
        old = b'AI-MODIFIED - 2026-10-01T00:00Z | PME-APPROVED - 2026-10-02T00:00Z\n# Client\nKeep this client rule.\n'
        (self.root / 'AGENTS.md').write_bytes(old)
        (self.root / '.gitignore').write_text('node_modules/\n')
        doc = self.root / 'docs/asdg/02-purpose/README.md'
        doc.parent.mkdir(parents=True); doc.write_text('# Existing purpose\nKeep this content.\n')
        self.init()
        self.assertIn(b'Keep this client rule.', (self.root / 'AGENTS.md').read_bytes())
        self.assertNotIn(b'PME-APPROVED', (self.root / 'AGENTS.md').read_bytes())
        self.assertTrue((self.root / '.gitignore').read_text().startswith('node_modules/\n'))
        self.assertIn('Keep this content.', doc.read_text())
        ledger = json.loads((self.root / '.asdg/document-reviews.json').read_text())
        entry = next(e for e in ledger['events'] if e['path'] == 'AGENTS.md')
        self.assertEqual(entry['previous_state']['sha256'], hashlib.sha256(old).hexdigest())
        self.assertIn('PME-APPROVED', entry['previous_state']['visible_review_markers'][0])
        self.assertIsNone(entry['human_approval'])

    def test_existing_codex_config_conflict_has_no_side_effects(self):
        p = self.root / '.codex/config.toml';p.parent.mkdir();p.write_text('model = "user-choice"\n')
        before = snapshot(self.root)
        self.init(expect=1)
        self.assertEqual(snapshot(self.root), before)

    def test_foreign_binding_and_legacy_data_are_not_overwritten(self):
        p = self.root / '.asdg/project.json';p.parent.mkdir();p.write_text('{"provider":"other"}')
        before = snapshot(self.root)
        self.init(expect=1);self.assertEqual(snapshot(self.root), before)
        shutil.rmtree(p.parent);(self.root / '.asdlc').mkdir()
        before = snapshot(self.root)
        self.init(expect=1);self.assertEqual(snapshot(self.root), before)

    def test_edited_adapter_is_preserved_and_verification_fails(self):
        self.init()
        p=self.root/'.agents/skills/asdg-focus-02-purpose/SKILL.md';p.write_text(p.read_text()+'\nLocal change.\n')
        before=snapshot(self.root)
        self.init(expect=1); self.run_cli('verify', expect=1)
        self.assertEqual(snapshot(self.root), before)

    def test_malformed_or_missing_state_is_never_recreated(self):
        self.init()
        for rel in ('.asdg/sprint.json', '.asdg/lifecycle.json', '.asdg/document-reviews.json'):
            p=self.root/rel; old=p.read_bytes()
            for bad in (b'{bad json', None):
                if bad is None:p.unlink()
                else:p.write_bytes(bad)
                before=snapshot(self.root)
                self.init(expect=1);self.assertEqual(snapshot(self.root), before)
                p.write_bytes(old)

    def test_symlink_destination_is_rejected(self):
        outside=Path(self.area.name)/'outside';outside.mkdir()
        (self.root/'.asdg').symlink_to(outside, target_is_directory=True)
        self.init(expect=1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_relocation_and_subdirectory_invocation(self):
        self.init('--project-status','defining')
        before=snapshot(self.root)
        moved=Path(self.area.name)/"moved client's space";self.root.rename(moved);self.root=moved
        (self.root/'nested').mkdir()
        self.run_cli('verify',cwd=self.root/'nested')
        self.init(cwd=self.root/'nested')
        self.assertEqual(snapshot(self.root),before)
        result=self.hook(self.payload(['app.js']),cwd=self.root/'nested')
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'],'deny')
        for path in (self.root/'.asdg').glob('*.json'):
            self.assertNotIn(str(Path(self.area.name)/'client project'),path.read_text())

    def test_rejects_non_git_and_external_root(self):
        outside=Path(self.area.name)/'outside';outside.mkdir()
        self.init(cwd=outside,expect=1)
        subprocess.run(['git','init','-q',str(outside)],check=True)
        self.init(cwd=outside,expect=1)
        self.assertFalse((outside/'.asdg').exists())

    def test_inactive_sprint_blocks_patch_and_arbitrary_shell(self):
        self.init();before=snapshot(self.root)
        self.denied(self.payload(['app.js']))
        self.denied({'tool_name':'Bash','tool_input':{'command':'echo bad > app.js'},'cwd':str(self.root)})
        self.run_cli('sprint','check-implementation','--path','app.js',expect=1)
        self.assertEqual(snapshot(self.root),before)

    def test_active_sprint_checks_every_path_and_is_preserved(self):
        self.init();self.active()
        self.assertEqual(self.hook(self.payload(['app.js'])),{})
        self.denied(self.payload(['app.js','index.html']))
        before=snapshot(self.root);self.init();self.assertEqual(snapshot(self.root),before)
        self.run_cli('sprint','check-implementation','--path','app.js')
        self.run_cli('sprint','check-implementation','--path','index.html',expect=1)
        self.run_cli('sprint','start','--id','S2','--objective','x','--scope','app.js','--acceptance','x',expect=1)
        self.run_cli('sprint','stop');self.denied(self.payload(['app.js']))

    def test_protected_governance_traversal_and_symlink_scope_blocked(self):
        self.init()
        for target in ('asdg/scripts/cli.py','.asdg/sprint.json','.codex/hooks.json','AGENTS.md','../outside','src/*'):
            self.run_cli('sprint','start','--id','S1','--objective','x','--scope',target,'--acceptance','x',expect=1)
        outside=Path(self.area.name)/'target';outside.write_text('safe')
        (self.root/'linked').symlink_to(outside)
        self.run_cli('sprint','start','--id','S1','--objective','x','--scope','linked','--acceptance','x',expect=1)
        self.assertEqual(outside.read_text(),'safe')

    def test_guard_failure_fallback_and_unknown_tool(self):
        self.init();self.denied({'tool_name':'unknown','tool_input':{}})
        (self.root/'asdg/scripts/hook.py').unlink()
        self.denied(self.payload(['app.js']))

    def test_guard_allows_only_local_factual_status(self):
        self.init()
        base={'tool_name':'Bash','cwd':str(self.root)}
        self.assertEqual(self.hook(dict(base,tool_input={'command':'python3 asdg/scripts/cli.py status --json'})),{})
        self.denied(dict(base,tool_input={'command':'python3 asdg/scripts/cli.py status --verbose'}))
        self.denied(dict(base,tool_input={'command':'python3 asdg/scripts/cli.py sprint stop'}))

    def test_logs_ignored_state_retained_and_no_raw_tool_data(self):
        self.init()
        payload={'hook_event_name':'SubagentStart','agent_type':'asdg_02','agent_id':'child-1',
                 'session_id':'session-1','turn_id':'turn-1','cwd':str(self.root)}
        self.hook(payload,event='SubagentStart');self.hook(payload,event='SubagentStart')
        payload.update(hook_event_name='PostToolUse',tool_name='Bash',tool_use_id='tool-1',
                       tool_input={'command':'sensitive content'},tool_response={'exit_code':0,'output':'private output'})
        self.hook(payload,event='PostToolUse')
        records=self.root/'logs/asdg/session-1/child-1/events.jsonl'
        rows=[json.loads(x) for x in records.read_text().splitlines()]
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['role_id'],'ASDG-02')
        self.assertNotIn('sensitive content',records.read_text());self.assertNotIn('private output',records.read_text())
        for path,code in [('logs/asdg/session-1/child-1/events.jsonl',0),('.asdg/sprint.json',1),('.asdg/document-reviews.json',1)]:
            result=subprocess.run(['git','check-ignore','-q',path],cwd=self.root)
            self.assertEqual(result.returncode,code,path)
        before={p.name:p.read_bytes() for p in (self.root/'.asdg').glob('*.json')}
        shutil.rmtree(self.root/'logs');self.run_cli('verify')
        self.assertEqual(before,{p.name:p.read_bytes() for p in (self.root/'.asdg').glob('*.json')})

    def test_recorded_evidence_and_release_survive_repeat_init(self):
        self.init()
        p=self.root/'docs/asdg/01-context-and-domain-analysis/current/context.md';p.parent.mkdir();p.write_text('# Evidence\nObserved fixture.\n')
        state={'schema_version':1,'project_status':'defining','release':{'release_id':'R1','status':'planning'},
               'stages':{'01':{'artifacts':[p.relative_to(self.root).as_posix()],'not_applicable_reason':None}}}
        (self.root/'.asdg/lifecycle.json').write_text(json.dumps(state))
        before=snapshot(self.root);self.init();self.assertEqual(snapshot(self.root),before)
        report=json.loads(self.run_cli('status','--json').stdout)
        self.assertEqual(report['current_stage']['number'],2);self.assertEqual(report['release_id'],'R1')

    def test_advice_context_and_environment_without_model_call(self):
        self.init()
        text=build_prompt(self.root,{},self.root)
        self.assertIn(str(self.root/'asdg/AGENTS.md'),text)
        self.assertIn(str(self.root/'asdg/docs/lifecycle-baseline.md'),text)
        environment=subprocess_environment({'PATH':'/usr/bin','API_KEY':'not-forwarded'})
        self.assertNotIn('API_KEY',environment)

    def test_transaction_rolls_back_only_its_own_changes(self):
        old=self.root/'client.txt';old.write_text('old')
        changes=[plan(self.root,'new/file.txt',b'new'),plan(self.root,'client.txt',b'changed',replace=True)]
        with patch('cli_files.atomic_replace',side_effect=OSError('injected failure')):
            with self.assertRaises(OSError):apply(changes)
        self.assertFalse((self.root/'new').exists());self.assertEqual(old.read_text(),'old')
        self.assertEqual((self.root/'app.js').read_bytes(),self.app)


if __name__ == '__main__':
    unittest.main()
