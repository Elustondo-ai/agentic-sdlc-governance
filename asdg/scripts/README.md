# ASDG scripts

Run these entry points from the client Git root using Python 3.9+:

| Script | Purpose |
| --- | --- |
| [init.py](init.md) | Preflight and initialize this embedded distribution |
| [cli.py](cli.md) | Project status, structural verification and sprint operations |
| [hook.py](hook.md) | Configured runtime guard and activity-log callbacks |
| [check.py](check.md) | Validate distribution references and optional delivery integrity |
| [build_distribution.py](build_distribution.md) | Build a verified ZIP from the explicit portable file list |

Each link opens the script's purpose and interface guide.
Browse the [runtime modules](lib/README.md) or the [test guides](../tests/README.md).
The old root-level Python launchers are intentionally removed.
