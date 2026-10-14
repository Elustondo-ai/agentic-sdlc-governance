AI-MODIFIED - 2026-10-09T14:33Z

# Why an adapter exists at all — Visual walkthrough

The central box is the canonical skill folder: it owns the instructions, documents, scripts,
and tests. The left branch is an adapter under .agents/skills, which Codex and GitHub
Copilot recognize. The right branch is .claude/skills, Claude Code's project discovery
location.

Each branch can be a tested symlink or a very short SKILL.md containing the required front
matter and a relative link to the canonical definition. We should not paste the entire
canonical implementation into each adapter.
