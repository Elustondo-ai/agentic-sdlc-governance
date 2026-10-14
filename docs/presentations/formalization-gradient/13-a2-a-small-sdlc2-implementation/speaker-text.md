AI-MODIFIED - 2026-09-28T14:23Z

# A2 — A small SDLC2 implementation

This is a proposed implementation shape for a bounded SDLC2 experiment. The repository guidance points to the governing commit definition. That definition, its schema and its status record live together. A discoverable skill coordinates the procedure, while a Node.js implementation owns the stable mechanics.

The illustrative operation accepts an approved snapshot and completion evidence, then returns an explicit result. Calling something ApprovedSnapshot is not enough. The implementation must establish that the candidate corresponds to the human-reviewed staged content and that it has not changed since validation.

The status record names the sprint, the intended state and its evidence. We prepare that record before human staging. The resulting commit hash belongs in the operation’s report, avoiding a self-reference inside the commit itself.

Useful tests include missing evidence, a changed index, stale approval and a failed commit. Push behavior requires its own authorized operation and failure tests. The skill should explain a blocked result clearly without trying to manufacture approval.

We can first test this design in assessment-only mode. That lets us check whether the definitions and evidence are useful before enabling the commit mechanics.

<!-- Reference metadata; exclude from narration.
https://learn.chatgpt.com/docs/build-skills
Implementation names and signatures are proposed SDLC2 examples.
-->
