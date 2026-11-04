# Agent configuration compatibility tests: case guide

[Module guide](test_agent_config.md) · [Source](test_agent_config.py)

Each method below belongs to `AgentConfigTests`, takes `self`, returns `None` and uses unittest assertions.
Names describe the intended regression checks; this index is not an execution result.

| Test method | Responsibility |
| --- | --- |
| `test_current_adapters_on_older_python` | current adapters on older python. |
| `test_multiline_and_basic_escapes` | multiline and basic escapes. |
| `test_rejects_unknown_syntax_and_duplicate_keys` | rejects unknown syntax and duplicate keys. |
