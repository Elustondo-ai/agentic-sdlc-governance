# AA03 — A bounded runtime agent

Our first runtime design deliberately has one agent and a small set of application tools. The product authenticates the user and supplies a bounded task. The managed harness runs the model and tool loop. The product implements the tools and decides whether each requested effect is permitted.

Codex gives us a familiar development model of instructions and skills. The OpenAI Agents API can run the Codex harness for application tasks, but repository AGENTS.md files are not automatically a complete server-side policy system. We would explicitly configure the instructions, skills, tool contracts and application boundary for this runtime.

This is a proposed reference architecture, not a claim that LifeBuckets currently runs this way. Simplicity means fewer moving parts, not weaker controls.

## Fine print

- OpenAI Agents API overview: https://developers.openai.com/api/docs/guides/agents-api/overview
- Harness and application server responsibilities: https://developers.openai.com/api/docs/guides/agents-api/architecture
- Function tools: https://developers.openai.com/api/docs/guides/agents-api/tools/functions
- Tool names on the slide are illustrative proposals.
