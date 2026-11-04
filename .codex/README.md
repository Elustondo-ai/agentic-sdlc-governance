# Codex adapters in the methodology provider

Thirteen named-role adapters point to the canonical packages under `asdg/`.
Their contents are generated from `asdg/templates/.codex/agents/`; update the templates first.
Stable native names and lifecycle IDs are preserved. Admin remains a conversational maintenance role outside this catalogue.

The adapters inherit runtime permissions; canonical contracts allow project documentation and retain separate application/state gates.
No adapter grants approval, publication, commit, push, deployment or hook trust.
Actual native discovery and invocation must be tested in the target client; this migration checks configuration only.

`python3 -B .codex/check_agents.py` delegates to the portable package checker.
The provider does not install client hooks or initialize application state for itself.
Repository skill entries under `.agents/disabled-skills-2026-10-20/` stay disabled.

For developer installation, extract the ZIP into a client repository and use [portable setup](../asdg/docs/installation.md).
