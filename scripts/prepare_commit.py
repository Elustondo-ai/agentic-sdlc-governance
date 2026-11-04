#!/usr/bin/env python3
"""Regenerate the local portable candidate before each provider commit/push."""
import argparse
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def prepare(root: Path) -> None:
    """Delegate manifest refresh and verified ZIP/checksum generation to the builder."""
    subprocess.run(
        [sys.executable, '-B', str(root / 'asdg/scripts/build_distribution.py'),
         '--refresh-manifest'], cwd=root, check=True,
    )


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        prepare(ROOT)
    except (OSError, subprocess.CalledProcessError) as exc:
        print('PREPARATION FAILED: ' + str(exc), file=sys.stderr)
        return 1
    print('Review and include the refreshed asdg/metadata/MANIFEST.json in your commit.')
    print('ZIP and checksum are under ignored build/distributions/; do not stage them.')
    print('Re-run before every commit/push and after any further package edit.')
    print('This is a working-tree candidate; commit, push and publication are separate human actions.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
