"""Documentation acceptance stays scoped, explicit and bound to dependencies."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/lib'))
from cli_files import Conflict
from cli_status import evidence_status, read_lifecycle
from stage_review import bundle_hashes, completion_status, validate_reviews


class StageReviewTests(unittest.TestCase):
    def setUp(self):
        area = tempfile.TemporaryDirectory(prefix='asdg-stage-review-')
        self.addCleanup(area.cleanup)
        self.root = Path(area.name)
        self.prefix = Path('docs/asdg/03-system-model-and-use-cases')
        self.folder = self.root / self.prefix
        (self.folder / 'images').mkdir(parents=True)
        (self.folder / 'images/story.png').write_bytes(b'concept image')
        (self.folder / 'images/model.svg').write_text('<svg/>')
        (self.folder / 'model.puml').write_text('@startuml\n@enduml\n')
        (self.folder / 'README.md').write_text('[System](system.md)\n[Scenario](scenario.md)\n')
        (self.folder / 'system.md').write_text(
            '# System\n[Diagram](images/model.svg)\n[Source](model.puml)\n[Scenario](scenario.md)\n')
        (self.folder / 'scenario.md').write_text(
            '# Scenario\n![Desired interaction](images/story.png)\n[System](system.md)\n')
        self.files = [str(self.prefix / p) for p in ('system.md', 'scenario.md')]
        self.entry = {'artifacts': self.files, 'not_applicable_reason': None, 'reviews': []}
        self.rule = {'number': 3, 'slug': self.prefix.name}

    def ready(self):
        event = {'decision': 'READY_FOR_ACCEPTANCE', 'actor': 'ASDG-03',
                 'recorded_at': '2026-10-21T01:00:00Z',
                 'artifacts': bundle_hashes(self.root, self.files, self.prefix),
                 'criteria': {'uml': 'Actors, boundary and source inspected.',
                              'scenarios': 'Flows, visuals and open questions inspected.'}}
        self.entry['reviews'].append(event)
        return event

    def accept(self):
        ready = self.ready()
        self.entry['reviews'].append({
            'decision': 'ACCEPTED', 'actor': 'User', 'recorded_at': '2026-10-21T01:01:00Z',
            'artifacts': dict(ready['artifacts']), 'statement': '$asdg-approve'})

    def status(self):
        return completion_status(self.root, self.entry, '03', self.prefix)

    def test_readiness_is_not_acceptance(self):
        self.assertEqual(self.status()['status'], 'IN_PROGRESS')
        ready = self.ready()
        self.assertIn(str(self.prefix / 'images/story.png'), ready['artifacts'])
        self.assertIn(str(self.prefix / 'model.puml'), ready['artifacts'])
        self.assertEqual(self.status()['status'], 'READY_FOR_ACCEPTANCE')
        self.assertFalse(self.status()['user_accepted'])
        self.accept()
        self.assertTrue(self.status()['user_accepted'])

    def test_changed_picture_diagram_source_or_navigation_invalidates_acceptance(self):
        self.accept()
        for name in ('scenario.md', 'images/story.png', 'images/model.svg', 'model.puml', 'README.md'):
            path = self.folder / name
            before = path.read_bytes()
            with self.subTest(name=name):
                path.write_bytes(before + b'\nchanged')
                self.assertTrue(self.status()['review_stale'])
                self.assertFalse(self.status()['user_accepted'])
            path.write_bytes(before)
        self.assertEqual(self.status()['status'], 'ACCEPTED')

    def test_no_matching_readiness_or_fake_actor_or_wrong_stage(self):
        self.accept()
        valid = copy.deepcopy(self.entry['reviews'])
        variants = [valid[1:], copy.deepcopy(valid), copy.deepcopy(valid)]
        variants[1][-1]['actor'] = 'ASDG-03'
        variants[2][-1]['artifacts']['docs/asdg/02-purpose/purpose.md'] = '0' * 64
        for reviews in variants:
            with self.assertRaises(Conflict):
                validate_reviews(reviews, '03', self.prefix)

    def test_missing_broken_remote_and_escaping_dependencies_fail(self):
        self.accept()
        (self.folder / 'images/story.png').unlink()
        self.assertTrue(self.status()['review_stale'])
        for text in ('[Missing](missing.md)', '![Image](https://example.com/image.png)',
                     '[Escape](../../../../../outside.md)', '![ ](images/model.svg)'):
            (self.folder / 'scenario.md').write_text(text)
            with self.assertRaises(Conflict):
                bundle_hashes(self.root, self.files, self.prefix)

    def test_symlink_is_not_an_approved_asset(self):
        picture = self.folder / 'images/story.png'
        picture.unlink()
        picture.symlink_to(self.folder / 'images/model.svg')
        with self.assertRaises(Conflict):
            bundle_hashes(self.root, self.files, self.prefix)

    def test_outgoing_sources_are_validated_without_approving_another_stage(self):
        source = self.root / 'docs/asdg/02-purpose/purpose.md'
        source.parent.mkdir(parents=True)
        source.write_text('# Purpose\n')
        with (self.folder / 'system.md').open('a') as stream:
            stream.write('[Purpose](../02-purpose/purpose.md)\n')
        self.accept()
        self.assertNotIn(str(source.relative_to(self.root)), self.entry['reviews'][-1]['artifacts'])
        source.unlink()
        self.assertTrue(self.status()['review_stale'])

    def test_state_readback_reports_acceptance_without_mutating_unrelated_state(self):
        self.accept()
        state = {'schema_version': 1, 'project_status': 'defining', 'release': None,
                 'stages': {'03': self.entry}}
        path = self.root / '.asdg/lifecycle.json'
        path.parent.mkdir()
        path.write_text(json.dumps(state))
        before = path.read_bytes()
        loaded = read_lifecycle(self.root, [self.rule])
        stage = evidence_status(self.root, [self.rule], loaded)[0]
        self.assertEqual(stage['readiness'], 'ESTABLISHED')
        self.assertEqual(stage['completion']['status'], 'ACCEPTED')
        self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
