# Repository CLI convenience entry

`bin/asdg` adds the canonical `asdg/scripts/lib` directory to the import path and invokes `cli.main()`.
It keeps the caller's working directory and uses the same policy/status engine as the portable client.
Use Python when the executable bit is unavailable.

| Invocation | Meaning |
| --- | --- |
| `python3 bin/asdg agent list` | Inspect canonical role definitions without starting a session. |
| `python3 asdg/scripts/init.py --client both` | Initialize an extracted distribution inside its client Git root. |
| `python3 asdg/scripts/build_distribution.py` | Build a verified local distribution artifact. |

The old `install`, `migrate-namespace` and `baseline` provider commands are not exposed by this launcher.
Their source and historical tests are retained for separate compatibility work; no global installation is changed.
See [distribution workflow](../asdg/docs/distribution-build.md) for the portable installation contract.
