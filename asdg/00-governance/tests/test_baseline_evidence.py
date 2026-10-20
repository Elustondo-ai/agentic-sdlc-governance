"""Offline adversarial checks for rejected-output diagnostic retention."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import cli_baseline_evidence as evidence
from cli_files import Conflict


class FailureEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'consumer'
        self.workspace = self.base / 'workspace'
        self.root.mkdir()
        self.unit = self.workspace / 'output/01-topic'
        self.unit.mkdir(parents=True)
        self.relative = evidence.PREFIX / 'offline-run' / '01'
        self.metadata = {'run_id': 'offline-run', 'role_id': 'ASDG-01',
                         'phase': '01', 'failure_phase': 'validation',
                         'session_id': 'offline-session', 'started_at': '2026-10-14T00:00:00Z'}

    def retain(self, **kwargs):
        return evidence.retain_failure(self.root, self.relative, self.workspace,
                                       self.metadata, kwargs.get('diagnostic', {'code': 'CITATION'}),
                                       kwargs.get('runtime', {'stderr': {'text': 'ordinary failure'}}))

    def manifest(self, result):
        return json.loads((self.root / result['manifest_path']).read_text())

    def test_retains_only_expected_text_as_private_unvalidated_evidence_after_cleanup(self):
        note = b'Sources: source/Plan.md\nSee [unknown](external.md).\n'
        (self.unit / 'speaker-notes.md').write_bytes(note)
        (self.unit / 'visual.svg').write_text('<svg><script>alert(1)</script></svg>')
        (self.workspace / 'source').mkdir()
        (self.workspace / 'source/Plan.md').write_text('SOURCE MUST NOT BE COPIED')
        (self.workspace / 'context').mkdir()
        (self.workspace / 'context/auth.json').write_text('AUTH MUST NOT BE COPIED')
        (self.workspace / 'auth.json').write_text('ROOT AUTH MUST NOT BE COPIED')
        (self.workspace / 'role.md').write_text('ROLE MUST NOT BE COPIED')
        result = self.retain()
        shutil.rmtree(self.workspace)
        manifest = self.manifest(result)
        self.assertEqual(len(result['artifacts']), 2)
        self.assertFalse(manifest['validated'])
        self.assertFalse(manifest['promoted'])
        self.assertFalse(manifest['approved'])
        self.assertEqual(manifest['invocation']['session_id'], 'offline-session')
        for entry in result['artifacts']:
            path = self.root / result['path'] / entry['copy']
            self.assertEqual(path.suffix, '.txt')
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(entry['retained_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(stat.S_IMODE((self.root / result['path']).stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((self.root / result['manifest_path']).stat().st_mode), 0o600)
        merged = b'\n'.join(path.read_bytes() for path in (self.root / result['path']).iterdir())
        self.assertNotIn(b'MUST NOT BE COPIED', merged)
        self.assertNotIn(b'PME-APPROVED', merged)
        self.assertFalse((self.root / 'docs/asdg/01-context-and-domain-analysis/baselines').exists())

    def test_rejects_symlinks_hardlinks_nonregular_and_unexpected_files(self):
        outside = self.base / 'private'
        outside.write_text('UNRELATED CANARY CONTENT')
        (self.unit / 'speaker-notes.md').symlink_to(outside)
        os.link(outside, self.unit / 'visual.mmd')
        os.mkfifo(self.unit / 'visual.svg')
        (self.unit / 'credentials.json').write_text('CREDENTIAL CANARY')
        (self.unit / 'nested').mkdir()
        (self.unit / 'nested/speaker-notes.md').write_text('NESTED CANARY')
        (self.workspace / 'output/02-linked').symlink_to(self.unit, target_is_directory=True)
        result = self.retain()
        self.assertEqual(result['artifacts'], [])
        reasons = {item['reason'] for item in result['omissions']}
        self.assertTrue({'unreadable_or_symlink', 'nonregular_or_hardlinked',
                         'unsupported_artifact_path', 'unexpected_unit_or_symlink'} <= reasons)
        self.assertNotIn('CANARY', (self.root / result['manifest_path']).read_text())

    def test_output_symlink_never_followed(self):
        shutil.rmtree(self.workspace / 'output')
        outside = self.base / 'unrelated'
        outside.mkdir()
        (self.workspace / 'output').symlink_to(outside, target_is_directory=True)
        result = self.retain()
        self.assertEqual(result['artifacts'], [])
        self.assertEqual(result['omissions'][0]['reason'], 'output_absent_nonregular_or_symlink')

    def test_sensitive_whole_artifact_binary_and_terminal_controls(self):
        secret = 'sk-proj-' + 's' * 40
        (self.unit / 'speaker-notes.md').write_text('draft\n' + secret)
        (self.unit / 'visual.png').write_bytes(b'\x89PNG\r\n\x1a\nSECRET IMAGE')
        (self.unit / 'visual.mmd').write_text('flowchart LR\nA\x1b[31m --> B\u202e\n')
        result = self.retain(runtime={'stdout': {'text': '\x1b[31m' + secret + '\u202e'}})
        self.assertEqual(len(result['artifacts']), 1)
        reasons = {item['reason'] for item in result['omissions']}
        self.assertIn('sensitive_content_entire_artifact_omitted', reasons)
        self.assertIn('binary_visual_not_retained', reasons)
        merged = '\n'.join(path.read_text() for path in (self.root / result['path']).iterdir())
        self.assertNotIn(secret, merged)
        self.assertNotIn('\x1b', merged)
        self.assertNotIn('\u202e', merged)
        self.assertTrue(result['artifacts'][0]['sanitized'])
        self.assertGreater(self.manifest(result)['record_processing']['redacted'], 0)

    def test_full_scan_precedes_truncation_and_copy_limits_are_explicit(self):
        secret = 'sk-proj-' + 'z' * 40
        (self.unit / 'speaker-notes.md').write_text('A' * 200 + secret)
        (self.unit / 'visual.mmd').write_text('flowchart LR\n' + 'B' * 200)
        with patch.object(evidence, 'MAX_COPY_FILE', 32):
            result = self.retain()
        self.assertEqual(len(result['artifacts']), 1)
        retained = result['artifacts'][0]
        self.assertLessEqual(retained['retained_bytes'], 32)
        self.assertTrue(retained['truncated'])
        self.assertEqual(len(result['truncations']), 1)
        self.assertIn('sensitive_content_entire_artifact_omitted',
                      [item['reason'] for item in result['omissions']])

    def test_entry_artifact_scan_and_total_copy_limits(self):
        (self.unit / 'speaker-notes.md').write_text('A' * 20)
        (self.unit / 'visual.mmd').write_text('B' * 20)
        with patch.object(evidence, 'MAX_ARTIFACTS', 1), patch.object(evidence, 'MAX_COPY_TOTAL', 10):
            result = self.retain()
        self.assertEqual(len(result['artifacts']), 1)
        self.assertEqual(result['artifacts'][0]['retained_bytes'], 10)
        self.assertIn('artifact_limit', [item['reason'] for item in result['omissions']])
        self.relative = evidence.PREFIX / 'offline-run' / '02'
        with patch.object(evidence, 'MAX_SCAN_FILE', 10):
            result = self.retain()
        self.assertEqual(result['artifacts'], [])
        self.assertEqual({item['reason'] for item in result['omissions']}, {'scan_byte_limit'})
        self.relative = evidence.PREFIX / 'offline-run' / '03'
        with patch.object(evidence, 'MAX_ENTRIES', 1):
            result = self.retain()
        self.assertEqual(result['artifacts'], [])
        self.assertEqual(result['omissions'][0]['reason'], 'entry_limit')

    def test_manifest_records_are_bounded_sanitized_and_preservation_is_exclusive(self):
        result = self.retain(runtime={'stdout': {'text': 'x' * 100_000},
                                      'extra': list(range(500))})
        manifest = self.manifest(result)
        self.assertLessEqual(len(manifest['runtime']['stdout']['text']), evidence.MAX_RECORD_STRING)
        self.assertGreater(manifest['record_processing']['truncated'], 0)
        original = (self.root / result['manifest_path']).read_bytes()
        with self.assertRaisesRegex(Conflict, 'already exists'):
            self.retain()
        self.assertEqual((self.root / result['manifest_path']).read_bytes(), original)

    def test_unsafe_destination_and_symlink_parents_never_written(self):
        for bad in (Path('../outside'), self.base / 'outside', evidence.PREFIX / '..' / 'oops',
                    Path('docs/asdg/01-context-and-domain-analysis/baselines/run/01')):
            with self.subTest(path=bad), self.assertRaises(Conflict):
                evidence.retain_failure(self.root, bad, self.workspace, {}, {}, {})
        outside = self.base / 'outside'
        outside.mkdir()
        (self.root / 'docs').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(Conflict):
            self.retain()
        self.assertEqual(list(outside.iterdir()), [])

    def test_preservation_failure_propagates_without_overwriting_other_evidence(self):
        protected = self.root / 'existing.txt'
        protected.write_bytes(b'preserved')
        with patch.object(evidence, '_write', side_effect=OSError('fixture disk failure')):
            with self.assertRaisesRegex(OSError, 'fixture disk failure'):
                self.retain()
        self.assertEqual(protected.read_bytes(), b'preserved')


if __name__ == '__main__':
    unittest.main()
