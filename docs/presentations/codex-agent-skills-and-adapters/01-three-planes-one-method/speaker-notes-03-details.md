# One methodology. Three execution environments. — Deeper explanation

Our current repository illustrates this separation. Under asdg we maintain the reusable
presentation and component-creation skills. The root AGENTS.md provides standing project
instructions.

To expose a skill to Codex or Copilot we place a thin discoverable adapter under
.agents/skills. To specialize a Codex reviewer we would use a TOML file under .codex/agents.
The reviewer's responsibility and the presentation skill's capability stay conceptually
distinct.
