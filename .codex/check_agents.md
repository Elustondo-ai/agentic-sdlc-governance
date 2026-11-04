# Check canonical agent packages

This compatibility entry point imports `asdg/scripts/check.py` and returns its exit code.
It validates the selected portable catalogue, role sources, templates and links using the current checker.
It does not initialize the provider, activate a native agent, trust hooks or grant approval.

| Caller | Responsibility | Collaborator |
| --- | --- | --- |
| `python3 -B .codex/check_agents.py` | Preserve a repository validation entry point | `asdg/scripts/check.py` |
| Optional `--integrity` | Verify selected hashes as well as structure | Current package manifest |

Legacy provider validators remain historical; native behavior requires separate runtime evidence.
