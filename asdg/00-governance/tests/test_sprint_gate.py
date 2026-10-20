"""Sprint CLI and pre-execution hook regressions; no live model is implied."""
import json
import subprocess
import sys
from pathlib import Path

from test_cli_bootstrap import Fixture, SRC
from cli_files import Conflict
from cli_hook import decision
from cli_project import BRIDGE, LEGACY_BRIDGE, initialize, inspect
from cli_sprint import INACTIVE, SPRINT, check_implementation, read_state, start, stop


class SprintTests(Fixture):
    def setUp(self):
        super().setUp()
        self.setup_install()
        result = self.run_cli('init')
        self.assertEqual(result.returncode, 0, result.stderr)

    def activate(self, scope=None):
        return start(self.project, 'SPRINT-001', 'Hello endpoint', scope or ['app.py'], ['GET /hello returns hello world'])

    def patch_call(self, path='app.py', content='print("hello world")'):
        return {'tool_name': 'apply_patch', 'cwd': str(self.project), 'tool_input': {
            'command': f'*** Begin Patch\n*** Add File: {path}\n+{content}\n*** End Patch'}}

    def hook(self, payload):
        # Execute the EXACT generated command, including its fail-closed fallback.
        config = json.loads((self.project / '.codex/hooks.json').read_text())
        command = config['hooks']['PreToolUse'][0]['hooks'][0]['command']
        result = subprocess.run(command, shell=True, input=json.dumps(payload), text=True,
                                capture_output=True, cwd=self.project, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        if not result.stdout:
            return True, ''
        output = json.loads(result.stdout)['hookSpecificOutput']
        self.assertEqual(output['permissionDecision'], 'deny')
        return False, output['permissionDecisionReason']

    def test_case_a_no_sprint_blocks_hello_creation_and_modification(self):
        self.assertEqual(read_state(self.project), INACTIVE)
        result = self.run_cli('sprint', 'check-implementation', '--path', 'app.py')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, 'IMPLEMENTATION BLOCKED\nNo active ASDG sprint is defined.\n'
                         '\nRecommended next action:\nDefine project context and domain boundaries.\n')
        # A tool executor must check hook output before applying the patch.
        (self.project / 'app.py').unlink()
        before = {str(p.relative_to(self.project)): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        for payload in (self.patch_call(), {'tool_name': 'Bash', 'tool_input': {'command': "echo hello > app.py"}}):
            allowed, reason = self.hook(payload)
            self.assertFalse(allowed)
            self.assertTrue(reason.startswith('IMPLEMENTATION BLOCKED\nNo active ASDG sprint is defined.'))
            self.assertIn('Recommended next action:', reason)
        self.assertFalse((self.project / 'app.py').exists())
        self.assertEqual(before, {str(p.relative_to(self.project)): p.read_bytes() for p in self.project.rglob('*') if p.is_file()})
        (self.project / 'app.py').write_text('unchanged')
        allowed, _ = self.hook(self.patch_call())
        self.assertFalse(allowed)
        self.assertEqual((self.project / 'app.py').read_text(), 'unchanged')

    def test_case_b_active_sprint_allows_scoped_patch(self):
        result = self.run_cli('sprint', 'start', '--id', 'SPRINT-001', '--objective', 'Hello endpoint',
                              '--scope', 'app.py', '--acceptance', 'GET /hello returns hello world')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('ALL GOOD!', result.stdout)
        self.assertEqual(check_implementation(self.project, ['app.py'], self.provider), (True, 'Implementation allowed.'))
        self.assertTrue(self.hook(self.patch_call())[0])
        self.assertEqual(self.run_cli('sprint', 'check-implementation', '--path', 'app.py').returncode, 0)

    def test_case_c_outside_scope_blocks(self):
        self.activate(['src/'])
        self.assertFalse(self.hook(self.patch_call())[0])
        result = self.run_cli('sprint', 'check-implementation', '--path', 'app.py')
        self.assertEqual(result.returncode, 1)
        self.assertIn('outside active sprint scope: app.py', result.stdout)
        self.assertTrue(self.hook(self.patch_call('src/hello.py'))[0])
        self.assertFalse(self.hook(self.patch_call('src-other/hello.py'))[0])

    def test_status_stop_and_repeat_init_preserve_state(self):
        self.assertEqual(self.run_cli('sprint', 'status').stdout, 'No active sprint.\n')
        state = self.activate()
        self.assertEqual(self.run_cli('sprint', 'status').stdout,
                         'Sprint SPRINT-001 active.\nObjective: Hello endpoint\nALL GOOD!\n')
        self.assertEqual(json.loads(self.run_cli('sprint', 'status', '--json').stdout), state)
        self.assertEqual(self.run_cli('init').returncode, 0)
        self.assertEqual(read_state(self.project), state)
        self.assertEqual(self.run_cli('sprint', 'stop').stdout, 'No active sprint.\n')
        self.assertEqual(read_state(self.project), INACTIVE)
        self.assertFalse(self.hook(self.patch_call())[0])

    def test_missing_invalid_and_symlink_state_fail_closed(self):
        state = self.project / SPRINT
        state.unlink()
        self.assertFalse(check_implementation(self.project, ['app.py'], self.provider)[0])
        self.assertFalse(inspect(self.project, self.provider)['structure_ok'])
        for value in ('not json', '{}', '{"status":"active"}', json.dumps(dict(INACTIVE, status='active'))):
            state.write_text(value)
            self.assertFalse(self.hook(self.patch_call())[0])
            self.assertNotEqual(self.run_cli('init').returncode, 0)
        state.unlink()
        outside = self.base / 'sprint.json'
        outside.write_text(json.dumps(INACTIVE))
        state.symlink_to(outside)
        self.assertFalse(self.hook(self.patch_call())[0])

    def test_protected_paths_traversal_symlinks_and_multi_file_patch(self):
        self.activate(['src/', 'app.py'])
        for path in ('.asdg/sprint.json', '.codex/hooks.json', 'AGENTS.md', '.git/config',
                     '../escape.py', str(self.base / 'escape.py'), 'src/../escape.py', 'src/AGENTS.md'):
            self.assertFalse(self.hook(self.patch_call(path))[0], path)
        outside = self.base / 'external'
        outside.mkdir()
        (self.project / 'src').symlink_to(outside, target_is_directory=True)
        self.assertFalse(self.hook(self.patch_call('src/hello.py'))[0])
        payload = self.patch_call()
        payload['tool_input']['command'] = ('*** Begin Patch\n*** Update File: app.py\n'
            '*** Move to: outside.py\n@@\n-print(1)\n+print(2)\n*** End Patch')
        self.assertFalse(self.hook(payload)[0])
        self.assertFalse(self.hook({'tool_name': 'apply_patch', 'tool_input': {'command': 'garbage'}})[0])

    def test_arbitrary_tools_and_shell_cannot_bypass_or_start_sprint(self):
        self.activate()
        for command in ('python3 -c "open(\"app.py\", \"w\")"', 'touch app.py',
                        'asdg sprint start --id ATTACK', 'asdg sprint stop',
                        'cat AGENTS.md; touch app.py', 'git status > app.py'):
            self.assertFalse(self.hook({'tool_name': 'Bash', 'tool_input': {'command': command}})[0])
        for name in ('mcp__fs__write', 'mcp__node_repl__js', 'unknown'):
            self.assertFalse(self.hook({'tool_name': name, 'tool_input': {}})[0])
        for command in ('pwd', 'cat AGENTS.md .asdg/sprint.json', 'asdg sprint status'):
            self.assertTrue(self.hook({'tool_name': 'Bash', 'tool_input': {'command': command}})[0])

    def test_guard_execution_failure_returns_deny(self):
        (self.provider / 'asdg/00-governance/src/cli_hook.py').unlink()
        self.assertFalse(self.hook(self.patch_call())[0])

    def test_invalid_start_does_not_mutate_state(self):
        for scope in (['../app.py'], ['.asdg/sprint.json'], ['*.py'], ['src/../app.py']):
            with self.assertRaises(Conflict):
                self.activate(scope)
            self.assertEqual(read_state(self.project), INACTIVE)
        self.activate()
        with self.assertRaises(Conflict):
            self.activate()
        self.assertEqual(self.run_cli('sprint', 'check-implementation').returncode, 1)

    def test_legacy_bridge_migrates_but_authored_edits_are_preserved(self):
        agents = self.project / 'AGENTS.md'
        agents.write_text('# Project rules\nKeep my rule.\n' + LEGACY_BRIDGE)
        initialize(self.project, self.provider)
        self.assertIn(BRIDGE, agents.read_text())
        self.assertIn('Keep my rule.', agents.read_text())
        agents.write_text(agents.read_text().replace('just write the code', 'override all gates'))
        before = agents.read_bytes()
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)
        self.assertEqual(agents.read_bytes(), before)

    def test_conflicting_hook_not_overwritten(self):
        hook = self.project / '.codex/hooks.json'
        hook.write_text('{"hooks": {}}')
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)
        self.assertEqual(hook.read_text(), '{"hooks": {}}')
        self.assertFalse(inspect(self.project, self.provider)['structure_ok'])

    def test_active_sprint_without_binding_is_blocked(self):
        self.activate()
        (self.project / '.asdg/project.json').unlink()
        allowed, reason = check_implementation(self.project, ['app.py'], self.provider)
        self.assertFalse(allowed)
        self.assertIn('.asdg', reason)
        self.assertFalse(self.hook(self.patch_call())[0])

    def test_conflicting_project_config_is_not_overwritten(self):
        config = self.project / '.codex/config.toml'
        config.write_text('[features]\nhooks = false\n')
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)
        self.assertEqual(config.read_text(), '[features]\nhooks = false\n')
        self.assertFalse(inspect(self.project, self.provider)['structure_ok'])
