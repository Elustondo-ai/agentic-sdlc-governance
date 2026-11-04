#!/usr/bin/env python3
"""Project-local ASDG entry point; no machine-wide installation required."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / 'lib'))
from cli import main

if __name__ == '__main__':
    sys.exit(main())
