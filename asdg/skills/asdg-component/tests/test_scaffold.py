import tempfile, unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from create_component import run, STAGES
class ScaffoldTests(unittest.TestCase):
    def test_creates_and_checks(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d); target=run(repo,'video-builder')
            self.assertEqual(len(STAGES),12)
            self.assertTrue((target/'docs/00-governance/README.md').exists())
            self.assertTrue((target/'types/README.md').exists())
            self.assertTrue((target/'src/README.md').exists())
            self.assertTrue((target/'tests/README.md').exists())
            self.assertEqual(run(repo,'video-builder',True),target)
    def test_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d);run(repo,'video-builder')
            with self.assertRaises(FileExistsError):run(repo,'video-builder')
    def test_rejects_bad_name(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):run(Path(d),'../unsafe')
if __name__=='__main__':unittest.main()
