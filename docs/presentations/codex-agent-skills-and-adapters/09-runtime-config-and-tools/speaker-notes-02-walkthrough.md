AI-MODIFIED - 2026-10-09T14:33Z

# Configuration, tools, and enforcement are separate — Visual walkthrough

The left panel shows project-scoped config.toml. The agents table sets a concurrent delegate
limit. The optional MCP connection points to OpenAI's read-only documentation server.

Personal defaults may live in ~/.codex/config.toml, and trusted project configuration can
override them. On the right, distinguish runtime configuration from registered tools, actual
scripts, and the final authority check. For example, a reviewer can invoke a documentation
lookup without being allowed to publish anything.

A commit operation must independently verify its approved staged content rather than trust a
reassuring natural-language response.
