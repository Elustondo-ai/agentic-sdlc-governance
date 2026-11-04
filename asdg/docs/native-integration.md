# Native Codex integration: verify locally

Claude Code integration and client selection are covered in [client integrations](client-integrations.md); this page covers Codex.

The package generates repository skill adapters and thirteen custom-agent TOML files.
It also generates hook configuration for the existing conservative implementation gate and public activity logging.
These are configuration artifacts; actual client behavior must be observed before claiming them operational.

## Compatibility facts checked 20 October 2026

Codex discovers repository skills under `.agents/skills/` and custom agents under `.codex/agents/`.
Custom agents inherit the parent's permissions. The former `sandbox_mode` adapter field is removed;
the role instructions were read-only at that check. Current roles share [documentation authority](../00-governance/docs/documentation-authority.md); parent runtime permissions still apply.
Model/provider/approval settings are not installed or changed by this package.
Hooks use `tool_input.command` for shell and patch events and supported deny JSON for blocked calls.
Project and exact-hook trust must be handled in the actual local Codex client.
Hook failures, timeouts, disabled hooks and unsupported host paths can leave interception incomplete.
The shell fallback covers a guard-process failure; it cannot make runtime timeouts fail closed.

## Verification boundary

The included tests execute the generated hook command directly in disposable repositories.
They test inactive/active/out-of-scope decisions, failure fallback and public-log storage.
Those tests do not establish trust or interception in Pablo's Mac session.
Local Codex must verify picker discovery, a real Focus invocation and a harmless denied write in a test copy.
Session continuation, compaction, native child invocation and actual lifecycle callbacks remain local checks.
Record unverified checks as unverified; do not weaken the guard or bypass trust to produce a green result.
Main-conversation Focus is not a subagent; child logging hooks do not capture its full conversation.

## Official references

- [Skills](https://learn.chatgpt.com/docs/build-skills)
- [Custom agents and inherited permissions](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Hooks, trust and tool coverage](https://learn.chatgpt.com/docs/hooks)

These references describe the platform. The installed client version and observed behavior decide compatibility.
