"""Create disposable clients for observed continuation trials, never real acceptance."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
CORE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE / 'scripts/lib'))
from cli_project import plan_initialization
from cli_files import apply
from purpose_review import CRITERIA, DOCUMENTS, PREFIX, bundle_hashes


def create_fixture(root: Path, scenario: str) -> Path:
    if scenario not in ('empty', 'partial', 'accepted', 'stale'):
        raise ValueError('Unknown continuation fixture scenario.')
    root = root.expanduser().resolve()
    if root.exists():
        raise ValueError('Fixture destination must not exist; existing projects are never overwritten.')
    root.mkdir(parents=True)
    shutil.copytree(CORE, root / 'asdg', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    # Explicitly authorized disposable fixture construction, not the public installer.
    _, changes = plan_initialization(root, repo=root)
    apply(changes)
    (root / 'FIXTURE.txt').write_text(
        'Disposable ASDG continuation exercise. All readiness and acceptance events are simulated.\n'
        'No actual human acceptance, native title change or operational transfer is established.\n')
    folder = root / PREFIX
    if scenario == 'partial':
        (folder / 'draft.md').write_text(
            '# Interview support\n\n'
            'Help job seekers during practice interviews.\n'
            'The first outcome is undecided: remembering the current question or structuring an answer.\n'
            'A transcript display and brief cues are proposed features, not demonstrated outcomes.\n'
            'This substantive draft has not been registered or accepted.\n')
    elif scenario in ('accepted', 'stale'):
        (folder / 'images').mkdir()
        (folder / 'images/vision.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100">'
            '<rect width="400" height="100" fill="white"/>'
            '<text x="12" y="50" fill="black">User sees current question while answering</text></svg>\n')
        (folder / DOCUMENTS[0]).write_text(
            '# Purpose\n\n![Desired experience](images/vision.svg)\n\n'
            'Vision, not verified behavior. Help job seekers keep the current interview question in view while answering.\n'
            'The first outcome is retaining that question, not generating answers.\n'
            'Success question: can the User check the current question without interrupting their answer?\n')
        (folder / DOCUMENTS[1]).write_text(
            '# Current capabilities\n\nNo implementation or operational outcome has been verified in this fixture.\n')
        (folder / DOCUMENTS[2]).write_text(
            '# Planned improvements\n\nDescribe the question-retention interaction and its exceptions next.\n'
            'Answer generation is deferred. No application sprint or release has been authorized.\n')
        (folder / 'README.md').write_text(
            '# Purpose evidence\n\n' + '\n'.join(f'- [{name}]({name})' for name in DOCUMENTS) + '\n')
        artifacts = [(PREFIX / name).as_posix() for name in DOCUMENTS]
        hashes = bundle_hashes(root, artifacts)
        ready = {'decision': 'READY_FOR_ACCEPTANCE', 'actor': 'ASDG-02',
                 'recorded_at': '2026-10-21T12:00:00Z', 'artifacts': hashes,
                 'criteria': {key: 'Simulated fixture assessment for ' + key for key in CRITERIA}}
        accepted = {'decision': 'ACCEPTED', 'actor': 'User', 'recorded_at': '2026-10-21T12:01:00Z',
                    'artifacts': copy.deepcopy(hashes),
                    'statement': 'Role-play fixture only: I accept this Purpose baseline as done for now.'}
        path = root / '.asdg/lifecycle.json'
        state = json.loads(path.read_text())
        state['stages']['02'] = {'artifacts': artifacts, 'not_applicable_reason': None,
                                 'reviews': [ready, accepted]}
        path.write_text(json.dumps(state, indent=2) + '\n')
        if scenario == 'stale':
            path = folder / DOCUMENTS[0]
            path.write_text(path.read_text() + '\nUnreviewed change: generating full answers is now the first outcome.\n')
    return root


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('scenario', choices=('empty', 'partial', 'accepted', 'stale'))
    args = parser.parse_args()
    print(create_fixture(args.destination, args.scenario))
