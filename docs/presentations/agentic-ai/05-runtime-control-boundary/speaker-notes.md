AI-MODIFIED - 2026-10-01T13:53Z

# AA05 — The runtime control boundary

The agent can interpret a request and propose that an action be completed. The application receives a tool call, checks the authenticated caller, verifies the target and current state, applies the confirmation rule and either commits or rejects the change. A prompt cannot substitute for those checks.

We also need three kinds of evidence. The approval record identifies the exact state and operation the human accepted. The tool result tells us whether the application actually changed anything, including failures and retries. Observability helps diagnose behavior, latency and cost, subject to privacy boundaries.

A trace of the model's reasoning is not a transaction record. Conversely, a successful write does not prove that the agent's explanation was correct. Both must be testable.

## Fine print

- Control and evidence model: proposed SDLC2 design.
- Agents API architecture: https://developers.openai.com/api/docs/guides/agents-api/architecture
- LangGraph human-in-the-loop concepts: https://docs.langchain.com/oss/python/langgraph/overview
