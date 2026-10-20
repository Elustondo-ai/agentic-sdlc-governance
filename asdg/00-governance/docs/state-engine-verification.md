AI-MODIFIED - 2026-10-14T03:10:00Z

# State engine verification

Implementation and tests are confined to `agentic-sdlc-governance`; test projects live in temporary
Git repositories. `agentic-speaker-coach` was not read, upgraded or modified for this change.
No new external dependency, Node/npm project, hosted site, role activation or approval was added.

## Automated regression commands
```sh
python3 -B -m unittest discover -s asdlc/00-governance/tests -p 'test_*.py'
ASDG_NATIVE_CODEX_TESTS=1 python3 -B -m unittest discover \
  -s asdlc/00-governance/tests -p test_codex_sprint_integration.py -v
```
Full discovery: 119 tests, 103 passed, 3 opt-in native skips, 13 existing package setup errors.
The 13 errors are missing `asdlc/README.md`; they are outside this engine change and remain reported.
Relevant CLI/guard/status tests: 57 + 13 + 12 = 82 passed.
Three opt-in native Codex tests passed separately: inactive blocks, active/in-scope permits,
active/out-of-scope blocks. Tests vet generated temporary hooks and use one-off trust bypass;
this does not activate hook trust in any consuming project.
All CLI source files also parse using Python 3.9 grammar; native tests ran with installed Python.

## Engine scenarios covered
Fresh valid structure, inactive sprint and deterministic Stage 01 recommendation;
earliest unmet stage and missing/empty evidence; active sprint identity/scope/criteria;
scope restriction shared with guard; structural errors; CLI/text/JSON agreement;
deterministic next output; planning/implementation/cycle rules; unnecessary POC;
malformed index, README placeholders, unsafe references and symlinks; bridge migration;
shared status queries through the hook allowlist; dashboard rendering and HTML escaping.
Tests distinguish normal policy blocks (status exit 0) from actual errors (exit 1).

## Live dashboard check
A temporary `example-app` repository served at 127.0.0.1:8765.
HTML returned 200. JSON matched `asdg status --json` except the evaluation timestamp.
POST mutation requests returned 501; non-loopback Host headers returned 403.
Chrome preview verified permission, stage, recommendation, scope, criteria, blockers and binding.
The temporary preview server is stopped after verification; it is not a deployed Site.

## Limits
Read [state engine](state-engine.md) and [sprint gate](sprint-gate.md) for policy and trust boundaries.
These tests do not establish semantic evidence quality, approval, an adversarial OS sandbox,
or native hook activation in Speaker Coach. Registration of evidence remains a human operation.
