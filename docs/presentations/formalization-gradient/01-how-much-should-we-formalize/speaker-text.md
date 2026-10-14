AI-MODIFIED - 2026-09-28T14:23Z

# FG01 — How much should we formalize?

Imagine asking an agent to prepare a sprint for review. The sentence sounds clear, but it leaves important questions open. Which tests are required? What should the walkthrough explain? Which changes does the evidence describe?

We can keep the request in prose and let the agent reason through the project context. We can make the conditions explicit in a structured contract. Or we can provide an operation that checks those conditions and returns a result.

These are three representations of related work, with different responsibilities. The contract defines what ready means. The checker determines whether the supplied evidence satisfies the conditions it can verify. Human judgment still matters for questions such as whether the explanation is adequate.

The record and function on this slide are illustrative design examples. They do not claim that these exact interfaces already exist in our repository.

This is the question behind the formalization gradient: how much meaning should remain open to interpretation, and where should we make that meaning explicit enough to check?
