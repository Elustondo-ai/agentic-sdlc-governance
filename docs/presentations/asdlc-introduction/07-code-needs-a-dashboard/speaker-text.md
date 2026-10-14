AI-MODIFIED - 2026-09-23T23:28Z

# Slide 7 — Code Needs a Dashboard

Let me try an analogy from data. If I want to know whether a system is healthy, I could read every event, transaction, and log line. That would be a terrible way to see the trend. A dashboard turns a large amount of raw detail into a view where I can notice a pattern, ask a better question, and make a decision. The data remains available when I need to inspect it.

I think code is reaching a similar point. In many projects, especially after years of maintenance, someone says, "Just read the code." Developers can do that, and sometimes they must. But code is a very large and slow route to understanding a system. It tells me what an implementation does more readily than why a choice was made. In older systems, becoming familiar with the components and their interactions can take months. If agents generate changes at a higher pace, a human cannot keep up simply by reading more source files.

That is why I want a second direction of documentation. Before implementation, intent, use cases, architecture, and tests explain what we want to build and why. After implementation, an agent can inspect the actual code and evidence and produce a navigable view: a component map, a scenario walkthrough, links to the relevant files and tests, and a record of what still needs checking. This is the software equivalent of the dashboard in my analogy.

There is an important limit. An agent cannot recover a missing business reason from code just by drawing a confident diagram. It should distinguish what the code proves, what the earlier specification says, and what remains unknown. We compare the explanation of the built system with the intended system. Any difference becomes a question for human review, a test, or an update to the project knowledge.
