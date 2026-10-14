AI-MODIFIED - 2026-10-13T19:54:48Z

# ASDG CLI v0.1.2 — Python minimum and regression verification

Minimum compatibility target: Python 3.9+ for the base CLI only.
Status: 51 automated tests passed on Linux, Python 3.13.5.
Native Python 3.9.6, Mac/zsh installation and live Codex execution remain untested here.
A Python 3.9 interpreter was unavailable; download attempts failed in this environment.
Version-gate mocks and Python-3.9 syntax checks are not native-interpreter execution.

## Change and evidence
Both shell entry points and the Python installer now require 3.9 rather than 3.10.
The repository launcher also checks the minimum for non-install commands.
The release value is 0.1.2; no provider/schema identity, catalogue or role ID changed.
The earlier 39 bootstrap tests and eight rename tests all still pass (47 regressions).
Four additional tests cover minimum-version policy, shell consistency and 3.9 syntax.
Mocked version gates accept 3.9.0/3.9.6/3.10.0/3.13.5; reject 3.8.20 before writes.
Actual installer and CLI subprocess tests use the reported Python 3.13.5 interpreter.
Install, init, verify, help, new-shell discovery and repeat execution passed in fixtures.
Tests preserve application files, Git control data, approvals and existing shell content.
Conflict/symlink rejection, backups, rollback, spaces and quotes remain covered.
No changes to the user's Mac, Speaker Coach, native agents, hooks or Git remote occurred.

## Local acceptance still required
After all edited files sync, run ./asdg install with the Mac's python3 3.9.6.
Record the interpreter and the installer result; then verify command discovery.
The complete local regression command is:
```sh
python3 -B -m unittest discover -s asdlc/00-governance/tests -p test_cli_bootstrap.py -v
```
No compatibility or approval is inferred for separate video/runtime dependencies.

## Tested source SHA-256 (evidence, not human approval)
- `asdg`: `561dc5cec2a8080634dd96d1fbc2cc52982fc8edefe10698932c9ef7940006df`
- `install`: `56859abeca4248b46f3130eab9dc004df389b1aca8983e45cf6043b435a5082e`
- `cli.py`: `85880cd1ceed0700e874e79469b4a7f2d68d94f4861e586f8fe0ad665ed9a42e`
- `cli_files.py`: `2d243a86f96f628261a0f6565946e7d94619e76a016e4348d2272589d41386fd`
- `cli_model.py`: `7e26b4126b8f3ea8ff1e658fab02bd6170ac9d3d2db31b0032ac3a6b60e8e53d`
- `cli_project.py`: `05a623c9c82f02cea2b15f525202a7bb3b1ba65b59e1862159cc6b90c6872848`
- `cli_install.py`: `35beda9ac12799ab2703555e12f3c9148480c3b405b946113b70d3395edb3ce9`
- `test_cli_bootstrap.py`: `44be1f4499a7f91b76f59c76eec886aadbfec7ef77e638a304e9aa5277332969`
