AI-MODIFIED - 2026-09-27T17:04:47Z

# R02 — Speaker text

This reference is an article by Neo Kim in The System Design Newsletter, called Spec Driven Development — A Deep Dive. It illustrates the approach through Blitzy. We should treat it as a practitioner case study, rather than independent proof that a particular product or process is more effective.

For us, the important comparison is not who invented documentation or human review. The article shares our direction: give agents structured context, inspect the plan before coding, and make the resulting changes understandable to people.

Blitzy’s own documentation makes that concrete. It describes a technical specification derived from the existing codebase, an Agent Action Plan for review before generation, and a Project Guide delivered with the pull request. That guide is supposed to be reviewed alongside the actual changes. It is an explanation, not a substitute for evidence.

This connects directly to our three directions of knowledge. We recover understanding from existing code. We express intent and design to guide new code. And we explain the resulting code so that humans can understand, review and accept it.

SDLC2 makes this an explicit repository operating model: twelve steps repeated for sprints and releases, guided by a product roadmap. Module folders connect high-level architecture to low-level design and then to types and behavioral contracts. Human-only staging, a mandatory code walkthrough, and real-system acceptance testing make responsibilities visible.

One detail deserves particular attention. Blitzy’s plan-review documentation warns that some supplied rules may be omitted from a generated plan. Our governance should require those conflicts to be surfaced and resolved explicitly. An agent must not silently weaken a policy.

The practical additions I would take from this reference are dependency impact maps, explicit checks for behavior that must remain unchanged, and traceability from requirements through code changes to test evidence. These are proposals to strengthen SDLC2, not claims that the article validates our whole method.
