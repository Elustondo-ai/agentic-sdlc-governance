AI-MODIFIED - 2026-10-08T23:32Z

# Slide 11 — Visual walkthrough

The first blue box groups steps one through eight as Set the Direction. It includes context and intent, use cases and tests, architecture and a useful proof of concept, planning, and component design. Grouping them here does not merge or renumber them.

The orange box is step nine, Build and Test Cycle. Its curved arrow marks the inner iteration: the agent implements, tests, inspects the result, and revises. Code, tests, and evidence evolve together, constrained by the intended behavior.

The purple box is step ten, Document, Review and Release. The agent explains the changes; the human understands and approves the code. The caption says ready for end-to-end testing. That is a boundary, not a claim that every acceptance check has already happened.

The green box is step eleven, DevOps and User Acceptance. The human tests the change in a running system: development or staging at sprint scope, production at release scope. Step twelve then collects observability, insights, and learning. The long green return arrow carries those findings back toward the next direction-setting pass.

The final sentence distinguishes the two loops. The small loop improves an implementation against its current intent. The wider loop can change our understanding of the problem, the plan, or the intended solution.
