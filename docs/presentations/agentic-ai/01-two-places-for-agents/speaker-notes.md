AI-MODIFIED - 2026-10-01T13:53Z

# AA01 — Agents in development and in the product

We use the word agent in two distinct settings. On the left, Codex helps us develop the application. It reads our repository, specifications and working rules, and proposes changes that a human can review. Its output is software and evidence about that software.

On the right, an agent participates in the running application. It responds to a product user and may call application tools. Its output could be an answer, a proposal, or an actual change to product data. That makes its permissions and failure modes different.

SDLC2 can guide both settings, but a development approval does not authorize a runtime action. We will keep these two lanes separate throughout this chapter.

## Fine print

- Architectural distinction and labels: SDLC2 proposal for review.
- Codex project guidance: https://developers.openai.com/codex/agent-configuration/agents-md
- OpenAI Agents API architecture: https://developers.openai.com/api/docs/guides/agents-api/architecture
