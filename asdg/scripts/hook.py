#!/usr/bin/env python3
"""Portable hook entry; output root comes from this installed file, never event data."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'asdg/scripts/lib'))

if __name__ == '__main__':
    if sys.argv[1:] == ['log']:
        from agent_log_hook import main
        sys.exit(main())
    if sys.argv[1:]:
        sys.exit('Unsupported hook operation')
    from cli_hook import main
    sys.exit(main(ROOT))
