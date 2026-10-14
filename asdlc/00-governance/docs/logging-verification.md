AI-MODIFIED - 2026-10-10T14:17:15Z

# Per-agent logging — implementation verification

Status: recorder tests passed here; native Mac/Codex integration still pending.
Environment: Linux, Python 3.13.5.
Scope: added logs folders; no agent names, roles or sandbox permissions changed.

## Executed evidence
18 automated tests passed using synthetic callbacks and temporary repositories.
Coverage includes all 13 catalogue routes and architecture start/stop summaries.
Checks cover follow-up turns, separate sessions, six concurrent writers and deduplication.
Invalid identifiers, missing cwd, wrong workspace and symlink outputs are rejected.
Raw prompts, tool arguments/results and transcript paths are not persisted.
Common-secret redaction and missing/invalid self-report marking were exercised.
Source AGENTS.md files remained unchanged while the recorder ran.
Generated human views and authored Markdown were checked at <=50 physical lines.
Hook JSON parses; lifecycle matchers include exactly the intended 13 role names.
Git check-ignore confirmed generated sessions are ignored in a temporary repository.
The test suite launches no LLM and creates no real agent session record.

## Re-run locally
```sh
python3 -m unittest discover -s asdlc/00-governance/tests -p test_agent_logging.py -v
```
See [native acceptance](logging-acceptance.md) for the required live asdlc_05 interview.
No statement here establishes runtime hook trust, Mac write permission or live coverage.
Source hashes below identify the files tested, not human approval.

## SHA-256 of tested implementation
- `agent_log_event.py`: `88222df897bfa9bc854cb0a6bddc4087cb8da51d37f74a78787a612b5fecd0ac`
- `agent_log_hook.py`: `5e19e8fbcd9484a9e6ffe84b949c18fc6ba9b828025df2302d9996e0c5f98c33`
- `agent_log_store.py`: `f98fa8661e1dfa2b104bccba9f8d477b3a3a3816337aaaba838b1a43f226b142`
- `test_agent_logging.py`: `5fba9d8bd8113ff56f05032830d7c170b023774db9661504d9b996d6ec838c7a`
