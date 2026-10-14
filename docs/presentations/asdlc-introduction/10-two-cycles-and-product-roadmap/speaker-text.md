AI-MODIFIED - 2026-09-24T16:05Z

# Slide 10 — Two Cycles, One Product Roadmap

Now we can say how the project memory is organized over time. I think we have two recurring cycles: release and sprint. Both go through the twelve SDLC steps, at different levels of detail. Around them is a product roadmap. The roadmap captures the purpose, domain, users, priorities, and outcomes we want over a longer horizon. It guides the cycles, but does not itself need to act like another sprint with twelve separate steps.

The sprint intent should make sense within its release, and the release should advance the product roadmap. That context flows inward. As sprints finish, their tests, code review, acceptance results, and observations provide evidence that flows outward. They can change release scope or even the roadmap. At release time, we reconcile what the sprints actually delivered, review readiness, and update release knowledge before production. The roadmap evolves as we learn from releases.

The destination of step eleven changes with the cycle. During a sprint, the human tests the approved changes end to end in development or staging. During a release, the human tests the released changes in production. Step ten prepares that decision through documentation, a deep human review, and approval of the code; step eleven checks what actually happens in the appropriate real environment.

The agent needs a small, explicit governance status record: which release is active, which sprint is active or just completed, where we are in the cycle, and which review is pending. That lets an agent act with the right context instead of repeatedly asking where we are. It also lets a human correct the state if it drifts.

The roadmap, release, and sprint remain connected in the project knowledge base. The roadmap is a concise directional view; each release and sprint records only the detail appropriate to its scope. A sprint's architecture or proof of concept may be brief or say that no change is needed. The goal is to make the work navigable and verifiable for both agents and humans, all the way through the final steps.
