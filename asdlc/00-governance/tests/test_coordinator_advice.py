"""Coordinator boundary tests; model quality requires a separate live acceptance run."""
import asyncio
import copy
from enum import Enum
import importlib.util
import inspect
import json
import sys
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import cli
import cli_advice as advice

VALID = {'summary': {'action': 'Review the existing context baseline.',
                     'reason': 'Its evidence is not registered.', 'question': 'Who accepts the baseline?'},
         'action': 'Review definition', 'reason': 'Acceptance unknown',
         'evidence': ['.asdlc/lifecycle.json'], 'questions': ['Is the definition accepted?'],
         'uncertainties': ['Acceptance owner is unknown.'],
         'requirements': ['Human review required; handoff proposed only.']}


class AdviceTests(TestCase):
    def test_installed_sdk_contract_when_available(self):
        if importlib.util.find_spec('openai_codex') is None:
            self.skipTest('Optional SDK not installed; no live invocation is claimed')
        from importlib.metadata import version
        from openai_codex import AsyncCodex, AsyncThread
        from openai_codex.types import TurnStatus
        self.assertEqual(version('openai-codex'), advice.SDK_VERSION)
        self.assertFalse(TurnStatus.completed == 'completed')
        self.assertEqual(TurnStatus.completed.value, 'completed')
        self.assertIn('ephemeral', inspect.signature(AsyncCodex.thread_start).parameters)
        self.assertIn('output_schema', inspect.signature(AsyncThread.run).parameters)

    def test_invalid_or_extra_state_rejected(self):
        for raw in ('null', '{}', json.dumps(dict(VALID, project_status='defined')),
                    json.dumps(dict(VALID, evidence='invented'))):
            with self.assertRaises(ValueError):
                advice.validate_advice(raw)

    def test_state_is_not_mutated(self):
        state = {'errors': [], 'project_status': 'defining'}
        before = copy.deepcopy(state)
        with patch('importlib.metadata.version', return_value=advice.SDK_VERSION), \
             patch.object(advice, 'build_prompt', return_value='prompt'), \
             patch.object(advice, '_run', new=AsyncMock(return_value=VALID)):
            result = advice.coordinator_advice(Path('/tmp'), state)
        self.assertEqual(result['status'], 'available')
        self.assertEqual(state, before)

    def test_invalid_state_does_not_invoke_model(self):
        with patch.object(advice, '_run') as run:
            result = advice.coordinator_advice(Path('/tmp'), {'errors': ['invalid']})
        run.assert_not_called()
        self.assertEqual(result['status'], 'unavailable')

    def test_timeout_and_provider_errors_are_honest(self):
        for error in (asyncio.TimeoutError(), RuntimeError('SECRET')):
            with patch('importlib.metadata.version', return_value=advice.SDK_VERSION), \
                 patch.object(advice, 'build_prompt', return_value='prompt'), \
                 patch.object(advice, '_run', new=AsyncMock(side_effect=error)):
                result = advice.coordinator_advice(Path('/tmp'), {'errors': []})
            self.assertEqual(result['status'], 'unavailable')
            self.assertNotIn('SECRET', str(result))

    def test_json_and_facts_only_never_invoke_sdk(self):
        for flags in (['--json'], ['--facts-only']):
            with patch.object(cli, 'project_root', return_value=Path('/tmp')), \
                 patch.object(cli, 'project_status', return_value={'errors': []}), \
                 patch.object(cli, 'render_status', return_value='FACTS'), \
                 patch.object(advice, 'coordinator_advice') as run, \
                 patch('sys.stdout', new_callable=StringIO):
                self.assertEqual(cli.main(['status'] + flags), 0)
                run.assert_not_called()

    def test_sdk_read_only_and_schema_contract(self):
        # SDK 0.163.0 uses a plain Enum, not a string or str-derived Enum.
        class TurnStatus(Enum):
            completed = 'completed'
        recorded = SimpleNamespace(cli_version='0.163.0', model='configured-model',
                                   model_provider='openai', ephemeral=True)
        thread = SimpleNamespace(run=AsyncMock(return_value=SimpleNamespace(
            status=TurnStatus.completed, final_response=json.dumps(VALID), id='turn-id')),
            id='thread-id', read=AsyncMock(return_value=SimpleNamespace(thread=recorded)))
        client = SimpleNamespace(thread_start=AsyncMock(return_value=thread))
        context = AsyncMock()
        context.__aenter__.return_value = client
        factory = SimpleNamespace(config=None)
        def make_client(config):
            factory.config = config
            return context
        fake = SimpleNamespace(AsyncCodex=make_client, CodexConfig=lambda **kw: SimpleNamespace(**kw),
                               Sandbox=SimpleNamespace(read_only='read-only'),
                               ApprovalMode=SimpleNamespace(deny_all='deny-all'))
        binary = SimpleNamespace(bundled_codex_path=lambda: Path('/runtime/codex'), bundled_path_dir=lambda: None)
        with patch.dict(sys.modules, {'openai_codex': fake, 'codex_cli_bin': binary}), \
             patch.dict('os.environ', {'OPENAI_API_KEY': 'SECRET'}):
            result = asyncio.run(advice._run(Path('/tmp'), 'prompt'))
        self.assertEqual({field: result[field] for field in advice.FIELDS}, VALID)
        self.assertEqual(result['runtime']['model'], 'configured-model')
        launch = factory.config.launch_args_override
        self.assertNotIn('SECRET', str(launch))
        self.assertNotIn('OPENAI_API_KEY', str(launch))
        self.assertIn('asdg_coordinator', launch[3])
        self.assertIn('os.execve', launch[3])
        self.assertIn('mcp_servers={}', launch)
        self.assertIn('features.apps=false', launch)
        self.assertEqual(client.thread_start.call_args.kwargs['sandbox'], 'read-only')
        self.assertEqual(client.thread_start.call_args.kwargs['approval_mode'], 'deny-all')
        self.assertTrue(client.thread_start.call_args.kwargs['ephemeral'])
        self.assertEqual(thread.run.call_args.kwargs['output_schema'], advice.SCHEMA)

    def test_missing_or_wrong_sdk_has_actionable_safe_diagnostic(self):
        from importlib.metadata import PackageNotFoundError
        for settings in ({'side_effect': PackageNotFoundError('openai-codex')},
                         {'return_value': '0.162.0'}):
            with patch('importlib.metadata.version', **settings), patch.object(advice, '_run') as run:
                result = advice.coordinator_advice(Path('/tmp'), {'errors': []})
            run.assert_not_called()
            self.assertEqual(result['status'], 'unavailable')
            self.assertIn('openai-codex==0.163.0', result['reason'])
            self.assertIn(sys.executable, result['reason'])

    def test_turn_diagnostic_reports_codes_without_provider_text(self):
        info = SimpleNamespace(model_dump=lambda **kw: {
            'responseTooManyFailedAttempts': {'httpStatusCode': 401, 'detail': 'SECRET'}})
        result = SimpleNamespace(error=SimpleNamespace(codex_error_info=info, message='SECRET'))
        reason = advice.turn_failure(result)
        self.assertIn('HTTP 401', reason)
        self.assertIn('responseTooManyFailedAttempts', reason)
        self.assertNotIn('SECRET', reason)

    def test_cli_advice_modes_preserve_facts_and_gates(self):
        for flags in ([], ['--advise'], ['--json', '--advise']):
            state = {'errors': [], 'implementation_permission': 'BLOCKED', 'sprint_status': 'inactive'}
            before = copy.deepcopy(state)
            with patch.object(cli, 'project_root', return_value=Path('/tmp')), \
                 patch.object(cli, 'project_status', return_value=state), \
                 patch.object(cli, 'render_status', return_value='FACTS'), \
                 patch.object(advice, 'coordinator_advice', return_value=dict(VALID, status='available')) as run, \
                 patch('sys.stdout', new_callable=StringIO) as output:
                self.assertEqual(cli.main(['status'] + flags), 0)
            run.assert_called_once_with(Path('/tmp'), state)
            self.assertEqual(state, before)
            if '--json' in flags:
                result = json.loads(output.getvalue())
                self.assertEqual(result['implementation_permission'], 'BLOCKED')
                self.assertEqual(result['sprint_status'], 'inactive')
                self.assertEqual(result['advice']['action'], VALID['action'])
            else:
                self.assertLess(output.getvalue().index('FACTS'), output.getvalue().index(VALID['summary']['action']))

    def test_unavailable_advice_retains_facts_and_signals_failure(self):
        with patch.object(cli, 'project_root', return_value=Path('/tmp')), \
             patch.object(cli, 'project_status', return_value={'errors': [], 'sprint_status': 'inactive'}), \
             patch.object(advice, 'coordinator_advice', return_value={'status': 'unavailable', 'reason': 'Timeout'}), \
             patch('sys.stdout', new_callable=StringIO) as output:
            self.assertEqual(cli.main(['status', '--json', '--advise']), 1)
        result = json.loads(output.getvalue())
        self.assertEqual(result['sprint_status'], 'inactive')
        self.assertEqual(result['advice']['status'], 'unavailable')

    def test_next_remains_deterministic(self):
        with patch.object(cli, 'project_root', return_value=Path('/tmp')), \
             patch.object(cli, 'project_status', return_value={'errors': []}), \
             patch.object(cli, 'render_next', return_value='NEXT'), \
             patch.object(advice, 'coordinator_advice') as run, \
             patch('sys.stdout', new_callable=StringIO):
            self.assertEqual(cli.main(['next']), 0)
        run.assert_not_called()
