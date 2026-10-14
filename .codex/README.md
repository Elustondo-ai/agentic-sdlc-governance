AI-MODIFIED - 2026-10-10T01:50Z

# Codex named agents — conversational evaluation

- Thirteen project-local Codex custom-agent configurations, one Coordinator and twelve stage specialists.
- `asdlc/agents/*.md` remains canonical; `.codex/agents/*.toml` is the Codex-specific adapter layer.
- All adapters are **read-only by design** for the initial role interviews; they cannot be used to test implementation or state transitions.
- The root Codex session remains the entry point. Ask it to spawn the named specialist, then inspect the subagent thread.
- `asdlc_coordinator` represents the proposed default routing role; a plain session does not automatically become this agent merely because a TOML file exists.
- Out-of-scope results use the textual `OUT_OF_SCOPE` protocol. Direct child-to-coordinator control transfer is not assumed or verified.
- No model is pinned: each role inherits your running Codex model and reasoning settings.
- No real sprint state machine, authority enforcement, or Git automation has been activated.

## Suggested interview prompts

1. `Spawn asdlc_coordinator for a conversation. Ask it to introduce itself, explain the twelve specialist roles and describe its governance boundaries. Do not write files.`
2. `Spawn asdlc_05 and ask it who it is, what it owns, what it must refuse, and which artifacts it produces. Then ask it to implement an architecture. Do not write files.`
3. `Spawn asdlc_09 and ask it how it distinguishes an approved implementation task from an unapproved coding request. Do not write files.`

Native discovery and handoff behavior still require verification in the Codex IDE extension.
