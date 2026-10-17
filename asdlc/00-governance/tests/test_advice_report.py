"""Console/report contracts and bounded writes; LLM execution is mocked here."""
import copy
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from test_cli_bootstrap import Fixture
from test_coordinator_advice import VALID
import cli
import cli_advice as advice
import cli_advice_report as report
from cli_files import Conflict
from cli_model import BINDING, catalogue
from cli_project import initialize
from cli_status import project_status

RUNTIME = dict(sdk_version='0.163.0', cli_version='0.163.0', model='configured-model',
               model_provider='openai', model_basis='THREAD_CONFIGURATION',
               thread_id='thread-id', turn_id='turn-id', sandbox='read-only',
               approval_mode='deny-all', ephemeral=True)


class ReportTests(Fixture):
    def setUp(self):
        super().setUp()
        self.setup_install()
        initialize(self.project, self.provider)
        self.status = project_status(self.project, self.provider)
        self.advice = dict(copy.deepcopy(VALID), status='available', runtime=RUNTIME)

    def invoke(self, flags, result=None, save_error=None):
        with patch.object(cli, 'project_root', return_value=self.project), \
             patch.object(cli, 'project_status', return_value=self.status), \
             patch.object(advice, 'coordinator_advice', return_value=result or self.advice) as run, \
             patch.object(report, 'save_advice', wraps=report.save_advice) as save, \
             patch('sys.stdout', new_callable=StringIO) as output:
            if save_error:
                save.side_effect = save_error
            code = cli.main(['status'] + flags)
        return code, output.getvalue(), run, save

    def test_concise_console_omits_detail_and_shows_one_question(self):
        self.advice['questions'] = ['Detailed first question?', 'Detailed second question?']
        code, output, run, save = self.invoke([])
        self.assertEqual(code, 0)
        self.assertIn('Recommended action: ' + VALID['summary']['action'], output)
        self.assertIn('Reason: ' + VALID['summary']['reason'], output)
        self.assertEqual(output.count('Question:'), 1)
        for value in (VALID['action'], VALID['reason'], '.asdlc/lifecycle.json', 'Runtime:', 'thread-id'):
            self.assertNotIn(value, output)
        run.assert_called_once()
        save.assert_not_called()

    def test_verbose_saves_same_result_in_canonical_folder(self):
        before = {p: p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        code, output, run, save = self.invoke(['--verbose'])
        self.assertEqual(code, 0, output)
        run.assert_called_once_with(self.project, self.status)
        save.assert_called_once_with(self.project, self.status, self.advice)
        files = [p for p in self.project.rglob('*') if p.is_file() and p not in before]
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].parent, report.advice_destination(self.project, self.provider))
        self.assertIn(str(files[0]), output)
        document = files[0].read_text()
        self.assertLessEqual(len(document.splitlines()), 50)
        self.assertRegex(document, r'^AI-MODIFIED - \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ\n')
        self.assertIn('not an approved plan', document)
        self.assertNotIn('PME-APPROVED', document)
        for value in (VALID['action'], VALID['reason'], VALID['evidence'][0],
                      VALID['requirements'][0], VALID['uncertainties'][0], 'configured-model',
                      self.status['evaluated_at'], self.status['sprint_status']):
            self.assertIn(value, document)
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data, str(path))

    def test_json_verbose_is_one_valid_object(self):
        code, output, run, save = self.invoke(['--json', '--advise', '--verbose'])
        value = json.loads(output)
        self.assertEqual(code, 0, output)
        self.assertEqual(value['advice'], self.advice)
        self.assertEqual(value['advice_report']['status'], 'saved')
        self.assertTrue(Path(value['advice_report']['path']).is_file())
        run.assert_called_once()
        save.assert_called_once()

    def test_invalid_combinations_fail_before_model_or_project_access(self):
        for flags in (['--facts-only', '--verbose'], ['--json', '--verbose']):
            with patch.object(cli, 'project_root') as root, \
                 patch('sys.stderr', new_callable=StringIO) as output:
                with self.assertRaises(SystemExit) as raised:
                    cli.main(['status'] + flags)
            self.assertEqual(raised.exception.code, 2)
            self.assertIn('--verbose', output.getvalue())
            root.assert_not_called()

    def test_no_report_or_write_when_advice_unavailable(self):
        for flags in (['--verbose'], ['--json', '--advise', '--verbose']):
            code, output, run, save = self.invoke(flags, {'status': 'unavailable', 'reason': 'Timed out.'})
            self.assertEqual(code, 1)
            run.assert_called_once()
            save.assert_not_called()
            self.assertIn('unavailable', output.lower())
            if '--json' in flags:
                value = json.loads(output)
                self.assertEqual(value['advice_report']['status'], 'not_saved')
                self.assertNotIn('path', value['advice_report'])
        self.assertFalse(report.advice_destination(self.project, self.provider).exists())

    def test_save_failure_does_not_hide_successful_advice_or_claim_saved(self):
        for flags in (['--verbose'], ['--json', '--advise', '--verbose']):
            code, output, run, save = self.invoke(flags, save_error=PermissionError('Read-only directory'))
            self.assertEqual(code, 1)
            run.assert_called_once()
            save.assert_called_once()
            self.assertIn('Could not save advisory report', output)
            self.assertNotIn('Advisory report: ', output)
            if '--json' in flags:
                value = json.loads(output)
                self.assertEqual(value['advice']['status'], 'available')
                self.assertEqual(value['advice_report']['status'], 'failed')
                self.assertNotIn('path', value['advice_report'])

    def test_filenames_unique_even_with_same_timestamp(self):
        fixed = datetime(2026, 10, 16, 12, 34, 56, tzinfo=timezone.utc)
        with patch.object(report, 'datetime') as clock:
            clock.now.return_value = fixed
            first = report.save_advice(self.project, self.status, self.advice, self.provider)
            second = report.save_advice(self.project, self.status, self.advice, self.provider)
        self.assertNotEqual(first, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertTrue(first.name.startswith('status-20261016T123456000000Z-'))

    def test_collision_never_overwrites_existing_report(self):
        fixed = datetime(2026, 10, 16, 12, 34, 56, tzinfo=timezone.utc)
        with patch.object(report, 'datetime') as clock, \
             patch.object(report, 'uuid4', return_value=SimpleNamespace(hex='a' * 32)):
            clock.now.return_value = fixed
            first = report.save_advice(self.project, self.status, self.advice, self.provider)
            before = first.read_bytes()
            with self.assertRaises(Conflict):
                report.save_advice(self.project, self.status, self.advice, self.provider)
        self.assertEqual(first.read_bytes(), before)
        self.assertEqual(list(first.parent.iterdir()), [first])

    def test_publish_failure_leaves_no_partial_report_or_temporary_file(self):
        destination = report.advice_destination(self.project, self.provider)
        with patch.object(report.os, 'link', side_effect=OSError('Storage failure')):
            with self.assertRaises(OSError):
                report.save_advice(self.project, self.status, self.advice, self.provider)
        self.assertFalse(destination.exists())

    def test_line_limit_rejected_before_creating_destination(self):
        for key, limit in (('action', 400), ('reason', 600)):
            self.advice[key] = ('word ' * limit)[:limit]
        for key in ('questions', 'uncertainties', 'requirements'):
            self.advice[key] = [('word ' * 40)[:200]] * 2
        self.advice['evidence'] = [('word ' * 80)[:400]] * 4
        with self.assertRaisesRegex(Conflict, '50 readable lines'):
            report.save_advice(self.project, self.status, self.advice, self.provider)
        self.assertFalse(report.advice_destination(self.project, self.provider).exists())

    def test_destination_comes_from_catalogue_capability_and_binding(self):
        agents, digest = catalogue(self.provider)
        planning = next(a for a in agents if a.get('skill_name') == 'asdlc-prepare-plan')
        planning['folder'] = 'asdlc/catalogue-planning'
        path = self.project / BINDING
        project = json.loads(path.read_text())
        project['stages'].append('catalogue-planning')
        path.write_text(json.dumps(project))
        folder = self.project / project['artifacts_root'] / 'catalogue-planning'
        folder.mkdir()
        (folder / 'README.md').write_text('Canonical planning artifacts.\n')
        with patch.object(report, 'catalogue', return_value=(agents, digest)):
            self.assertEqual(report.advice_destination(self.project, self.provider), folder / 'advice')

    def test_rejects_symlink_destinations_and_foreign_artifact_root(self):
        destination = report.advice_destination(self.project, self.provider)
        outside = self.base / 'outside'
        outside.mkdir()
        destination.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(Conflict):
            report.save_advice(self.project, self.status, self.advice, self.provider)
        destination.unlink()
        path = self.project / BINDING
        project = json.loads(path.read_text())
        for target in ('../outside', str(outside)):
            project['artifacts_root'] = target
            path.write_text(json.dumps(project))
            with self.assertRaises(Conflict):
                report.save_advice(self.project, self.status, self.advice, self.provider)
        self.assertFalse(list(outside.iterdir()))

    def test_invalid_summary_is_rejected(self):
        for value in ('One. Two. Three.', 'line\nbreak', 'See docs/asdlc/context.md', 'x' * 321):
            candidate = copy.deepcopy(VALID)
            candidate['summary']['action'] = value
            with self.assertRaises(ValueError):
                advice.validate_advice(json.dumps(candidate))
