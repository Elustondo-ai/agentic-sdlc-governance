"""Offline diagnostics checks; citation acceptance policy remains unchanged."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from cli_baseline_diagnostics import SECRET, ValidationDiagnostic, sanitize_record, sanitize_text
from cli_baseline_provenance import validate_provenance
from cli_baseline_safety import docs_from_output
from cli_files import Conflict


class CitationDiagnosticTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'source').mkdir()
        (self.root / 'source/Plan.md').write_text('Existing evidence.\n')
        self.output = self.root / 'output'
        self.unit = self.output / '01-topic'
        self.unit.mkdir(parents=True)
        (self.unit / 'visual.mmd').write_text('flowchart LR\nA --> B\n')
        self.good = ('AI-MODIFIED - 2026-10-14T20:00:00Z\n\n# Observed\n\n'
                     'Agent: ASDLC-01\nSources: source/Plan.md\n'
                     'Uncertainties: None in fixture.\nContradictions: None in fixture.\n')

    def diagnostic(self, text, **kwargs):
        with self.assertRaises(ValidationDiagnostic) as failure:
            validate_provenance(text, self.root, **kwargs)
        self.assertIsInstance(failure.exception, Conflict)
        return failure.exception

    def test_external_citation_reports_original_line_target_and_legacy_message(self):
        citation = '[report](https://user:shortpass@example.invalid/doc?token=shorttoken)'
        failure = self.diagnostic(self.good + '\n' + citation + '\n', artifact_dir=self.unit)
        self.assertEqual(str(failure), 'External or unsupported citation; declare it as an unverified narrative citation.')
        detail = failure.diagnostic
        self.assertEqual(detail['code'], 'BASELINE_CITATION_UNSUPPORTED')
        self.assertEqual(detail['line'], 10)
        self.assertEqual(detail['target'], 'https://[REDACTED]@example.invalid/doc?[REDACTED]')
        self.assertIsNone(detail['artifact'])
        self.assertIn('inline', detail['expected'].lower())
        self.assertIn('Narrative citations:', detail['expected'])
        self.assertIn('snapshot', detail['rule'])

    def test_artifact_relative_path_is_attached_in_both_output_validation_modes(self):
        (self.unit / 'speaker-notes.md').write_text(self.good + '[fake](source/missing.md)\n')
        for owner in ({'role_id': 'ASDLC-01'}, None):
            with self.subTest(owner=owner), self.assertRaises(ValidationDiagnostic) as failure:
                docs_from_output(self.output, owner, evidence_root=self.root)
            self.assertEqual(failure.exception.diagnostic['artifact'], '01-topic/speaker-notes.md')
            self.assertEqual(failure.exception.diagnostic['line'], 9)
            self.assertEqual(failure.exception.diagnostic['target'], 'source/missing.md')
            self.assertEqual(failure.exception.diagnostic['code'], 'BASELINE_CITATION_UNRESOLVED_REFERENCE')

    def test_each_existing_rejection_branch_has_stable_diagnostic_code(self):
        fixtures = (
            ('Sources: source/../outside.md\n', 'UNSAFE_REFERENCE', 1),
            ('Sources: source/missing.md\n', 'UNRESOLVED_REFERENCE', 1),
            ('No declared sources.\n', 'SOURCES_REQUIRED', None),
            ('Sources: source/Plan.md\n[bad]: https://example.invalid\n', 'REFERENCE_STYLE', 2),
            ('Sources: source/Plan.md\nNarrative citations: source/Plan.md\n', 'NARRATIVE_SNAPSHOT', 2),
            ('Sources: source/Plan.md\n<https://example.invalid>\n', 'AUTOLINK', 2),
            ('Sources: source/Plan.md\n[missing](unknown.mmd)\n', 'UNRESOLVED_ARTIFACT', 2),
        )
        for text, code, line in fixtures:
            with self.subTest(code=code):
                detail = self.diagnostic(text, artifact_dir=self.unit).diagnostic
                self.assertEqual(detail['code'], 'BASELINE_CITATION_' + code)
                self.assertEqual(detail['line'], line)
                self.assertTrue(detail['rule'])
                self.assertTrue(detail['expected'])

    def test_symlink_and_irregular_workspace_remain_rejected(self):
        (self.root / 'source/linked.md').symlink_to(self.root / 'source/Plan.md')
        detail = self.diagnostic('Sources: source/linked.md\n').diagnostic
        self.assertEqual(detail['code'], 'BASELINE_CITATION_UNSAFE_PATH')
        self.assertEqual(detail['line'], 1)
        (self.unit / 'linked.mmd').symlink_to(self.unit / 'visual.mmd')
        detail = self.diagnostic('Sources: source/Plan.md\n[linked](linked.mmd)\n', artifact_dir=self.unit).diagnostic
        self.assertEqual(detail['code'], 'BASELINE_CITATION_UNSAFE_PATH')
        self.assertEqual(detail['line'], 2)
        with self.assertRaises(ValidationDiagnostic) as failure:
            validate_provenance('Sources: source/Plan.md\n', self.root / 'missing-workspace')
        self.assertEqual(failure.exception.diagnostic['code'], 'BASELINE_CITATION_WORKSPACE')
        self.assertIsNone(failure.exception.diagnostic['line'])

    def test_offsets_survive_masked_declarations_narrative_and_links(self):
        prefix = ('Sources: source/Plan.md; `source/Plan.md:1`\n'
                  'Narrative citations: https://example.invalid (unverified).\n'
                  'See [evidence](source/Plan.md).\n\n')
        detail = self.diagnostic(prefix + 'See source/missing.md.\n', artifact_dir=self.unit).diagnostic
        self.assertEqual(detail['line'], 5)
        self.assertEqual(detail['target'], 'source/missing.md')
        detail = self.diagnostic(prefix + '[first]\n[second]\n').diagnostic
        self.assertEqual(detail['line'], 5)
        self.assertEqual(detail['code'], 'BASELINE_CITATION_REFERENCE_STYLE')

    def test_supported_citations_and_sources_keep_the_same_result(self):
        text = ('Sources: [plan](source/Plan.md#heading); `source/Plan.md:1`\n'
                '[visual](visual.mmd)\n[here](#heading)\n'
                'Narrative citations: <https://example.invalid/doc> (unverified).\n')
        self.assertEqual(validate_provenance(text, self.root, artifact_dir=self.unit), ['source/Plan.md'])
        (self.unit / 'speaker-notes.md').write_text(self.good + '[visual](visual.mmd)\n')
        self.assertEqual(len(docs_from_output(self.output, {'role_id': 'ASDLC-01'}, evidence_root=self.root)), 2)


class DiagnosticSanitizerTests(unittest.TestCase):
    def test_common_secrets_controls_bidi_and_url_values_are_not_exposed(self):
        key = 'sk-proj-' + 'a' * 24
        payload = ('\x1b[31mred\x1b[0m\x1b]2;unsafe-title\x07\x00\x1f\u202e '
                   + key + ' https://user:smallpass@example.invalid/doc?token=shortquery '
                   'OPENAI_API_KEY=shortkey "password": "smallpwd" Authorization: Bearer smallbearer')
        actual = sanitize_text(payload, 2000)
        for secret in (key, 'smallpass', 'shortquery', 'shortkey', 'smallpwd', 'smallbearer', 'unsafe-title'):
            self.assertNotIn(secret, actual)
        for control in ('\x1b', '\x00', '\x1f', '\u202e'):
            self.assertNotIn(control, actual)
        self.assertIn('red', actual)
        self.assertIn('https://[REDACTED]@example.invalid/doc?[REDACTED]', actual)
        self.assertEqual(sanitize_text('//user:shortpass@example.invalid/doc?token=short'),
                         '//[REDACTED]@example.invalid/doc?[REDACTED]')
        self.assertEqual(sanitize_text('relative.md?credential=smallvalue'), 'relative.md?[REDACTED]')

    def test_private_key_body_is_redacted_and_multiline_is_explicit(self):
        payload = 'before\n-----BEGIN RSA PRIVATE KEY-----\nVERY_PRIVATE_BODY\n-----END RSA PRIVATE KEY-----\nafter\n'
        safe = sanitize_text(payload, 2000, multiline=True)
        self.assertNotIn('VERY_PRIVATE_BODY', safe)
        self.assertEqual(safe, 'before\n[REDACTED PRIVATE KEY]\nafter\n')
        self.assertEqual(sanitize_text('first\r\nsecond\tthird'), 'first second third')
        self.assertEqual(sanitize_text('first\r\nsecond\tthird', multiline=True), 'first\nsecond\tthird')

    def test_diagnostic_fields_are_bounded_and_redaction_precedes_truncation(self):
        secret = 'sk-proj-' + 'z' * 80
        detail = ValidationDiagnostic('Original generic error', code='X' * 200,
                                      target=secret + 'a' * 500, artifact='a' * 500,
                                      rule='r' * 500, expected='e' * 500).diagnostic
        self.assertEqual(len(detail['code']), 80)
        for key in ('target', 'artifact', 'rule', 'expected'):
            self.assertLessEqual(len(detail[key]), 320)
        self.assertNotIn('sk-proj', detail['target'])
        self.assertTrue(detail['target'].startswith('[REDACTED]'))
        self.assertEqual(sanitize_text(b'a\xffb', limit=2), 'a\ufffd')
        self.assertEqual(sanitize_text('value', limit=0), '')

    def test_shared_secret_detection_regex_is_unchanged(self):
        expected = (rb'(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|'
                    rb'-----BEGIN [A-Z ]*PRIVATE KEY-----|'
                    rb'(?i:api[_-]?key|password|secret|access[_-]?token)\s*[:=]\s*[\"\']?[A-Za-z0-9_/+=-]{16,})')
        self.assertEqual(SECRET.pattern, expected)

    def test_record_sanitization_preserves_typed_routing_copy_without_mutating_input(self):
        pem = '-----BEGIN RSA PRIVATE KEY-----\nSYNTHETIC_PRIVATE_BODY\n-----END RSA PRIVATE KEY-----'
        route = {'selected_stages': [1, 2], 'reason': pem,
                 'assignments': [{'stage': 1, 'task': 'Inspect\x1b[31m source\x1b[0m',
                                  'evidence': ['source/Plan.md'], 'details': {'password': 'short',
                                      'note': 'password=shortvalue'}}],
                 'questions': ['https://user:shortpass@example.invalid/?token=shortquery'],
                 'approved': False, 'estimate': 1.5, 'optional': None}
        recorded = sanitize_record(route)
        self.assertEqual(recorded['selected_stages'], [1, 2])
        self.assertEqual(recorded['assignments'][0]['stage'], 1)
        self.assertIs(recorded['approved'], False)
        self.assertIsNone(recorded['optional'])
        self.assertEqual(recorded['estimate'], 1.5)
        self.assertEqual(recorded['reason'], '[REDACTED PRIVATE KEY]')
        self.assertEqual(recorded['assignments'][0]['task'], 'Inspect source')
        self.assertEqual(recorded['assignments'][0]['evidence'], ['source/Plan.md'])
        self.assertEqual(recorded['assignments'][0]['details']['password'], '[REDACTED]')
        self.assertNotIn('shortpass', repr(recorded))
        self.assertNotIn('shortquery', repr(recorded))
        self.assertNotIn('shortvalue', repr(recorded))
        self.assertEqual(route['reason'], pem)
        self.assertIn('\x1b', route['assignments'][0]['task'])

    def test_record_bounds_are_explicit_after_full_value_redaction(self):
        pem = '-----BEGIN RSA PRIVATE KEY-----\n' + 'sensitive' * 400 + '\n-----END RSA PRIVATE KEY-----'
        self.assertEqual(sanitize_record({'result': pem})['result'], '[REDACTED PRIVATE KEY]')
        text = sanitize_record('A' * 5000)
        self.assertLessEqual(len(text), 2048)
        self.assertTrue(text.endswith('[TRUNCATED]'))
        self.assertEqual(len(sanitize_record(list(range(300)))), 129)
        deep = {'nested': None}
        for _ in range(30):
            deep = {'nested': deep}
        self.assertIn('[OMITTED: record limit]', repr(sanitize_record(deep)))


if __name__ == '__main__':
    unittest.main()
