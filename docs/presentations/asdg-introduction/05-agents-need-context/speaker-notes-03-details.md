# Slide 05 — Explanation and example

For example, suppose a conversation feature must avoid retaining raw audio. That is a hypothetical constraint, not a claim about the current Speaker Coach implementation. A developer who heard the privacy discussion may already know it. An agent receiving only a request for a conversation summary might not.

Recording the constraint changes the task. It affects possible architectures, the data a tool may return, the tests we need, and the questions that remain. A successful summary would not justify violating that constraint.

The same applies to stale context. A design from a previous sprint may no longer be the agreed design. A useful entry point should identify the governing artifact, its scope, and any unresolved conflict. The agent should surface disagreement rather than quietly combine incompatible assumptions.

The goal is not to write down everything anyone might ever know. It is to preserve the knowledge necessary for the present decision and give people and agents a clear route to the relevant detail.
