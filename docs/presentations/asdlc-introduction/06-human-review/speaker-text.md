AI-MODIFIED - 2026-09-23T22:34Z

# Slide 6 — Human Review at Agent Speed

There is one more reason to reconsider documentation. Agents can produce an explanation after they produce the code. That matters because the speed and parallelism of agent work can overwhelm the person who must understand and approve it.

On the left, several agents are working at once. One changes a component, another writes tests, and another looks for risks. Their raw output may include many files, commits, logs, and discussions. Passing all of that to a human without structure makes the human the bottleneck.

In the middle is a focused review package. It answers three practical questions: what changed, how was it verified, and what still needs my decision? The agent can create a short walkthrough with a component or sequence diagram, point to the relevant tests, and link to the details if I want to inspect them. The exact format depends on the change, but it should make the work easy to navigate.

On the right, the human reads that evidence, asks questions, and approves or redirects the work. The agent's summary is not a substitute for QA or for independent review when those are needed. Its purpose is to make the evidence understandable and the decision clear. This is the third reason: AI helps us consume the results of AI-assisted development without drowning in its output.
