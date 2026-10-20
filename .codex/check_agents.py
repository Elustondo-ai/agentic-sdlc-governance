"""Compatibility entry point for the canonical folder-based agent validator."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'asdg/00-governance/src'))
from validate_agents import main

if __name__ == '__main__':
    sys.exit(main())
