"""One evaluator, deterministic rules, and thin CLI/agent/dashboard views."""
import copy
from io import BytesIO
import json
from unittest.mock import patch

from test_cli_bootstrap import Fixture
from cli_dashboard import make_server, render_dashboard
from cli_hook import shell_read_only
from cli_model import ARTIFACTS
from cli_project import BRIDGE, SPRINT_BRIDGE, initialize
from cli_sprint import check_implementation, start
from cli_status import EMPTY_LIFECYCLE, LIFECYCLE, lifecycle_rules, project_status, render_next, render_status


class StatusTests(Fixture):
    def setUp(self):
        super().setUp()
        self.setup_install()
        initialize(self.project, self.provider)

    def status(self, paths=None):
        return project_status(self.project, self.provider, paths)

    def evidence(self, through):
        value = copy.deepcopy(EMPTY_LIFECYCLE)
        for stage in lifecycle_rules(self.provider)[:through]:
            file = ARTIFACTS / stage['slug'] / 'evidence.md'
            (self.project / file).write_text('Project-specific evidence with sources and open questions.\n')
            value['stages'][f"{stage['number']:02d}"] = {'artifacts': [file.as_posix()], 'not_applicable_reason': None}
        (self.project / LIFECYCLE).write_text(json.dumps(value))
        return value

    def activate(self):
        start(self.project, 'SPRINT-001', 'Hello endpoint', ['app.py'], ['GET /hello returns hello world'])

    def test_a_fresh_init_valid_inactive_blocked_and_context_next(self):
        status = self.status()
        self.assertTrue(status['structure_ok'])
        self.assertEqual(status['sprint_status'], 'inactive')
        self.assertEqual(status['implementation_permission'], 'BLOCKED')
        self.assertEqual(status['recommendation']['code'], 'ESTABLISH_STAGE_01')
        self.assertEqual(status['recommendation']['action'], 'Define project context and domain boundaries.')
        self.assertEqual(status['current_stage']['number'], 1)
        self.assertEqual(status['guard']['runtime_trust'], 'UNKNOWN')
        self.assertEqual(json.loads((self.project / LIFECYCLE).read_text()), EMPTY_LIFECYCLE)

    def test_b_earliest_unmet_stage_and_missing_recorded_file(self):
        for through in range(1, 6):
            self.evidence(through)
            self.assertEqual(self.status()['current_stage']['number'], through + 1)
        value = self.evidence(3)
        context = value['stages']['01']['artifacts'][0]
        (self.project / context).unlink()
        status = self.status()
        self.assertEqual(status['current_stage']['number'], 1)
        self.assertIn(context, status['recommendation']['reason'])
        (self.project / context).write_text(' \n')
        self.assertEqual(self.status()['current_stage']['number'], 1)

    def test_c_active_sprint_fields_and_shared_permission(self):
        self.activate()
        status = self.status()
        self.assertEqual(status['sprint_status'], 'active')
        self.assertEqual(status['sprint_id'], 'SPRINT-001')
        self.assertEqual(status['sprint_scope'], ['app.py'])
        self.assertEqual(status['acceptance_criteria'], ['GET /hello returns hello world'])
        self.assertEqual(status['implementation_permission'], 'ALLOWED_WITHIN_SCOPE')
        self.assertIsNone(status['implementation']['allowed'])
        scoped = self.status(['app.py'])
        self.assertEqual(scoped['implementation_permission'], 'ALLOWED')
        self.assertEqual(check_implementation(self.project, ['app.py'], self.provider),
                         (scoped['implementation']['allowed'], scoped['implementation_reason']))
        # Sprint activation does not fabricate missing lifecycle evidence.
        self.assertEqual(status['current_stage']['number'], 1)

    def test_d_outside_scope_and_structural_error_block_same_guard(self):
        self.activate()
        status = self.status(['other.py'])
        self.assertEqual(status['implementation_permission'], 'BLOCKED')
        self.assertIn('outside active sprint scope', status['implementation_reason'])
        self.assertEqual(check_implementation(self.project, ['other.py'], self.provider),
                         (False, status['implementation_reason']))
        (self.project / 'AGENTS.md').unlink()
        status = self.status(['app.py'])
        self.assertEqual(status['recommendation']['code'], 'REPAIR_STATE')
        self.assertEqual(status['implementation_permission'], 'BLOCKED')
        self.assertTrue(status['errors'])
        self.assertEqual(status['blockers'], status['errors'])

    def test_e_cli_json_and_plain_output_share_model(self):
        result = self.run_cli('status', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertEqual(self.run_cli('status').stdout, render_status(status) + '\n')
        self.assertEqual(self.run_cli('sprint', 'status').stdout, 'No active sprint.\n')
        self.activate()
        result = self.run_cli('status', '--json', '--path', 'other.py')
        self.assertEqual(result.returncode, 0)  # A policy block is not a system malfunction.
        self.assertEqual(json.loads(result.stdout)['implementation_permission'], 'BLOCKED')
        self.assertNotIn('ERROR:', self.run_cli('status').stdout)

    def test_f_dashboard_renders_same_object_and_escapes_content(self):
        status = self.status()
        status['project_name'] = '<script>unsafe</script>'
        status['recommendation']['action'] = 'MODEL RECOMMENDATION SENTINEL'
        status['implementation_permission'] = 'MODEL_PERMISSION_SENTINEL'
        page = render_dashboard(status)
        self.assertIn('MODEL RECOMMENDATION SENTINEL', page)
        self.assertIn('MODEL_PERMISSION_SENTINEL', page)
        self.assertIn('&lt;script&gt;unsafe&lt;/script&gt;', page)
        self.assertNotIn('<script>unsafe</script>', page)
        for field in ('Can I implement?', 'Where am I?', 'What should I do next?',
                      'Why', 'Acceptance criteria', 'CLI version', 'Hook trust'):
            self.assertIn(field, page)

    def test_dashboard_http_routes_use_evaluator_and_offer_no_writes(self):
        # Test actual handler protocol without requiring a listening socket.
        with patch('cli_dashboard.ThreadingHTTPServer') as server, \
                patch('cli_dashboard.project_status', return_value=self.status()) as evaluator:
            make_server(self.project, self.provider)
            handler_type = server.call_args.args[1]
            for route, method, expected in (('/', 'GET', b'200 OK'), ('/status.json', 'GET', b'200 OK'),
                                            ('/sprint/start', 'POST', b'501'), ('/missing', 'GET', b'404')):
                handler = handler_type.__new__(handler_type)
                handler.server = type('Server', (), {'server_port': 8765})()
                handler.client_address = ('127.0.0.1', 1234)
                handler.rfile = BytesIO(f'{method} {route} HTTP/1.1\r\nHost: 127.0.0.1:8765\r\n\r\n'.encode())
                handler.wfile = BytesIO()
                handler.handle_one_request()
                response = handler.wfile.getvalue()
                self.assertIn(expected, response.split(b'\r\n')[0])
                if route == '/status.json':
                    self.assertEqual(json.loads(response.split(b'\r\n\r\n', 1)[1]), evaluator.return_value)
            self.assertEqual(evaluator.call_count, 2)
            evaluator.assert_called_with(self.project, self.provider)

    def test_g_next_is_deterministic_and_same_recommendation(self):
        first, second = self.run_cli('next'), self.run_cli('next')
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stdout, render_next(self.status()) + '\n')
        self.assertIn('01 — Context and Domain Analysis', first.stdout)
        self.assertIn('No active ASDLC sprint is defined.', first.stdout)

    def test_planning_implementation_and_cycle_recommendations(self):
        self.evidence(6)
        self.assertEqual(self.status()['recommendation']['code'], 'DEFINE_SPRINT')
        self.activate()
        self.assertEqual(self.status()['recommendation']['code'], 'ESTABLISH_STAGE_07')
        self.evidence(8)
        self.assertEqual(self.status()['recommendation']['code'], 'IMPLEMENT_WITHIN_SPRINT')
        self.evidence(9)
        self.assertEqual(self.status()['current_stage']['number'], 10)
        self.evidence(12)
        self.assertEqual(self.status()['recommendation']['code'], 'REVIEW_NEXT_CYCLE')

    def test_poc_can_be_unnecessary_but_other_stages_cannot_be_skipped(self):
        value = self.evidence(5)
        value['stages']['06'] = {'artifacts': [], 'not_applicable_reason': 'No experimental uncertainty remains.'}
        (self.project / LIFECYCLE).write_text(json.dumps(value))
        self.assertEqual(self.status()['current_stage']['number'], 7)
        value['stages']['02']['not_applicable_reason'] = 'Skip intent'
        (self.project / LIFECYCLE).write_text(json.dumps(value))
        self.assertTrue(self.status()['errors'])
        self.assertEqual(self.status()['recommendation']['code'], 'REPAIR_STATE')

    def test_bad_evidence_index_readme_symlinks_and_unknown_stage_fail_closed(self):
        self.activate()
        for value in ('invalid json', json.dumps({'schema_version': 1, 'stages': {'99': {}}}),
                      json.dumps({'schema_version': 1, 'stages': {'01': {
                          'artifacts': ['docs/asdlc/01-context-and-domain-analysis/README.md'], 'not_applicable_reason': None}}})):
            (self.project / LIFECYCLE).write_text(value)
            self.assertEqual(self.status()['implementation_permission'], 'BLOCKED')
            self.assertNotEqual(self.run_cli('status').returncode, 0)
            self.assertIn('ERROR:', self.run_cli('status').stdout)
            self.assertNotEqual(self.run_cli('verify').returncode, 0)
        value = self.evidence(1)
        file = self.project / value['stages']['01']['artifacts'][0]
        file.unlink()
        file.symlink_to(self.project / 'app.py')
        self.assertTrue(self.status()['errors'])

    def test_bridge_and_hook_allow_shared_status_queries(self):
        self.assertIn('asdg status --json', BRIDGE)
        self.assertIn('asdg next', BRIDGE)
        for command in ('asdg status --json', 'asdg next', 'asdg verify', 'elustondo-asdlc status'):
            self.assertTrue(shell_read_only(self.project, self.project, command))
        self.assertFalse(shell_read_only(self.project, self.project, 'asdg status; touch app.py'))
        (self.project / 'AGENTS.md').write_text('# Rules\n' + SPRINT_BRIDGE)
        initialize(self.project, self.provider)
        self.assertIn(BRIDGE, (self.project / 'AGENTS.md').read_text())
