"""Synthetic hook-contract tests. These do not launch or impersonate a live agent."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from agent_log_hook import handle
from agent_log_event import normalize

CATALOG = Path(__file__).resolve().parents[1] / 'types/agent-catalog.json'


class AgentLoggingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.catalog = json.loads(CATALOG.read_text())
        p = self.repo / 'asdlc/00-governance/types/agent-catalog.json'
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps(self.catalog))
        for role in self.catalog['agents']:
            p = self.repo / role['entry']
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('# Synthetic test contract: ' + role['native_name'])
        self.arch = self.repo / self.catalog['agents'][5]['folder']
        self.p = {'hook_event_name': 'SubagentStart', 'session_id': 'test-parent',
                  'agent_id': 'test-child', 'agent_type': 'asdlc_05',
                  'turn_id': 'test-turn', 'cwd': str(self.repo), 'permission_mode': 'plan'}

    def rows(self, directory=None):
        directory = directory or self.arch
        return [json.loads(l) for p in directory.rglob('events.jsonl') for l in p.read_text().splitlines()]

    def test_start_and_stop(self):
        r = handle(self.p, self.repo)
        self.assertIn('additionalContext', r['hookSpecificOutput'])
        report = {'request_summary': 'Implement this design', 'outcome': 'OUT_OF_SCOPE',
                  'summary': 'Returned implementation request to parent for coordinator routing.',
                  'artifacts_read': ['docs/architecture.md'], 'artifacts_written': [],
                  'skills_used': [], 'handoff_state': 'requested'}
        p = dict(self.p, hook_event_name='SubagentStop', last_assistant_message=
                 'Public answer\n```asdlc-log\n' + json.dumps(report) + '\n```')
        handle(p, self.repo)
        rows = self.rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[-1]['outcome'], 'OUT_OF_SCOPE')
        self.assertEqual(rows[-1]['evidence_kind'], 'agent_self_report')
        self.assertEqual(rows[-1]['stop_semantics'], 'turn_stopped_not_session_closed')
        summary = next(self.arch.rglob('session.md')).read_text()
        self.assertLessEqual(len(summary.splitlines()), 50)

    def test_all_thirteen_routes(self):
        for role in self.catalog['agents']:
            handle(dict(self.p, agent_type=role['native_name']), self.repo)
            self.assertEqual(len(self.rows(self.repo/role['folder'])), 1)

    def test_followup_keeps_child_log(self):
        handle(self.p, self.repo)
        handle(dict(self.p, hook_event_name='SubagentStop'), self.repo)
        handle(dict(self.p, hook_event_name='SubagentStop', turn_id='test-turn2'), self.repo)
        self.assertEqual(len(list(self.arch.rglob('events.jsonl'))), 1)
        self.assertEqual(len(self.rows()), 3)

    def test_parallel_instances_are_separate(self):
        handle(self.p, self.repo)
        handle(dict(self.p, agent_id='other-child'), self.repo)
        handle(dict(self.p, session_id='other-parent'), self.repo)
        self.assertEqual(len(list(self.arch.rglob('events.jsonl'))), 3)

    def test_duplicate_delivery_is_idempotent(self):
        handle(self.p, self.repo)
        handle(self.p, self.repo)
        self.assertEqual(len(self.rows()), 1)

    def test_never_store_raw_inputs_outputs_or_transcript(self):
        p = dict(self.p, hook_event_name='PostToolUse', tool_name='Bash', tool_use_id='call1',
                 tool_input={'command': 'echo sk-SUPERSECRET'},
                 tool_response={'stdout':'PRIVATE_OUTPUT', 'exit_code':1},
                 transcript_path='/private/path', prompt='PRIVATE_PROMPT')
        handle(p, self.repo)
        content = next(self.arch.rglob('events.jsonl')).read_text()
        for bad in ['SUPERSECRET', 'PRIVATE_OUTPUT', '/private/path', 'PRIVATE_PROMPT']:
            self.assertNotIn(bad, content)
        self.assertEqual(self.rows()[0]['exit_code'], 1)

    def test_redact_report_and_drop_unknown_fields(self):
        r = {'outcome':'OK', 'summary':'token=PRIVATE sk-SECRETXYZ',
             'reasoning':'PRIVATE_REASONING', 'artifacts_read':['../escape','/etc/passwd','.env','docs/a.md']}
        handle(dict(self.p, hook_event_name='SubagentStop', last_assistant_message=
                    'Do not store my full answer PRIVATE_ANSWER\n```asdlc-log\n' + json.dumps(r)+'\n```'), self.repo)
        row = self.rows()[0]
        self.assertEqual(row['artifacts_read'], ['docs/a.md'])
        text = json.dumps(row)
        for bad in ['PRIVATE_REASONING','PRIVATE_ANSWER','SECRETXYZ','PRIVATE']:
            self.assertNotIn(bad,text)

    def test_missing_summary_is_not_invented(self):
        handle(dict(self.p, hook_event_name='SubagentStop', last_assistant_message='Done'),self.repo)
        self.assertEqual(self.rows()[0]['report_state'],'missing')
        self.assertNotIn('outcome',self.rows()[0])

    def test_bad_summary_is_flagged(self):
        handle(dict(self.p, hook_event_name='SubagentStop', last_assistant_message='```asdlc-log\n{bad}\n```'),self.repo)
        self.assertEqual(self.rows()[0]['report_state'],'invalid')

    def test_non_asdlc_and_unattributed_tools_are_ignored(self):
        self.assertEqual(handle(dict(self.p,agent_type='explorer'),self.repo),{})
        self.assertEqual(handle(dict(self.p,hook_event_name='PostToolUse',agent_id=None),self.repo),{})
        self.assertEqual(handle(dict(self.p,hook_event_name='SessionStart'),self.repo),{})
        self.assertFalse(list(self.repo.rglob('events.jsonl')))

    def test_reject_path_traversal_identifier(self):
        with self.assertRaises(ValueError):
            handle(dict(self.p,agent_id='../../escape'),self.repo)
        self.assertFalse(list(self.repo.rglob('events.jsonl')))

    def test_reject_wrong_workspace(self):
        with self.assertRaises(ValueError):
            handle(dict(self.p,cwd='/'),self.repo)

    def test_reject_symlink_logs(self):
        (self.arch/'logs').symlink_to(self.repo/'asdlc/00-governance',target_is_directory=True)
        with self.assertRaises(ValueError):
            handle(self.p,self.repo)

    def test_contract_is_unchanged(self):
        before={p:p.read_bytes() for p in self.repo.rglob('AGENTS.md')}
        handle(self.p,self.repo)
        self.assertEqual(before,{p:p.read_bytes() for p in before})

    def test_no_secret_in_failure_output(self):
        p=subprocess.run([sys.executable,str(SRC/'agent_log_hook.py')],input=b'{"bad":"SECRET"',capture_output=True)
        self.assertEqual(p.returncode,1)
        self.assertNotIn(b'SECRET',p.stdout+p.stderr)
        self.assertIn('systemMessage',json.loads(p.stdout))

    def test_reject_missing_cwd(self):
        with self.assertRaises(ValueError):
            handle(dict(self.p,cwd=''),self.repo)

    def test_unidentified_deliveries_are_not_silently_merged(self):
        p=dict(self.p,hook_event_name='PostToolUse',tool_name='Bash',turn_id=None)
        handle(p,self.repo)
        handle(p,self.repo)
        self.assertEqual(len(self.rows()),2)

    def test_concurrent_writers_remain_valid(self):
        # Different turn ids simulate independent callbacks writing the same child log.
        script = 'import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from agent_log_hook import handle;handle(json.loads(sys.argv[2]),Path(sys.argv[3]))'
        processes=[]
        for i in range(6):
            payload=dict(self.p,hook_event_name='PostToolUse',turn_id='turn'+str(i),tool_name='Bash',tool_use_id='call'+str(i))
            processes.append(subprocess.Popen([sys.executable,'-c',script,str(SRC),json.dumps(payload),str(self.repo)],stdout=subprocess.PIPE,stderr=subprocess.PIPE))
        for p in processes:
            stdout,stderr=p.communicate(timeout=10)
            self.assertEqual(p.returncode,0,stderr.decode())
        self.assertEqual([r['sequence'] for r in self.rows()],list(range(1,7)))


if __name__=='__main__':
    unittest.main()
