# ASDG scripts

Run these entry points from the client Git root using Python 3.9+:

| Script | Purpose |
| --- | --- |
| `init.py` | Preflight and initialize this embedded distribution |
| `cli.py` | Project status, structural verification and sprint operations |
| `hook.py` | Configured runtime guard and activity-log callbacks |
| `check.py` | Validate distribution references and optional delivery integrity |

Supporting modules live in `lib/`; automated tests live in `asdg/tests/`.
The old root-level Python launchers are intentionally removed.
