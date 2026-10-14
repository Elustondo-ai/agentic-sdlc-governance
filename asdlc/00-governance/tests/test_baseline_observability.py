"""Offline end-to-end observability; all child executables are synthetic doubles."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from cli_files import Conflict
from test_baseline import BaselineFixture, MOCK_CODEX


class ObservabilityTests(BaselineFixture):
    def rejected_citation(self):
        self.fake.write_text(MOCK_CODEX.replace('Sources: source/Plan.md\\n',
            'Sources: source/Plan.md\\nSee [unsupported](https://example.invalid/evidence).\\n'))

    def failure_receipt(self):
        return json.loads(next(self.root.rglob('*__baseline-run.json')).read_text())

    def test_quiet_heartbeat_and_stage_progress_stay_on_stderr(self):
        self.fake.write_text(MOCK_CODEX.replace('prompt = sys.stdin.read()',
                                               'prompt = sys.stdin.read(); import time; time.sleep(0.09)'))
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr), \
                patch('cli_baseline.HEARTBEAT_SECONDS', 0.02):
            report = self.call_capture(max_agents=2)
        self.assertEqual(stdout.getvalue(), '')
        progress = stderr.getvalue()
        for text in ('ASDLC-COORDINATOR', 'Coordinator routing', 'Selected specialists (2)',
                     'Stage 01: Context and Domain Analysis', 'Stage 02: Intent', 'Specialist 1 of 2',
                     'Specialist 2 of 2', 'Task: Capture stage evidence', 'still running; elapsed',
                     'execution completed', 'validation passed; 2 artifacts validated',
                     'promotion completed; 2 artifacts', 'Coordinator synthesis', 'Log:'):
            self.assertIn(text, progress)
        self.assertNotIn('%', progress)
        for invocation in report['invocations']:
            self.assertEqual(invocation['execution_status'], 'OK')
            self.assertEqual(invocation['validation_status'], 'OK')
            self.assertIn(invocation['promotion_status'], ('OK', 'NOT_APPLICABLE'))
            self.assertGreater(invocation['elapsed_seconds'], 0)

    def test_cli_json_stdout_remains_a_single_report(self):
        import cli
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch('cli.project_root', return_value=self.root), \
                patch('cli_baseline.capture', side_effect=lambda *a, **kw: self.call_capture(max_agents=1)), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = cli.main(['baseline', 'capture', '--source', str(self.source), '--json'])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(stdout.getvalue())['status'], 'PARTIAL_CAPTURE_NEEDS_HUMAN_REVIEW')
        self.assertIn('Coordinator routing', stderr.getvalue())
        self.assertNotIn('execution started', stdout.getvalue())

    def test_recorded_model_results_and_routing_are_sanitized_without_changing_assignment(self):
        import cli_baseline
        body = 'SYNTHETIC_PRIVATE_KEY_BODY'
        pem = '-----BEGIN RSA PRIVATE KEY-----\n' + body + '\n-----END RSA PRIVATE KEY-----'
        task = 'Capture stage evidence; password=synthetic-short-secret\x1b[31m'
        extra = "\nif 'selected_stages' in message:\n" + \
                '    message["reason"] = ' + repr(pem) + '\n' + \
                '    message["assignments"][0]["task"] = ' + repr(task) + '\n' + \
                '    message["debug"] = {"token": "synthetic-short-token", "key": ' + repr(pem) + '}\n' + \
                'else:\n    message["result"] = ' + repr(pem) + '\n'
        self.fake.write_text(MOCK_CODEX.replace('last.write_text(json.dumps(message))',
                                               extra + '\nlast.write_text(json.dumps(message))'))
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), \
                patch('cli_baseline.documentation_prompt', wraps=cli_baseline.documentation_prompt) as prompt:
            report = self.call_capture(max_agents=1)
        self.assertEqual(prompt.call_args_list[0].args[2], task)
        self.assertEqual(report['selected_stages'], [1])
        self.assertEqual(report['routing_plan']['assignments'][0]['stage'], 1)
        self.assertEqual(report['routing_plan']['debug']['token'], '[REDACTED]')
        evidence = json.dumps(report) + stderr.getvalue() + ''.join(
            p.read_text() for p in (self.root / 'docs').rglob('*') if p.is_file())
        for value in (body, 'synthetic-short-secret', 'synthetic-short-token', '\x1b'):
            self.assertNotIn(value, evidence)
        self.assertIn('[REDACTED PRIVATE KEY]', evidence)

    def test_precise_citation_bundle_survives_workspace_cleanup_without_promotion(self):
        self.rejected_citation()
        import cli_baseline
        workspaces = []
        original = cli_baseline.fresh_workspace
        def remember(*args, **kwargs):
            path = original(*args, **kwargs)
            workspaces.append(path)
            return path
        stderr = io.StringIO()
        with patch('cli_baseline.fresh_workspace', side_effect=remember), contextlib.redirect_stderr(stderr):
            with self.assertRaisesRegex(Conflict, 'External or unsupported citation'):
                self.call_capture(max_agents=1)
        self.assertTrue(workspaces)
        self.assertTrue(all(not p.exists() for p in workspaces))
        report = self.failure_receipt()
        failure = report['invocations'][-1]
        self.assertEqual(failure['execution_status'], 'OK')
        self.assertEqual(failure['validation_status'], 'ERROR')
        self.assertEqual(failure['promotion_status'], 'SKIPPED')
        self.assertEqual(failure['failure_phase'], 'validation')
        diagnostic = failure['diagnostic']
        self.assertEqual(diagnostic['code'], 'BASELINE_CITATION_UNSUPPORTED')
        self.assertEqual(diagnostic['artifact'], '01-topic/speaker-notes.md')
        self.assertEqual(diagnostic['line'], 7)
        self.assertEqual(diagnostic['target'], 'https://example.invalid/evidence')
        self.assertEqual(diagnostic['run_id'], report['run_id'])
        self.assertEqual(diagnostic['session_id'], failure['session_id'])
        self.assertTrue(diagnostic['expected'])
        bundle = Path(failure['diagnostic_bundle'])
        manifest = json.loads((bundle / 'manifest.json').read_text())
        self.assertEqual(manifest['diagnostic'], diagnostic)
        self.assertEqual(manifest['invocation']['failure_phase'], 'validation')
        self.assertEqual(manifest['runtime']['exit_code'], 0)
        self.assertFalse(manifest['validated'] or manifest['promoted'] or manifest['approved'])
        self.assertEqual(len(manifest['artifacts']), 2)
        rejected = ''.join((bundle / a['copy']).read_text() for a in manifest['artifacts'])
        self.assertIn('https://example.invalid/evidence', rejected)
        self.assertEqual(report['written_artifacts'], [])
        self.assertEqual(failure['artifacts'], [])
        self.assertFalse(list((self.root / 'docs').rglob('speaker-notes.md')))
        self.assertIn('01-topic/speaker-notes.md:7', stderr.getvalue())
        self.assertIn(str(bundle), stderr.getvalue())

    def test_runtime_failure_is_distinct_and_retains_sanitized_streams(self):
        secret = 'sk-' + 'SyntheticFailureCredential' * 2
        snippet = "    sys.stderr.write(" + repr('api_key=' + secret + '\x1b[31m\x00\n') + "); sys.exit(9)\n"
        self.fake.write_text(MOCK_CODEX.replace("    message = {'role_id':rid", snippet + "    message = {'role_id':rid"))
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaisesRegex(Conflict, 'Codex failed'):
            self.call_capture(max_agents=1)
        failure = self.failure_receipt()['invocations'][-1]
        self.assertEqual(failure['failure_phase'], 'execution')
        self.assertEqual(failure['execution_status'], 'ERROR')
        self.assertEqual(failure['validation_status'], 'NOT_STARTED')
        self.assertEqual(failure['diagnostic']['code'], 'BASELINE_EXECUTION_FAILED')
        self.assertIsNotNone(failure['session_id'])
        bundle = Path(failure['diagnostic_bundle'])
        manifest = json.loads((bundle / 'manifest.json').read_text())
        self.assertEqual(manifest['runtime']['exit_code'], 9)
        self.assertIn('[REDACTED]', manifest['runtime']['stderr']['text'])
        evidence = stderr.getvalue() + ''.join(p.read_text() for p in (self.root / 'docs').rglob('*') if p.is_file())
        for value in (secret, '\x1b', '\x00'):
            self.assertNotIn(value, evidence)

    def test_bundle_preservation_error_does_not_hide_validation_failure(self):
        self.rejected_citation()
        stderr = io.StringIO()
        with patch('cli_baseline.retain_failure', side_effect=OSError('synthetic evidence disk failure')), \
                contextlib.redirect_stderr(stderr), self.assertRaisesRegex(Conflict, 'External or unsupported citation'):
            self.call_capture(max_agents=1)
        failure = self.failure_receipt()['invocations'][-1]
        self.assertEqual(failure['diagnostic']['code'], 'BASELINE_CITATION_UNSUPPORTED')
        self.assertEqual(failure['evidence_preservation_error']['code'], 'BASELINE_EVIDENCE_PRESERVATION_FAILED')
        self.assertIn('Evidence preservation FAILED separately', stderr.getvalue())
        self.assertIn('synthetic evidence disk failure', stderr.getvalue())
        self.assertEqual(self.failure_receipt()['written_artifacts'], [])

    def test_cli_json_failure_keeps_stdout_empty(self):
        import cli
        self.rejected_citation()
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch('cli.project_root', return_value=self.root), \
                patch('cli_baseline.capture', side_effect=lambda *a, **kw: self.call_capture(max_agents=1)), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = cli.main(['baseline', 'capture', '--source', str(self.source), '--json'])
        self.assertEqual(status, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assertIn('validation FAILED', stderr.getvalue())
        self.assertEqual(json.loads(stderr.getvalue().splitlines()[-1])['operation'], 'baseline')


if __name__ == '__main__':
    unittest.main()
