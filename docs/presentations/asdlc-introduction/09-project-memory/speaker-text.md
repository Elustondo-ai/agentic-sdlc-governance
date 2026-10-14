AI-MODIFIED - 2026-09-24T02:19Z

# Slide 9 — Project Memory Connects the Work

Here is the system-level picture behind structured knowledge. The top layer is the project's living memory. It includes intent and domain definitions, architecture and decisions, code and test evidence, governance and current status, and observations from the running system. The point is not to place five unrelated document piles in a repository. We link and version them so a person or an agent can follow the reason for a change and inspect the evidence behind it.

Humans and agents use that same project memory as they work together. A human brings purpose, judgment, and approval. Agents can propose, build, document, and check work against the recorded rules. We still need human review because an agent can misread a rule, invent a rationale, or miss a constraint. The knowledge base makes its work more inspectable; it does not grant an agent authority by itself.

The work passes through our twelve-step lifecycle. This slide deliberately does not replace those steps with the older six-step summary from my earlier presentation. The lifecycle also includes delivery, operations, observation, and learning. That last part is essential. Tests, incidents, usage, and other runtime signals tell us whether the system behaved as intended. We feed those observations back into the project memory, where they can change a plan, a test, a design, or the next cycle's context.

So when I say project memory, I mean a practical engineering system: artifacts, relationships, status, evidence, and rules that both humans and agents can navigate. Its value depends on whether it stays connected to the code and to reality.
