# AA07 — The same contract in LangGraph

Here is the same request expressed as an explicit workflow. State carries the request, authorized scope, versions of records, proposed action, approval and final outcome. Nodes load context, produce a proposal, validate scope, pause when approval is needed, and execute only after the application permits the effect.

LangGraph offers stateful orchestration, persistence and human-in-the-loop interruption. A real design must also define the rejection, expiration, retry and compensation paths; the slide deliberately shows only the main route and names the alternate outcome. LangChain can provide higher-level agent abstractions on top of LangGraph, while LangGraph gives us more direct control over the workflow.

The transition from our first approach changes the control mechanism, not the meaning of “approval” or the evidence needed to claim a successful update. This graph is illustrative, not a claim about an existing LifeBuckets deployment.

## Fine print

- LangGraph orchestration and persistence: https://docs.langchain.com/oss/python/langgraph/overview
- State and node design: https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
- LangChain agent architecture: https://docs.langchain.com/oss/python/langchain/overview
- Specific LifeBuckets workflow: SDLC2 proposal for Pablo's review.
