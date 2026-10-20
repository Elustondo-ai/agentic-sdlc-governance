# Delegation is a workflow; approval is a boundary — Deeper explanation

Parallel subagents can reduce context pollution and divide read-heavy tasks, but they use
extra resources and may share an incorrect assumption. We should start with focused
read-only reviewers, and avoid concurrent write-heavy delegation until conflicts and
handoffs are addressed.

The parent sandbox and approval mode also matter, so a TOML setting alone must not be
treated as an unconditional security boundary.
