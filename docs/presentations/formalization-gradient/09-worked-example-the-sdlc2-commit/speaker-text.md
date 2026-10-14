AI-MODIFIED - 2026-09-28T14:23Z

# FG07 — Worked example: the SDLC2 commit

Our SDLC2 commit is the concrete example that motivated this discussion. We want code, documentation and the prepared sprint status to enter one reviewed commit together.

The agent first prepares the candidate, including the status change. The human then reviews and stages the intended content. The checker verifies that the staged snapshot satisfies the required conditions and that its evidence applies to that candidate. The script may then commit that approved snapshot within its authorization.

The human-only staging rule also applies to scripts the agent invokes. A script must not quietly add a changed status file after approval. If governed content changes, the new content needs renewed review and staging.

Git does not automatically remove an older staged version when a working file changes. Our checks must distinguish those versions and prevent an unreviewed edit from being mistaken for approved content. The operation must also guard against concurrent changes to the candidate.

A successful commit produces a hash that we report separately. A push is another operation and may fail while the local commit remains valid. These are distinct outcomes. The value of formalization is to make those boundaries explicit and verifiable.
