import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from build_piper_video import REPO, select_slides, read_notes, check_media


class PiperVideoTests(unittest.TestCase):
    def test_full_detailed_range_and_coverage(self):
        root = REPO / 'docs/presentations/codex-agent-skills-and-adapters'
        slides = select_slides(root, 9, 13, 'detailed')
        self.assertEqual([s.number for s in slides], [9, 10, 11, 12, 13])
        for slide in slides:
            self.assertEqual(len(slide.note_files), 3)
            self.assertEqual(slide.narration, '\n\n'.join(read_notes(p)[1] for p in slide.note_files))
        self.assertIn('~/.codex/config.toml', slides[0].narration)
        self.assertIn('Personal Agent System Registry', slides[-1].narration)

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            select_slides(REPO / 'docs/presentations/codex-agent-skills-and-adapters', 13, 9, 'detailed')

    def test_rejects_missing_audio_and_truncated_duration(self):
        with patch('build_piper_video.probe', return_value={
                'streams': [{'codec_type': 'video'}], 'format': {'duration': '10'}}):
            with self.assertRaises(RuntimeError):
                check_media(Path('test.mp4'), 10)
        with patch('build_piper_video.probe', return_value={
                'streams': [{'codec_type': 'video'}, {'codec_type': 'audio'}],
                'format': {'duration': '9'}}):
            with self.assertRaises(RuntimeError):
                check_media(Path('test.mp4'), 10)
