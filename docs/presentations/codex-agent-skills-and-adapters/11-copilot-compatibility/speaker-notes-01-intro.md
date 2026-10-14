AI-MODIFIED - 2026-10-09T14:33Z

# GitHub Copilot: skills align; named agents differ — Opening narration

GitHub Copilot gives us a useful simplification: it recognizes repository skills under
.agents/skills, so the same discovery adapter can serve Codex and Copilot. Custom agents are
a separate matter.

Copilot uses Markdown-based profiles under .github/agents and may offer different tools or
settings depending on whether we run in VS Code, the CLI, or GitHub's cloud agent.
