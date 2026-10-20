# Slide 5 — Agents Cannot Read Our Minds

Now we come to the necessity. Imagine asking an agent to implement a feature. The human team may already know why the feature matters, which cases are exceptional, what architecture was chosen last month, and what security policy applies. Much of that knowledge comes from meetings and years of experience. The instruction "just build it" leaves those facts out.

Look at the left side. Some knowledge is in conversations, some in an issue tracker, some in old diagrams, and some has never been written down. A person who was in those meetings can sometimes reconstruct it. A new agent cannot reliably do that. Even a very capable model needs the relevant information in its working context.

The middle shows what SDLC2 asks us to put into the project: intent, use cases, architecture, constraints, policies, and the current release and sprint status. This does not mean writing every possible detail in advance. It means making the context for the current decision findable, versioned, and open to review. Product and release context frame each focused sprint.

Now the agent can do more than generate plausible code. It can follow the rules, implement against the intended behavior, test it, show evidence, and ask us when something is unclear. The repository becomes shared working knowledge for humans and agents. That is the second reason for specifications: agents need a reliable account of what we are asking them to do.
