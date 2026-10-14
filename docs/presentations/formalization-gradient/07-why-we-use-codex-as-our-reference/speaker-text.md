AI-MODIFIED - 2026-09-28T14:59Z

# FG05a — Why we use Codex as our reference

Why do we use Codex as the concrete reference in this chapter? It is our primary development agent, so we can connect the formalization gradient to mechanisms we actually use: project instructions, skills, tools and scripts. This is a practical architectural choice, rather than a claim that one vendor defines the whole discipline.

There is already a path toward shared conventions. The Agentic AI Foundation, under the Linux Foundation, provides a neutral home for building blocks including AGENTS.md, contributed by OpenAI, and the Model Context Protocol, contributed by Anthropic. These address parts of the ecosystem; they do not make every agent workflow interchangeable.

Claude Code now supports AGENTS.md as project instructions. That is welcome convergence. It still supports CLAUDE.md, and the loading behavior depends on the version and settings. Supporting the same filename does not guarantee identical interpretation in every tool.

Our preference is to keep shared project knowledge and SDLC2 policies expressed in neutral terms. Tool-specific configuration belongs behind explicit mappings or adapters, so the project's meaning does not depend on a vendor's naming conventions.

For now, Codex gives us a concrete implementation vocabulary. As shared standards develop, we can change those mappings while preserving our domain definitions, governance and human review responsibilities.

<!-- Reference metadata; exclude from narration.
https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
https://code.claude.com/docs/en/memory
-->
