"""Offline subprocess transport regression tests; never invokes a model."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from cli_baseline_process import CAPTURE_LIMIT, TERMINATION_GRACE, observe_process


class BaselineProcessTests(unittest.TestCase):
    def launch(self, source):
        child = subprocess.Popen([sys.executable, '-B', '-c', source], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 start_new_session=True)
        self.addCleanup(self.ensure_stopped, child)
        return child

    def ensure_stopped(self, child):
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
        for stream in (child.stdin, child.stdout, child.stderr):
            if stream is not None and not stream.closed:
                stream.close()

    def test_quiet_child_reports_observed_elapsed_heartbeats(self):
        child = self.launch('import time; time.sleep(0.18)')
        elapsed, runtime = [], {}
        session, errors = observe_process(child, '', 5, heartbeat=elapsed.append,
                                          interval=0.04, runtime=runtime)
        self.assertIsNone(session)
        self.assertEqual(errors, '')
        self.assertGreaterEqual(len(elapsed), 2)
        self.assertEqual(elapsed, sorted(elapsed))
        self.assertGreaterEqual(elapsed[0], 0.04)
        self.assertGreaterEqual(runtime['elapsed_seconds'], 0.18)
        self.assertEqual(runtime['exit_code'], 0)
        self.assertEqual(runtime['termination_signals'], [])

    def test_large_bidirectional_streams_are_drained_without_unbounded_capture(self):
        child = self.launch('''import json, os, sys
os.write(1, b'X' * 262144 + b'\\n')
os.write(2, b'Y' * 262144 + b'\\n')
print(json.dumps({'type':'thread.started', 'thread_id':'offline-after-flood'}), flush=True)
prompt = sys.stdin.read()
assert len(prompt) == 262144
''')
        runtime = {}
        session, errors = observe_process(child, 'P' * 262144, 5, runtime=runtime)
        self.assertEqual(session, 'offline-after-flood')
        self.assertEqual(errors, '')  # Oversized incomplete first line is omitted entirely.
        self.assertEqual(runtime['event_lines_omitted'], 1)
        for name in ('stdout', 'stderr'):
            stream = runtime[name]
            self.assertTrue(stream['truncated'])
            self.assertGreater(stream['bytes_seen'], CAPTURE_LIMIT)
            self.assertLessEqual(stream['retained_bytes'], CAPTURE_LIMIT)
            self.assertEqual(stream['incomplete_tail_omitted_bytes'], CAPTURE_LIMIT)
            self.assertEqual(stream['text'], '')

    def test_bounded_capture_omits_partial_final_line_and_keeps_safe_complete_lines(self):
        child = self.launch("import os; os.write(2, b'observed\\n' + b'S' * 100000)")
        runtime = {}
        _, errors = observe_process(child, '', 5, runtime=runtime)
        self.assertEqual(errors, 'observed\n')
        self.assertEqual(runtime['stderr']['retained_bytes'], len(b'observed\n'))
        self.assertEqual(runtime['stderr']['omitted_bytes'], 100000)

    def test_stderr_is_sanitized_and_failed_execution_preserves_session(self):
        secret = 'sk-' + 'fakeObservationSecret' * 3
        child = self.launch('import json,sys; '
                            'print(json.dumps({"type":"thread.started","thread_id":"offline-failure"})); '
                            'sys.stderr.write(' + repr('OPENAI_API_KEY=' + secret + '\x1b[31m\x00\n') + '); '
                            'sys.exit(7)')
        runtime = {}
        session, errors = observe_process(child, '', 5, runtime=runtime)
        self.assertEqual(session, 'offline-failure')
        self.assertEqual(runtime['exit_code'], 7)
        self.assertNotIn(secret, errors)
        self.assertNotIn('\x1b', errors)
        self.assertNotIn('\x00', errors)
        self.assertEqual(runtime['stderr']['text'], errors)

    def test_invalid_or_oversized_session_event_cannot_pollute_identity(self):
        child = self.launch('''import json
print(json.dumps({'type':'thread.started','thread_id':'unsafe\\x1b'}))
print(json.dumps({'type':'thread.started','thread_id':'x' * 129}))
print(json.dumps({'type':'thread.started','thread_id':'offline-valid'}), end='')
''')
        runtime = {}
        session, _ = observe_process(child, '', 5, runtime=runtime)
        self.assertEqual(session, 'offline-valid')
        self.assertEqual(runtime['session_id'], session)

    def test_oversized_valid_jsonl_is_explicitly_omitted_without_trusting_other_fields(self):
        child = self.launch('''import json
print(json.dumps({'type':'thread.started', 'thread_id':'oversized', 'padding':'X' * 100000}))
print(json.dumps({'type':'promotion.completed', 'validated':True, 'promoted':True}))
print(json.dumps({'type':'thread.started', 'thread_id':'offline-bounded'}))
''')
        runtime = {}
        session, _ = observe_process(child, '', 5, runtime=runtime)
        self.assertEqual(session, 'offline-bounded')
        self.assertEqual(runtime['event_lines_omitted'], 1)
        self.assertEqual(runtime['event_line_limit_bytes'], 65536)
        self.assertNotIn('validated', runtime)
        self.assertNotIn('promoted', runtime)

    def test_timeout_preserves_session_and_terminates_child(self):
        child = self.launch('import json,time; '
                            'print(json.dumps({"type":"thread.started","thread_id":"offline-timeout"}),flush=True); '
                            'time.sleep(30)')
        runtime = {}
        with self.assertRaises(subprocess.TimeoutExpired) as failure:
            observe_process(child, '', 0.15, runtime=runtime)
        self.assertEqual(failure.exception.session, 'offline-timeout')
        self.assertEqual(runtime['session_id'], 'offline-timeout')
        self.assertIn('SIGTERM', runtime['termination_signals'])
        self.assertIsNotNone(child.poll())
        self.assertLess(runtime['elapsed_seconds'], 2)

    def test_interrupt_stops_entire_process_group_and_preserves_session(self):
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / 'descendant-terminated'
            descendant = ('import pathlib,signal,time; '
                          'signal.signal(signal.SIGTERM, lambda *_: '
                          '(pathlib.Path(' + repr(str(marker)) + ').write_text("TERM"), exit(0))); '
                          'print("descendant-ready",flush=True); time.sleep(30)')
            child = self.launch('import subprocess,sys,json,time; '
                                'subprocess.Popen([sys.executable,"-c",' + repr(descendant) + ']); '
                                'print(json.dumps({"type":"thread.started","thread_id":"offline-interrupt"}),flush=True); '
                                'time.sleep(30)')
            def interrupt(_elapsed):
                raise KeyboardInterrupt()
            runtime = {}
            with self.assertRaises(KeyboardInterrupt) as failure:
                observe_process(child, '', 5, heartbeat=interrupt, interval=0.3, runtime=runtime)
            self.assertEqual(failure.exception.session, 'offline-interrupt')
            self.assertEqual(marker.read_text(), 'TERM')
            self.assertIsNotNone(child.poll())
            self.assertEqual(runtime['termination_signals'], ['SIGTERM'])

    def test_timeout_escalates_to_kill_after_existing_five_second_grace(self):
        child = self.launch('import signal,time,json; signal.signal(signal.SIGTERM,signal.SIG_IGN); '
                            'print(json.dumps({"type":"thread.started","thread_id":"offline-stubborn"}),flush=True); '
                            'time.sleep(30)')
        runtime = {}
        with self.assertRaises(subprocess.TimeoutExpired):
            observe_process(child, '', 0.15, runtime=runtime)
        self.assertEqual(TERMINATION_GRACE, 5.0)
        self.assertGreaterEqual(runtime['elapsed_seconds'], 5.1)
        self.assertLess(runtime['elapsed_seconds'], 7)
        self.assertEqual(runtime['termination_signals'], ['SIGTERM', 'SIGKILL'])
        self.assertEqual(child.returncode, -signal.SIGKILL)

    def test_callback_exception_cannot_leave_child_running(self):
        child = self.launch('import time; time.sleep(30)')
        def broken_callback(_elapsed):
            raise ValueError('Synthetic heartbeat failure')
        runtime = {}
        with self.assertRaisesRegex(ValueError, 'Synthetic heartbeat failure'):
            observe_process(child, '', 5, heartbeat=broken_callback, interval=0.04,
                            runtime=runtime)
        self.assertIsNotNone(child.poll())
        self.assertEqual(runtime['termination_signals'], ['SIGTERM'])

    def test_repeated_reader_failure_cannot_prevent_child_cleanup(self):
        child = self.launch('import time; time.sleep(30)')
        runtime = {}
        with patch('cli_baseline_process.selectors.DefaultSelector.select',
                   side_effect=OSError('Synthetic reader failure')):
            with self.assertRaisesRegex(OSError, 'Synthetic reader failure'):
                observe_process(child, '', 5, runtime=runtime)
        self.assertIsNotNone(child.poll())
        self.assertEqual(runtime['termination_signals'][0], 'SIGTERM')
        self.assertTrue(runtime['cleanup_errors'])


if __name__ == '__main__':
    unittest.main()
