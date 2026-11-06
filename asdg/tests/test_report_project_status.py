"""Exercise packet validation, coverage, platform boundaries and actual provider PowerPoint export."""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.sax.saxutils import escape

CORE = Path(__file__).resolve().parents[1]
SKILL = CORE / 'skills/asdg-report-project-status'
sys.path.insert(0, str(SKILL))
from report_packets import COORDINATOR, KINDS, ordered_report, renderer_preflight

CATALOGUE = json.loads((CORE / '00-governance/types/agent-catalog.json').read_text())


def fixture(owner=COORDINATOR, client='codex'):
    run = dict(run_id='fixture-01', project='report-verification', snapshot='fixture-r1',
               client=client, owner=owner, named_delegation=True, outcomes={})
    for role in reversed(CATALOGUE['agents']):
        rid = role['role_id']
        if not role['stage'] or owner not in (COORDINATOR, rid):
            continue
        slides = [dict(kind=k, headline=f'{rid} / {k}', points=[f'Synthetic {k} evidence'],
                       visual_brief=f'Show the key {k} finding for {role["title"]}.',
                       notes=f'{role["title"]} presents the fixture {k}.', sources=['[Synthetic input](../evidence.md)'])
                  for k in KINDS]
        packet = dict(run_id=run['run_id'], project=run['project'], snapshot=run['snapshot'],
                      role_id=rid, loaded=[role['entry'], role['skill']], slides=slides)
        run['outcomes'][rid] = dict(packet=packet, worker_ref='fixture-attempt-'+rid)
    return run


def author_fixture(run, run_dir):
    """Author the example Markdown and visual sources without renderer imports or build outputs."""
    plan = ordered_report(run, CATALOGUE)
    deck = run_dir / 'presentation'
    deck.mkdir(parents=True)
    images = run_dir / 'images'
    images.mkdir()
    missing = len(plan['missing'])
    total = len(run['outcomes'])
    (images/'coverage.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="52" viewBox="0 0 480 52">'
        '<rect width="480" height="52" rx="6" fill="#e4eeef"/>'
        f'<rect width="{round(480*(total-missing)/total)}" height="7" fill="#168284"/>'
        f'<text x="14" y="36" font-family="sans-serif" font-size="21" fill="#163548">'
        f'{total-missing} of {total} specialist sections returned</text></svg>')
    (deck/'evidence.md').write_text('# Synthetic inputs\n\nThis fixture exercises presentation structure, slide order and references. All specialist returns and coverage outcomes are simulated.\n')
    intro = [f'# {run_dir.name} — project status', '',
             f'Synthetic example · {plan["status"]} coverage · Snapshot {run["snapshot"]}.',
             '![Specialist reporting coverage](../images/coverage.svg)', '',
             '| Slide | Editable visual | Spoken Markdown |', '| --- | --- | --- |']
    for number, slide in enumerate(plan['slides'], 1):
        kind = slide['kind']
        folder = deck / f'{number:02}-{slide["role_id"].lower()}-{kind}'
        folder.mkdir(parents=True)
        if kind == 'coverage':
            title = 'Partial coverage'
            points = [f'{r}: {why}' for r, why in slide['missing'].items()]
            notes, sources = 'These roles did not return a valid packet.', ['[Recorded fixture outcome](../evidence.md)']
        else:
            title, points = slide['headline'], slide['points']
            notes, sources = slide['notes'], slide['sources']
        (folder / 'speaker-notes.md').write_text(f'# {title}\n\n{notes}\n\n## Fine print\n'+'\n'.join(sources)+'\n')
        body = ''.join(f'<text x="72" y="{300+46*i}" font-size="31">{escape(p)}</text>' for i,p in enumerate(points))
        (folder / 'slide.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">'
            '<rect width="1280" height="720" fill="#f5f8fb"/><rect width="16" height="720" fill="#137c83"/>'
            '<g font-family="sans-serif" fill="#163548"><text x="72" y="85" font-size="24">'
            f'ELUSTONDO.AI  /  REPORT TEST FIXTURE  /  {plan["status"]}</text>'
            f'<text x="72" y="218" font-size="58">{escape(title)}</text>{body}'
            f'<text x="72" y="654" font-size="22">Synthetic inputs  ·  slide {number:02}</text></g></svg>')
        intro.append(f'| {number:02} · {title} | ![{title}]({folder.name}/slide.svg) | '
                     f'[Speaker notes]({folder.name}/speaker-notes.md) |')
    intro += ['', 'Edit the numbered slide sources and speaker notes to revise this report. '
              'The final PPTX, preview and build manifest are generated in `build/`.']
    (deck/'README.md').write_text('\n'.join(intro)+'\n')
    return deck


def export_fixture(deck):
    script = renderer_preflight(CORE.parent)['script']
    args = [sys.executable, '-B', script, '--presentation', str(deck), '--narration', 'intro']
    for flags in (['--check'], []):
        subprocess.run(args + flags, capture_output=True, text=True, check=True, timeout=120)
    return deck / 'build' / (deck.name+'.pptx')


class PacketTests(unittest.TestCase):
    def test_full_order_is_independent_of_return_order(self):
        plan = ordered_report(fixture(), CATALOGUE)
        ids = [f'ASDG-{n:02}' for n in range(1, 13)]
        self.assertEqual(plan['status'], 'COMPLETE')
        self.assertEqual([(s['role_id'], s['kind']) for s in plan['slides']],
                         [(rid, k) for rid in ids for k in KINDS])

    def test_partial_and_zero_coverage(self):
        run = fixture()
        run['outcomes']['ASDG-04'] = {'reason': 'timeout'}
        plan = ordered_report(run, CATALOGUE)
        self.assertEqual((plan['status'], len(plan['slides'])), ('PARTIAL', 34))
        self.assertEqual(plan['slides'][-1]['missing'], {'ASDG-04': 'timeout'})
        self.assertFalse(any(s['role_id'] == 'ASDG-04' for s in plan['slides']))
        run['outcomes'] = {r: {'reason': 'unavailable'} for r in run['outcomes']}
        blocked = ordered_report(run, CATALOGUE)
        self.assertEqual((blocked['status'], blocked['slides']), ('BLOCKED', []))

    def test_wrong_or_missing_packet_fields_fail(self):
        for key, value in [('run_id','old'), ('project','other'), ('snapshot','stale'),
                           ('role_id','ASDG-03'), ('loaded',[]), ('slides',[])]:
            with self.subTest(key=key):
                run = fixture('ASDG-02')
                run['outcomes']['ASDG-02']['packet'][key] = value
                with self.assertRaises(ValueError):
                    ordered_report(run, CATALOGUE)

    def test_bad_slide_fails(self):
        for key, value in [('kind','status'), ('notes',' '), ('visual_brief',''), ('points',[]), ('sources',[])]:
            with self.subTest(key=key):
                run = fixture('ASDG-02')
                run['outcomes']['ASDG-02']['packet']['slides'][0][key] = value
                with self.assertRaises(ValueError):
                    ordered_report(run, CATALOGUE)

    def test_unaccounted_role_and_reused_worker_fail(self):
        run = fixture()
        run['outcomes']['ASDG-02']['worker_ref'] = run['outcomes']['ASDG-01']['worker_ref']
        with self.assertRaisesRegex(ValueError, 'distinct'):
            ordered_report(run, CATALOGUE)
        del run['outcomes']['ASDG-02']
        with self.assertRaisesRegex(ValueError, 'explicit outcome'):
            ordered_report(run, CATALOGUE)

    def test_claude_specialist_and_governance_routing(self):
        run = fixture('ASDG-02', 'claude')
        run['outcomes']['ASDG-02'].pop('worker_ref')
        self.assertEqual(len(ordered_report(run, CATALOGUE)['slides']), 3)
        for client in ('claude', 'codex'):
            run = fixture(client=client)
            if client == 'codex':
                run['named_delegation'] = False
            with self.assertRaisesRegex(ValueError, 'delegation unavailable'):
                ordered_report(run, CATALOGUE)

    def test_cli_duplicate_fields_and_absent_renderer(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'input.json'
            file.write_text('{"owner":"a","owner":"b"}')
            cmd = [sys.executable, '-B', str(SKILL/'report_packets.py'), str(file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('duplicate JSON field', result.stderr)
            file.write_text(json.dumps(fixture('ASDG-02')))
            for extra in ([], ['--provider', tmp]):
                result = subprocess.run(cmd+extra, capture_output=True, text=True, check=True)
                self.assertEqual(json.loads(result.stdout)['renderer']['status'], 'UNAVAILABLE')
            self.assertEqual(list(Path(tmp).iterdir()), [file])


class ReportSourceTests(unittest.TestCase):
    def test_read_sources_with_no_build_or_renderer(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)/'example'
            deck = author_fixture(fixture('ASDG-02'), run_dir)
            self.assertFalse((deck/'build').exists())
            index = (deck/'README.md').read_text()
            for link in re.findall(r'\]\(([^)]+)\)', index):
                self.assertTrue((deck/link).resolve().is_file(), link)
            folders = sorted(p for p in deck.iterdir() if p.is_dir())
            self.assertEqual(len(folders), 3)
            for folder in folders:
                self.assertEqual({p.name for p in folder.iterdir()}, {'slide.svg','speaker-notes.md'})
                self.assertIn(folder.name+'/slide.svg', index)
                self.assertIn(folder.name+'/speaker-notes.md', index)
                note = (folder/'speaker-notes.md').read_text()
                self.assertIn('## Fine print', note)
                for link in re.findall(r'\]\(([^)]+)\)', note):
                    self.assertTrue((folder/link).resolve().is_file())
            self.assertTrue((run_dir/'images/coverage.svg').is_file())


class ReportRenderTests(unittest.TestCase):
    @unittest.skipUnless(all(importlib.util.find_spec(k) for k in ('pptx','cairosvg','defusedxml','PIL')),
                         'requires reviewed provider renderer dependencies')
    def test_specialist_full_and_partial_pptx(self):
        from pptx import Presentation
        runs = [fixture('ASDG-02', 'claude'), fixture(), fixture()]
        runs[2]['outcomes']['ASDG-04'] = {'reason': 'timeout'}
        with tempfile.TemporaryDirectory() as tmp:
            for run, count in zip(runs, [3,36,34]):
                with self.subTest(count=count):
                    deck = author_fixture(run, Path(tmp)/f'fixture-{count}')
                    file = export_fixture(deck)
                    pptx = Presentation(file)
                    manifest = json.loads((file.parent/'build-manifest.json').read_text())
                    plan = ordered_report(run, CATALOGUE)
                    self.assertEqual(len(pptx.slides), count)
                    self.assertEqual(manifest['slide_count'], count)
                    self.assertTrue(manifest['notes_round_trip_verified'])
                    for slide, record in zip(pptx.slides, plan['slides']):
                        title = record.get('headline', 'Partial coverage')
                        self.assertEqual(slide.shapes[0].name, title)
                        notes = slide.notes_slide.notes_text_frame.text
                        self.assertIn(record.get('notes', 'These roles did not return'), notes)
                        self.assertIn(record.get('sources', ['[Recorded fixture outcome](../evidence.md)'])[0], notes)

    @unittest.skipUnless(all(importlib.util.find_spec(k) for k in ('pptx','cairosvg','defusedxml','PIL')),
                         'requires reviewed provider renderer dependencies')
    def test_rebuild_after_editing_only_markdown(self):
        from pptx import Presentation
        with tempfile.TemporaryDirectory() as tmp:
            original = author_fixture(fixture('ASDG-02'), Path(tmp)/'original')
            export_fixture(original)
            moved = Path(tmp)/'handed-off'
            shutil.copytree(original.parent, moved, ignore=shutil.ignore_patterns('build'))
            deck = moved/'presentation'
            note = next(deck.glob('02-*/speaker-notes.md'))
            note.write_text(note.read_text().replace('## Fine print','A revised human observation.\n\n## Fine print'))
            before = {p: p.read_bytes() for p in moved.rglob('*') if p.is_file()}
            slides = Presentation(export_fixture(deck)).slides
            self.assertEqual([i+1 for i,s in enumerate(slides)
                              if 'A revised human observation.' in s.notes_slide.notes_text_frame.text], [2])
            self.assertEqual(before, {p: p.read_bytes() for p in moved.rglob('*')
                                      if p.is_file() and 'build' not in p.relative_to(moved).parts})


if __name__ == '__main__':
    unittest.main()
