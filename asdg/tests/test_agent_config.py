"""Python 3.9 adapter reader: supported syntax and explicit failure boundaries."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'asdg/scripts/lib'))
from agent_config import flat_strings, loads


class AgentConfigTests(unittest.TestCase):
    def test_current_adapters_on_older_python(self):
        paths = list((ROOT / 'asdg/templates/.codex/agents').glob('*.toml'))
        self.assertEqual(len(paths), 13)
        for path in paths:
            with self.subTest(path=path.name):
                text = path.read_text()
                value = flat_strings(text)
                self.assertEqual(value['name'], path.stem)
                self.assertNotIn('sandbox_mode', value)
                self.assertIn('Do not modify files', value['developer_instructions'])
                self.assertEqual(value, loads(text))

    def test_multiline_and_basic_escapes(self):
        value = flat_strings('name = "asdg_05" # comment\nbody = """\nFirst\nSecond\n"""\n')
        self.assertEqual(value['body'], 'First\nSecond\n')
        self.assertEqual(flat_strings('body = "a\\nb"')['body'], 'a\nb')

    def test_rejects_unknown_syntax_and_duplicate_keys(self):
        for text in ('[agents]\nname = "x"', 'enabled = true', 'name = "x"\nname = "y"'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                flat_strings(text)
