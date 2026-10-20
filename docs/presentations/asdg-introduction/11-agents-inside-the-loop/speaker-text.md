# Slide 11 — AI Works Best Inside the Loop

The previous slide showed where the cycles live. Now I want to show why we call the method iterative. An agent should work with the project's context and decisions, and it should bring evidence back to the people making decisions. This happens inside a sprint and again at release scope.

The first eight steps establish the direction for a piece of work. They move from context and intent through use cases, test strategy, high-level architecture, any useful proof of concept, planning, and low-level design. The agent can help produce each artifact, but a human decides what problem matters and approves the direction before implementation.

There is a smaller loop inside step nine. The agent can change the code, run tests, inspect failures, and try again. We call this the build and test cycle because an implementation rarely emerges correctly in one pass. The tests and the intent constrain that iteration. The agent brings back the changes and evidence rather than asking us to judge a raw stream of generated code.

At step ten, the agent documents what it actually changed. A walkthrough and a focused visual should help the human understand the affected components and behavior. The human reviews the code deeply, asks for corrections where necessary, and approves the change for end-to-end testing. That is what document, review, and release means here.

Step eleven checks the result in a running system. During a sprint, the human tests it in development or staging. During a release, the human tests it in production. That is user acceptance and operational reality, with DevOps making the relevant environment and deployment possible.

Finally, observability, insights, and learning close the wider loop. What we learn from tests and operation can change the next sprint, the release plan, or the product roadmap. There are therefore two different iterations on this slide: the quick build-and-test cycle inside step nine, and the larger feedback loop across the whole method. AI can accelerate both only when we keep their evidence and human decisions connected.
