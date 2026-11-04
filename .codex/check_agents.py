"""Compatibility entry point for canonical portable package validation."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'asdg/scripts'))
from check import main

if __name__ == '__main__':
    sys.exit(main())
