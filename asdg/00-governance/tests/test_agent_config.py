"""Python 3.9 adapter reader: supported syntax and explicit failure boundaries."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'asdg/00-governance/src'))
from agent_config import flat_strings, loads


class AgentConfigTests(unittest.TestCase):
    def test_current_adapters_on_older_python(self):
        for path in (ROOT / '.codex/agents').glob('*.toml'):
            with self.subTest(path=path.name):
                text = path.read_text()
                value = flat_strings(text)
                self.assertEqual(value['name'], path.stem)
                self.assertEqual(value['sandbox_mode'], 'read-only')
                self.assertEqual(value, loads(text))

    def test_multiline_and_basic_escapes(self):
        value = flat_strings('name = "asdg_05" # comment\nbody = """\nFirst\nSecond\n"""\n')
        self.assertEqual(value['body'], 'First\nSecond\n')
        self.assertEqual(flat_strings('body = "a\\nb"')['body'], 'a\nb')

    def test_rejects_unknown_syntax_and_duplicate_keys(self):
        for text in ('[agents]\nname = "x"', 'enabled = true', 'name = "x"\nname = "y"'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                flat_strings(text)
