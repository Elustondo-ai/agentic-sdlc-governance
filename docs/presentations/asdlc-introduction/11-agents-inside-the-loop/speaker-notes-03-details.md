AI-MODIFIED - 2026-10-08T23:32Z

# Slide 11 — Explanation and example

A failed unit test may send the agent around the inner loop to correct its implementation. But suppose a real user says the warning is technically correct and still unhelpful. Repeating the same unit tests will not resolve that observation. We may need to revisit the intent, use case, or success criterion.

Similarly, human review can reveal that the code works but its structure is too difficult to maintain. That finding can lead back to component design before another implementation attempt. The diagram's forward arrows do not prohibit those earlier returns.

The important question is which claim the evidence supports. Automated tests support specific checked behavior. A walkthrough supports inspection and understanding. Acceptance provides evidence from the running system and intended usage. None should be silently substituted for another.

We should record which boundary is complete and which remains open. That lets the agent continue useful bounded work without pretending the whole sprint or release is finished.
