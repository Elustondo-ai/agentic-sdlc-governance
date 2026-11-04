"""Exercise the provider wrapper against the actual portable builder."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'asdg/scripts'))
from build_distribution import refresh_manifest
from distribution_files import package_files

spec = importlib.util.spec_from_file_location('prepare_commit', ROOT / 'scripts/prepare_commit.py')
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)


class PrepareCommitTests(unittest.TestCase):
    def setUp(self):
        area = tempfile.TemporaryDirectory(prefix='asdg-prepare-')
        self.addCleanup(area.cleanup)
        self.root = Path(area.name).resolve() / "provider with spaces and 'quote"
        self.core = self.root / 'asdg'
        for source in package_files(ROOT / 'asdg'):
            target = self.core / source.relative_to(ROOT / 'asdg')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        refresh_manifest(self.core)

    def test_refreshes_changed_package_and_rebuilds_identically_on_repeat(self):
        readme = self.core / 'README.md'
        readme.write_text(readme.read_text().replace('# ', '# Updated ', 1))
        wrapper.prepare(self.root)
        version = json.loads((self.core / 'metadata/distribution.json').read_text())['version']
        archive = self.root / ('build/distributions/asdg-' + version + '.zip')
        with zipfile.ZipFile(archive) as zipped:
            self.assertEqual(zipped.read('asdg/README.md'), readme.read_bytes())
        original = archive.read_bytes()
        archive.write_bytes(b'obsolete artifact')
        wrapper.prepare(self.root)
        self.assertEqual(archive.read_bytes(), original)
        self.assertTrue(archive.with_suffix('.zip.sha256').is_file())

    def test_failed_package_check_propagates_without_creating_artifact(self):
        (self.core / 'scripts/init.py').unlink()
        with self.assertRaises(subprocess.CalledProcessError):
            wrapper.prepare(self.root)
        self.assertFalse((self.root / 'build/distributions').exists())

    def test_cli_from_other_directory_reports_failure_for_missing_builder(self):
        script = self.root / 'scripts/prepare_commit.py'
        script.parent.mkdir()
        shutil.copyfile(ROOT / 'scripts/prepare_commit.py', script)
        (self.core / 'scripts/build_distribution.py').unlink()
        result = subprocess.run([sys.executable, '-B', str(script)], cwd=Path(tempfile.gettempdir()),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('PREPARATION FAILED', result.stderr)


if __name__ == '__main__':
    unittest.main()
