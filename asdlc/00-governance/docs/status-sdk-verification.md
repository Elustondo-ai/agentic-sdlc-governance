AI-MODIFIED - 2026-10-16T23:29:52Z

# Integrated coordinator status verification

## Environment and compatibility
- Installed in ASDG's recorded interpreter: `../agentic-sandbox/.venv311/bin/python3`.
- Python 3.11.17; `openai-codex==0.163.0`; bundled `openai-codex-cli-bin==0.163.0`.
- Authentication: existing ChatGPT sign-in; no API key created or credential printed.
- SDK 0.163.0 returns a plain `TurnStatus` enum. Comparing it with a string
  rejected completed turns; the adapter now compares its value.
- SDK `config.env` merges inherited variables. The adapter uses a clean execve
  environment, with a nonempty originator, rather than blanking inherited settings.
- PATH Codex 0.162.1 is not used; the SDK's bundled 0.163.0 executable is selected.

## Successful live LLM execution
From the sibling `agentic-speaker-coach` working directory, exact command: `asdg status`.
Exit 0 in 48.0 seconds; factual state was printed before real coordinator advice.
The coordinator recommended human review of the existing Stage 01 baseline
`20261014T205435Z-149579087f` before deciding whether to register lifecycle evidence.
The advice cited actual context artifacts and kept review/registration decisions pending.
Observed thread metadata: Codex 0.163.0; configured model `gpt-6.1-sol`; provider `openai`.
This model field is thread configuration, not independent per-turn execution telemetry.
Before/after comparison covered 2,261 files, including Git metadata and untracked files,
checking content hashes, modification times, modes and symlink targets: no changes.
Sprint remained inactive and implementation remained BLOCKED; no actions were executed.
`asdg status --json --advise` also completed successfully: exit 0 in 60.2 seconds.
It returned one valid JSON object with `advice.status=available`, a review recommendation,
the same SDK/runtime/model metadata, and `ephemeral=true`.
Its separate before/after comparison again found no changes across 2,261 files.
Live JSON thread: `01a1470c-5d03-7503-a4b7-9dd59ee68444`.

## Deterministic and unit verification
`asdg status --json` and `asdg status --facts-only` skipped coordinator invocation.
Repeated factual JSON matched apart from the existing UTC evaluation timestamp.
Those checks also left all project files unchanged.
`../agentic-sandbox/.venv311/bin/python3 -B -m unittest discover -s asdlc/00-governance/tests -q`
ran 212 tests successfully, with 3 opt-in native tests skipped.
Unit tests include actual installed API introspection plus mocked adapter/CLI boundary tests;
they are separate evidence from the successful live LLM execution above.
Local test log: `/tmp/asdg-status-integration-tests.log`.
An existing `agentic-sandbox` dependency conflict (`openai<3` versus installed 3.31.0)
was reported by `pip check` and left unchanged; it did not prevent these SDK checks.
