"""Opt-in native Codex tests. Uses existing login; may consume model usage.

ASDG_NATIVE_CODEX_TESTS=1 python3 -B -m unittest discover \
    -s asdlc/00-governance/tests -p test_codex_sprint_integration.py
Hook trust is bypassed ONLY for the reviewed, isolated test fixture, not installed projects.
"""
import json
import os
import shutil
import signal
import subprocess
import unittest

from test_cli_bootstrap import Fixture
from cli_project import initialize
from cli_sprint import start


@unittest.skipUnless(os.environ.get('ASDG_NATIVE_CODEX_TESTS') == '1', 'opt-in native Codex/model test')
class NativeCodexGateTests(Fixture):
    def setUp(self):
        super().setUp()
        self.assertIsNotNone(shutil.which('codex'), 'Codex CLI is required')
        initialize(self.project, self.provider)
        (self.project / 'app.py').unlink()

    def attempt(self, target):
        args = ['codex', '-a', 'never', 'exec', '--ephemeral', '--json',
                '--dangerously-bypass-hook-trust', '--sandbox', 'workspace-write',
                '-C', str(self.project), '-c', 'projects.' + json.dumps(str(self.project)) + '.trust_level="trusted"',
                f'Test the configured PreToolUse guard. Attempt exactly one apply_patch tool call adding {target} '
                'containing print("hello world"). Do not use other tools. Report whether the tool was blocked.']
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            output, errors = proc.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.communicate(timeout=5)
            self.fail('Native Codex test timed out before completion.')
        self.assertEqual(proc.returncode, 0, errors[-2000:])
        return output, errors

    def test_a_inactive_sprint_blocks_native_write(self):
        output, errors = self.attempt('app.py')
        self.assertFalse((self.project / 'app.py').exists())
        self.assertIn('Command blocked by PreToolUse hook', errors)
        self.assertIn('No active ASDLC sprint is defined.', output + errors)

    def test_b_active_sprint_permits_native_scoped_write(self):
        start(self.project, 'SPRINT-001', 'Create hello-world script', ['app.py'], ['app.py prints hello world'])
        output, _ = self.attempt('app.py')
        self.assertEqual((self.project / 'app.py').read_text().strip(), 'print("hello world")')
        self.assertIn('"file_change"', output)

    def test_c_active_sprint_blocks_native_outside_scope(self):
        start(self.project, 'SPRINT-001', 'Create hello-world script', ['app.py'], ['app.py prints hello world'])
        output, errors = self.attempt('other.py')
        self.assertFalse((self.project / 'other.py').exists())
        self.assertIn('Command blocked by PreToolUse hook', errors)
        self.assertIn('outside active sprint scope: other.py', output + errors)
