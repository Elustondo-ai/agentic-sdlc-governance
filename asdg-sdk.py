#!/usr/bin/env python3
"""Compatibility launcher; use the installed asdg command for normal operation."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / 'asdg/00-governance/src'))
from cli import main


if __name__ == '__main__':
    sys.exit(main())
