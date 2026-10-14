AI-MODIFIED - 2026-09-24T00:04Z

# Slide 8 — From Code-Centric to Structured Knowledge

Now we can move from why this matters to what kind of project knowledge an agent actually needs. The old slide said “knowledge-centric,” and I still like that idea. But knowledge by itself can sound almost mystical. Here I mean structured knowledge: things we capture, organize, connect, and keep reviewable.

We capture the intent of the product, the use cases, domain rules, design decisions, and constraints. A taxonomy gives the material a place: which artifact belongs to which product, release, sprint, and SDLC step. An ontology, in the practical sense, says what our domain concepts mean and how they relate. Trace links connect an intent to a use case, a design, an implementation, and a test. Governance tells an agent which rules to follow, which artifacts to produce, and where human approval is required.

The contrast on the right is deliberate, but I do not mean that code becomes secondary or disposable. Code and tests still matter enormously. They show what we implemented and what we checked. The problem with code alone is that it often does not preserve the reason for a business rule, a constraint, or a design compromise. The agent then has to guess that missing context, just as a new developer would have to reconstruct it.

In SDLC 2, an agent can use structured project knowledge to propose work, follow the process, and explain its changes. The human remains responsible for judging whether that explanation is faithful. We also compare it with the actual code, tests, and runtime evidence. If the links are wrong or a rationale is missing, the honest answer is to mark a gap and resolve it, not to manufacture certainty.
