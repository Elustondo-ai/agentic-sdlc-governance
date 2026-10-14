AI-MODIFIED - 2026-10-01T13:53Z

# AA06 — When orchestration becomes explicit

A small agent with a few carefully designed tools is a serious architecture when the request and its control boundary are simple. We should not add a graph merely to look more advanced.

A workflow graph becomes attractive when work branches, lasts beyond a single request, pauses for approval, resumes after failure, or coordinates several specialized steps. Then explicit state and transitions make the behavior easier to inspect and test.

This is a design decision rather than a maturity ranking. We can keep the same domain contract while changing its execution mechanism. The next slide uses the same LifeBuckets example to show that transition.

## Fine print

- Selection criteria: SDLC2 architectural proposal.
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangChain agents and LangGraph relationship: https://docs.langchain.com/oss/python/langchain/overview
- Multi-agent caution: https://docs.langchain.com/oss/python/langchain/multi-agent
