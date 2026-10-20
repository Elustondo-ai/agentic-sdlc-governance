# A1 — Codex vocabulary and mechanisms

This reference separates the mechanisms that we loosely call the Codex language.

Project instruction files provide applicable guidance. Skill files package reusable workflows. In the command-line and IDE interfaces, a dollar mention can select an available skill. Slash commands belong to the supported interface. Configuration files and registered tools have their own readers and effects.

The distinction is practical. Naming a skill does not create it. Writing a command-looking string in a document does not install a command. Project prose can state a rule, while enforcement depends on the actual controls in the environment.

This mapping is specific to the product surface. ChatGPT Work does not automatically inherit every local repository configuration or command available in a developer’s CLI. We must use the skills and connections actually available in the environment where we work.

For SDLC2, the annex is a translation guide. We should identify which mechanism carries a rule or operation, how it becomes available, and where its authority stops. Those details should be checked against current documentation when the implementation changes.

<!-- Reference metadata; exclude from narration.
https://learn.chatgpt.com/docs/agent-configuration/agents-md
https://learn.chatgpt.com/docs/build-skills
https://learn.chatgpt.com/docs/reference/slash-commands
https://learn.chatgpt.com/docs/configuration
https://learn.chatgpt.com/docs/extend/mcp
-->
