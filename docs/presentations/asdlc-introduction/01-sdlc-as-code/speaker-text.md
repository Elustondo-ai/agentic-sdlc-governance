AI-MODIFIED - 2026-09-24T16:05Z

# Slide 1 — SDLC as Code

Software development has always had a lifecycle. We learn what problem we are solving, decide what success means, design a solution, build it, test it, release it, and learn from what happens in the real world. This diagram makes twelve areas of that work explicit. It is a cycle because what we learn in operation changes the context for our next decision.

The phrase “SDLC as Code” is the important part. We place the method in the project as structured, versioned artifacts that agents can read and use: intent, use cases, architecture, plans, tests, decisions, evidence, and rules. Those artifacts guide work at the point where it happens. Humans retain judgment and approval at consequential boundaries, while agents can actively plan, implement, test, and bring evidence back for review.

I am not claiming that SDLC2 invented the lifecycle or these engineering practices. The contribution is to make good practice usable by AI agents as part of everyday development. Making the process explicit also helps us humans follow it, work alongside the agents, and review their work without losing track of the bigger picture.

You can imagine an SDLC2 agent acting a little like a project manager or Scrum Master. It would know which policies apply, keep track of where we are in the cycle, and make sure we produce and review the required artifacts. It could remind us that a test strategy or release check is missing, then bring that gap to a person instead of silently moving on. It helps us follow the method; it does not take over human judgment.

Look at the later steps in particular. Step five is high-level solution design and architecture. Step nine is the build and test cycle: the agent iterates internally on code, tests, and evidence. Step ten is document, review, and release. Here the agent explains the changes in a form a person can really understand; the person reviews and approves the code and is ready to test the whole change. At step eleven, operational reality, DevOps, and user acceptance, that person tests the change in a running system. Within a sprint, that is a development or staging environment. At release scope, it is production.

The same twelve areas will reappear in release and sprint cycles, guided by a longer-range product roadmap. First, I want you to see the whole system: people and agents working inside a governed lifecycle that learns from reality.
