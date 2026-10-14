AI-MODIFIED - 2026-10-09T14:33Z

# SKILL.md: a reusable, task-conditioned capability — Deeper explanation

We should not assume that a description is an executable guarantee. For repeatable
operations, the implementation and tests must verify the outputs. Codex uses .agents/skills
for repository-level discovery; our canonical SKILL.md can live under asdlc/skills only
because a discoverable adapter points to it.

The YAML header must remain syntactically valid. Our PME approval-status rule has a known
conflict with front matter, so approval is not inferred or fabricated.
