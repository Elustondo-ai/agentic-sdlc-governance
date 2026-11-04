#!/usr/bin/env python3
"""Initialize this distribution's client repository, using only the standard library."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / 'lib'))
from cli import main

if __name__ == '__main__':
    sys.exit(main(['init', *sys.argv[1:]]))
