# Codex: five mechanisms, five readers — Visual walkthrough

AGENTS.md provides instructions that Codex loads according to its instruction-discovery
rules. SKILL.md has required front matter and becomes available through supported skill
directories. Custom named agents are standalone TOML configurations under .codex/agents.

The general config.toml file sets runtime defaults and project overrides. Finally,
executable scripts and registered MCP tools are where mechanically checkable operations and
external effects actually happen. A text policy can tell an agent what approval requires,
but it does not by itself prevent a tool from writing a file.
