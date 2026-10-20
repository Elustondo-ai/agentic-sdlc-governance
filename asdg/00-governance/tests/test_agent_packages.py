"""Structural regression tests. No native agents or external services are invoked."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'asdg/00-governance/src'))
from validate_agents import validate
from documentation import nonblank_source_lines


class AgentPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Copy only the governed packages, not video builds, virtualenvs or unrelated work.
        for p in (ROOT / 'asdg').iterdir():
            if p.is_dir() and p.name[:2].isdigit():
                shutil.copytree(p, self.root / 'asdg' / p.name, ignore=shutil.ignore_patterns('__pycache__'))
        for relative in ['.codex', 'AGENTS.md', 'asdg/README.md', 'docs/status/lifecycle-baseline.md',
                         'asdg/skills/asdg-documentation/SKILL.md']:
            src, dest = ROOT / relative, self.root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dest, ignore=shutil.ignore_patterns('__pycache__'))
            else:
                shutil.copyfile(src, dest)
        self.catalog = self.root / 'asdg/00-governance/types/agent-catalog.json'

    def change_catalog(self, change):
        data = json.loads(self.catalog.read_text())
        change(data)
        self.catalog.write_text(json.dumps(data))

    def assert_fails(self, expected):
        issues = validate(self.root)
        self.assertTrue(any(expected in message for message in issues), issues)

    def test_valid_packages(self):
        self.assertEqual(validate(self.root), [])

    def test_all_thirteen_actual_role_packages_load_for_baseline(self):
        from cli_baseline import instruction_text
        from cli_model import catalogue
        agents, _ = catalogue(self.root)
        self.assertEqual(len(agents), 13)
        for role in agents:
            with self.subTest(role=role['role_id']):
                text = instruction_text(self.root, role)
                self.assertIn(role['role_id'], text)
                self.assertIn('asdg/skills/asdg-documentation/SKILL.md', text)
                self.assertIn('OUT_OF_SCOPE', text)

    def test_operational_and_learning_roles_preserve_separate_boundaries(self):
        ops = (self.root / 'asdg/11-operational-reality-devops-and-user-acceptance/AGENTS.md').read_text()
        learning = (self.root / 'asdg/12-observability-insights-and-learning/AGENTS.md').read_text()
        self.assertIn('Do not deploy or promote releases without explicit authority', ops)
        self.assertIn('Do not silently change scope, implement fixes, or override product priorities', learning)
        self.assertNotEqual(ops, learning)

    def test_missing_package_directory(self):
        shutil.rmtree(self.root / 'asdg/02-purpose/src')
        self.assert_fails('Missing directory')

    def test_missing_skill(self):
        (self.root / 'asdg/02-purpose/skills/elicit-purpose/SKILL.md').unlink()
        self.assert_fails('Invalid entry')

    def test_invalid_native_skill_yaml_is_rejected(self):
        p = self.root / 'asdg/02-purpose/skills/elicit-purpose/SKILL.md'
        p.write_text(p.read_text().replace('description: "', 'description: ', 1))
        self.assert_fails('must be double quoted')

    def test_duplicate_skill_metadata_is_rejected(self):
        p = self.root / 'asdg/02-purpose/skills/elicit-purpose/SKILL.md'
        p.write_text(p.read_text().replace('name: asdg-elicit-purpose',
                     'name: asdg-elicit-purpose\nname: asdg-elicit-purpose', 1))
        self.assert_fails('duplicate role-skill metadata')

    def test_missing_contract(self):
        (self.root / 'asdg/02-purpose/types/contract.md').unlink()
        self.assert_fails('Missing package file')

    def test_duplicate_identity(self):
        self.change_catalog(lambda data: data['agents'][2].update(native_name='asdg_01'))
        self.assert_fails('distinct preserved')

    def test_path_escape(self):
        self.change_catalog(lambda data: data['agents'][2].update(folder='../outside'))
        self.assert_fails('Unsafe repository path')

    def test_read_only_setting(self):
        p = self.root / '.codex/agents/asdg_02.toml'
        p.write_text(p.read_text().replace('"read-only"', '"workspace-write"'))
        self.assert_fails('not read-only')

    def test_legacy_bootstrap_path(self):
        p = self.root / '.codex/agents/asdg_02.toml'
        p.write_text(p.read_text().replace('asdg/02-purpose/AGENTS.md', 'asdg/agents/02-purpose.md'))
        self.assert_fails('flat role path')

    def test_line_limit(self):
        p = self.root / 'asdg/02-purpose/docs/README.md'
        p.write_text(p.read_text() + 'An additional nonblank line.\n' * 51)
        self.assert_fails('50 nonblank source lines')

    def test_missing_baseline(self):
        (self.root / 'docs/status/lifecycle-baseline.md').unlink()
        self.assert_fails('Missing authoritative')

    def test_broken_role_link(self):
        p = self.root / 'asdg/02-purpose/AGENTS.md'
        p.write_text(p.read_text().replace('(types/contract.md)', '(types/missing.md)'))
        self.assert_fails('Broken role link')

    def test_extra_agent(self):
        p = self.root / '.codex/agents/extra.toml'
        p.write_text('name = "extra"\n')
        self.assert_fails('Unexpected or missing')

    def test_legacy_file_duplicate(self):
        p = self.root / 'asdg/agents/02-purpose.md'
        p.parent.mkdir(exist_ok=True)
        p.write_text('Legacy duplicate')
        self.assert_fails('Old flat role definitions')


if __name__ == '__main__':
    unittest.main()
