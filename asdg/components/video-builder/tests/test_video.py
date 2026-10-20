import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from build_video import clean_markdown,slides_at
class VideoTests(unittest.TestCase):
    def test_markdown_clean(self):
        self.assertEqual(clean_markdown('AI-MODIFIED - x\n# Title\n\nHello **world**.'),'Hello world.')
    def test_slide_discovery(self):
        root=Path(__file__).resolve().parents[4]/'docs'/'presentations'/'codex-agent-skills-and-adapters'
        result=slides_at(root)
        self.assertEqual(len(result),13)
        self.assertEqual(len(result[0][2]),3)
    def test_order(self):
        root=Path(__file__).resolve().parents[4]/'docs'/'presentations'/'codex-agent-skills-and-adapters'
        result=slides_at(root)
        self.assertTrue(result[0][3].index('This chapter is about') < result[0][3].index('Read the three columns'))
if __name__=='__main__':unittest.main()
