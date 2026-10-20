"""Reproduce the explicitly synthetic no-model rejection example in a new directory."""
from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'asdlc/00-governance/tests'))
sys.path.insert(0, str(REPO / 'asdlc/00-governance/src'))
import cli_baseline
from cli_files import Conflict
from test_baseline import BaselineFixture, MOCK_CODEX


def generate(destination):
    destination.mkdir(mode=0o700, parents=True, exist_ok=False)
    fixture = BaselineFixture()
    fixture.setUp()
    stdout, stderr, workspaces = io.StringIO(), io.StringIO(), []
    original = cli_baseline.fresh_workspace
    def remember(*args, **kwargs):
        workspace = original(*args, **kwargs)
        workspaces.append(workspace)
        return workspace
    try:
        fixture.fake.write_text(MOCK_CODEX.replace('[1,2,5]', '[1,4,5,8,11]').replace(
            'prompt = sys.stdin.read()', 'prompt = sys.stdin.read(); import time; time.sleep(0.09)').replace(
            'Sources: source/Plan.md\\n',
            'Sources: source/Plan.md\\nSee [unsupported](https://example.invalid/evidence).\\n'))
        failure = None
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr), \
                patch('cli_baseline.HEARTBEAT_SECONDS', 0.03), \
                patch('cli_baseline.fresh_workspace', side_effect=remember):
            try:
                fixture.call_capture()
            except Conflict as exc:
                failure = str(exc)
        assert failure and 'External or unsupported citation' in failure
        receipt = next(fixture.root.rglob('*__baseline-run.json'))
        report = json.loads(receipt.read_text())
        invocation = report['invocations'][-1]
        bundle = Path(invocation['diagnostic_bundle'])
        assert report['written_artifacts'] == [] and invocation['promoted_artifacts'] == 0
        assert workspaces and all(not p.exists() for p in workspaces)
        assert stdout.getvalue() == ''
        shutil.copytree(bundle, destination / 'bundle', copy_function=shutil.copy2)
        (destination / 'console.txt').write_text(stderr.getvalue())
        (destination / 'stdout.txt').write_text(stdout.getvalue())
        shutil.copy2(receipt, destination / 'receipt.json')
        description = dict(synthetic=True, no_model=True, origin='offline BaselineFixture fake executable',
            original_failed_experiment_reconstructed=False, heartbeat_seconds=0.03,
            production_heartbeat_seconds=cli_baseline.HEARTBEAT_SECONDS,
            selected_stages=report['selected_stages'], failure=failure,
            original_bundle=str(bundle), retained_bundle='bundle', workspace_cleanup_confirmed=True,
            validated_artifacts=invocation['validated_artifacts'], promoted_artifacts=0,
            note='Original temporary paths in byte-for-byte records no longer exist; review copy is bundle/.')
    finally:
        fixture.doCleanups()
    description['fixture_cleanup_confirmed'] = not fixture.path.exists()
    (destination / 'example.json').write_text(json.dumps(description, indent=2) + '\n')
    print(json.dumps(description, indent=2))


if __name__ == '__main__':
    generate(Path(sys.argv[1]).resolve())
