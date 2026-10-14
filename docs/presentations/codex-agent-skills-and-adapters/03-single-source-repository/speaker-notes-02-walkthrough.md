AI-MODIFIED - 2026-10-09T14:33Z

# One source of truth, thin native adapters — Visual walkthrough

Start at the top of the tree. The root AGENTS.md contains the always-applicable repository
rules. Below asdlc/skills are the two skills we already have: presentation production and
component creation.

The proposed asdlc/agents/reviewer directory would capture stable role meaning, but we have
not implemented it. The .agents/skills path exposes the canonical skills to Codex and
Copilot. The .codex, .claude, and .github agent paths contain native agent profiles, with
different syntax.

The tree intentionally labels future items as proposed rather than pretending they exist
today.
