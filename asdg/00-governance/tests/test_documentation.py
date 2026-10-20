"""Source-line boundaries, exact-state review preservation and readable generation."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from documentation import (check_length, nonblank_source_lines, review_record,
                           recorded_document, PROVIDER_REVIEWS, PROJECT_REVIEWS)
from test_cli_bootstrap import Fixture
from cli_project import initialize
from cli_baseline_safety import docs_from_output


class DocumentationTests(unittest.TestCase):
    def test_fifty_passes_fifty_one_fails_and_whitespace_is_free(self):
        text = '\n'.join('Readable line ' + str(i) for i in range(50)) + '\n'
        spaced = '\n \t\n'.join(text.splitlines()) + '\n\t\n'
        self.assertEqual(nonblank_source_lines(text), 50)
        self.assertEqual(nonblank_source_lines(spaced), 50)
        check_length(text)
        check_length(spaced)
        with self.assertRaisesRegex(ValueError, '51'):
            check_length(spaced + 'One more substantive line.\n')
        self.assertIn('\n \t\n', spaced)  # Counting never reformats its input.

    def test_code_indentation_and_long_source_lines_count_as_source(self):
        text = '# A title\n\n```python\n    print("hello")\n```\n' + 'word ' * 100
        self.assertEqual(nonblank_source_lines(text), 5)
        self.assertIn('    print', text)

    def test_legacy_approval_is_bound_to_old_bytes_only(self):
        before = b'AI-MODIFIED - 2026-01-01T00:00Z | PME-APPROVED - 2026-01-02T00:00Z\n# Old\n'
        after = b'# A readable title\n\nAn explanation.\n'
        event = review_record('docs/a.md', before, after, '2026-10-19T00:00:00Z')
        self.assertEqual(event['previous_state']['sha256'], hashlib.sha256(before).hexdigest())
        self.assertIn('PME-APPROVED', event['previous_state']['visible_review_markers'][0])
        self.assertEqual(event['sha256'], hashlib.sha256(after).hexdigest())
        self.assertIsNone(event['human_approval'])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'docs/a.md'
            p.parent.mkdir()
            p.write_bytes(after)
            receipt = root / PROVIDER_REVIEWS
            receipt.parent.mkdir(parents=True)
            receipt.write_text(json.dumps({'schema_version': 1, 'events': [event]}))
            self.assertTrue(recorded_document(root, p))
            p.write_bytes(after + b'Changed after recording.\n')
            self.assertFalse(recorded_document(root, p))

    def test_clean_baseline_keeps_evidence_checks_without_machine_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source').mkdir()
            (root / 'source/Plan.md').write_text('Documented aspiration, not observed value.\n')
            unit = root / 'output/01-outcome'
            unit.mkdir(parents=True)
            (unit / 'visual.mmd').write_text('flowchart LR\nA --> B\n')
            notes = unit / 'speaker-notes.md'
            notes.write_text('# Desired outcome\n\nThe plan describes an aspiration; user value is untested.\n\n'
                             '## Limitations and open questions\n\nActual usage is unknown.\n\n'
                             '## Conflicting evidence\n\nNone identified in this evidence set.\n\n'
                             '## Sources\n\nSources: source/Plan.md\n')
            self.assertEqual(len(docs_from_output(root / 'output', {'role_id': 'ASDG-02'},
                                                 evidence_root=root)), 2)
            notes.write_text(notes.read_text().replace('source/Plan.md', 'source/missing.md'))
            with self.assertRaises(ValueError):
                docs_from_output(root / 'output', {'role_id': 'ASDG-02'}, evidence_root=root)


class InitializationReadabilityTests(Fixture):
    def test_new_project_starts_readably_with_hash_bound_receipts(self):
        initialize(self.project, self.provider)
        from cli_model import catalogue, PERSPECTIVES
        for stage in catalogue(self.provider)[0]:
            for view in PERSPECTIVES.values():
                self.assertTrue((self.project / 'docs/asdg' / Path(stage['folder']).name / view).is_dir())
        history = json.loads((self.project / PROJECT_REVIEWS).read_text())
        for p in (self.project / 'docs/asdg').rglob('*.md'):
            text = p.read_text()
            self.assertTrue(text.startswith('# '), p)
            self.assertRegex(text, r'^# [^\n]+\n\n[^#\n]')
            check_length(text)
            entry = next(e for e in history['events'] if e['path'] == p.relative_to(self.project).as_posix())
            self.assertEqual(entry['sha256'], hashlib.sha256(p.read_bytes()).hexdigest())
            self.assertIsNone(entry['human_approval'])
        before = (self.project / PROJECT_REVIEWS).read_bytes()
        initialize(self.project, self.provider)
        self.assertEqual((self.project / PROJECT_REVIEWS).read_bytes(), before)
