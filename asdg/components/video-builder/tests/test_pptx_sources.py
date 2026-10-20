import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from build_piper_video import REPO, select_slides
from pptx_sources import extract, notes_body


class PptxSourceTests(unittest.TestCase):
    def test_intro_five_slides_keep_original_picture_placement(self):
        root = REPO / 'docs/presentations/asdg-introduction'
        deck = root / 'build/asdg-introduction.pptx'
        with tempfile.TemporaryDirectory(dir=root / 'build') as temporary:
            slides = extract(deck, Path(temporary), 1, 5)
            self.assertEqual([s.number for s in slides], [1, 2, 3, 4, 5])
            self.assertEqual(slides[0].pptx_parts['placement_emu']['x'], 447681)
            with ZipFile(deck) as archive:
                for slide in slides:
                    self.assertEqual(slide.narration, notes_body(archive.read(slide.pptx_parts['notes_xml'])))
                    self.assertEqual(slide.visual.read_bytes(), archive.read(slide.pptx_parts['image']))

    def test_existing_deck_preserves_embedded_visuals_and_complete_notes(self):
        root = REPO / 'docs/presentations/codex-agent-skills-and-adapters'
        deck = root / 'build/codex-agent-skills-and-adapters-detailed.pptx'
        with tempfile.TemporaryDirectory(dir=root / 'build') as temporary:
            slides = extract(deck, Path(temporary), 1, 13)
            canonical = select_slides(root, 1, 13, 'detailed')
            self.assertEqual([s.number for s in slides], list(range(1, 14)))
            with ZipFile(deck) as archive:
                for slide, source in zip(slides, canonical):
                    self.assertEqual(slide.visual.read_bytes(), archive.read(slide.pptx_parts['image']))
                    self.assertEqual(slide.narration, source.narration)
                    self.assertEqual(slide.note_files[0].read_text(), source.narration)
            with self.assertRaises(ValueError):
                extract(deck, Path(temporary), 1, 14)

    def test_notes_keep_blank_paragraphs_and_exclude_slide_number_placeholder(self):
        xml = b'''<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
        xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:sp>
        <p:nvSpPr><p:nvPr><p:ph type="body"/></p:nvPr></p:nvSpPr><p:txBody>
        <a:p><a:r><a:t>Complete </a:t></a:r><a:r><a:t>notes.</a:t></a:r></a:p>
        <a:p/><a:p><a:r><a:t>Keep ~/.codex/config.toml.</a:t></a:r></a:p>
        </p:txBody></p:sp><p:sp><p:nvSpPr><p:nvPr><p:ph type="sldNum"/></p:nvPr></p:nvSpPr>
        <p:txBody><a:p><a:r><a:t>9</a:t></a:r></a:p></p:txBody></p:sp></p:notes>'''
        self.assertEqual(notes_body(xml), 'Complete notes.\n\nKeep ~/.codex/config.toml.')
