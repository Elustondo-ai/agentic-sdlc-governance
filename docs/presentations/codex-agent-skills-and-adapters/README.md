# Codex Agents, Skills and Platform Adapters

**Purpose:** Implementation reference for ASDG instruction files, skills, named agents, configuration and platform adapters.
**Review state:** AI-authored draft, not PME-approved. No runtime integration claim.
**Audience:** Codex-first engineers; Claude and Copilot compatible concepts.

## Slides — editable sources and spoken narration

Each numbered folder contains `slide.svg`, `speaker-notes-01-intro.md`, `speaker-notes-02-walkthrough.md` and `speaker-notes-03-details.md`.

01. [One methodology. Three execution environments.](01-three-planes-one-method/slide.svg) · [Intro](01-three-planes-one-method/speaker-notes-01-intro.md) · [Walkthrough](01-three-planes-one-method/speaker-notes-02-walkthrough.md) · [Details](01-three-planes-one-method/speaker-notes-03-details.md)
02. [Codex: five mechanisms, five readers](02-codex-five-mechanisms/slide.svg) · [Intro](02-codex-five-mechanisms/speaker-notes-01-intro.md) · [Walkthrough](02-codex-five-mechanisms/speaker-notes-02-walkthrough.md) · [Details](02-codex-five-mechanisms/speaker-notes-03-details.md)
03. [One source of truth, thin native adapters](03-single-source-repository/slide.svg) · [Intro](03-single-source-repository/speaker-notes-01-intro.md) · [Walkthrough](03-single-source-repository/speaker-notes-02-walkthrough.md) · [Details](03-single-source-repository/speaker-notes-03-details.md)
04. [AGENTS.md: standing instructions with scope](04-agents-md-loading/slide.svg) · [Intro](04-agents-md-loading/speaker-notes-01-intro.md) · [Walkthrough](04-agents-md-loading/speaker-notes-02-walkthrough.md) · [Details](04-agents-md-loading/speaker-notes-03-details.md)
05. [SKILL.md: a reusable, task-conditioned capability](05-skill-definition-and-load/slide.svg) · [Intro](05-skill-definition-and-load/speaker-notes-01-intro.md) · [Walkthrough](05-skill-definition-and-load/speaker-notes-02-walkthrough.md) · [Details](05-skill-definition-and-load/speaker-notes-03-details.md)
06. [Why an adapter exists at all](06-skill-adapter-route/slide.svg) · [Intro](06-skill-adapter-route/speaker-notes-01-intro.md) · [Walkthrough](06-skill-adapter-route/speaker-notes-02-walkthrough.md) · [Details](06-skill-adapter-route/speaker-notes-03-details.md)
07. [Named agent: a Codex TOML role, not a skill](07-named-codex-agent/slide.svg) · [Intro](07-named-codex-agent/speaker-notes-01-intro.md) · [Walkthrough](07-named-codex-agent/speaker-notes-02-walkthrough.md) · [Details](07-named-codex-agent/speaker-notes-03-details.md)
08. [Delegation is a workflow; approval is a boundary](08-delegation-and-approval/slide.svg) · [Intro](08-delegation-and-approval/speaker-notes-01-intro.md) · [Walkthrough](08-delegation-and-approval/speaker-notes-02-walkthrough.md) · [Details](08-delegation-and-approval/speaker-notes-03-details.md)
09. [Configuration, tools, and enforcement are separate](09-runtime-config-and-tools/slide.svg) · [Intro](09-runtime-config-and-tools/speaker-notes-01-intro.md) · [Walkthrough](09-runtime-config-and-tools/speaker-notes-02-walkthrough.md) · [Details](09-runtime-config-and-tools/speaker-notes-03-details.md)
10. [Claude Code: shared meanings, different wrappers](10-claude-code-compatibility/slide.svg) · [Intro](10-claude-code-compatibility/speaker-notes-01-intro.md) · [Walkthrough](10-claude-code-compatibility/speaker-notes-02-walkthrough.md) · [Details](10-claude-code-compatibility/speaker-notes-03-details.md)
11. [GitHub Copilot: skills align; named agents differ](11-copilot-compatibility/slide.svg) · [Intro](11-copilot-compatibility/speaker-notes-01-intro.md) · [Walkthrough](11-copilot-compatibility/speaker-notes-02-walkthrough.md) · [Details](11-copilot-compatibility/speaker-notes-03-details.md)
12. [Compatibility is measured, not assumed](12-mapping-and-verification/slide.svg) · [Intro](12-mapping-and-verification/speaker-notes-01-intro.md) · [Walkthrough](12-mapping-and-verification/speaker-notes-02-walkthrough.md) · [Details](12-mapping-and-verification/speaker-notes-03-details.md)
13. [ASDG adoption: implement, inspect, then extend](13-asdg-adoption-path/slide.svg) · [Intro](13-asdg-adoption-path/speaker-notes-01-intro.md) · [Walkthrough](13-asdg-adoption-path/speaker-notes-02-walkthrough.md) · [Details](13-asdg-adoption-path/speaker-notes-03-details.md)

## Generated output

[Open PowerPoint](build/codex-agent-skills-and-adapters.pptx) · [Detailed PowerPoint](build/codex-agent-skills-and-adapters-detailed.pptx) · [Preview](build/preview-detailed.png)
**Generated files appear after build** and are excluded from Git. SVG and Markdown are authoritative.
Build from repository root: `python3 asdg/skills/asdg-presentation/src/build.py --presentation docs/presentations/codex-agent-skills-and-adapters --narration detailed`.

## Evidence and caveats

- Vendor docs checked 2026-10-09; exact runtime versions can alter behavior.
- The shared conceptual role is portable; named agent profiles are **not** byte-for-byte portable across Codex, Claude and Copilot.
- `.agents/skills/asdg-component` adapter and platform agent definitions are **proposed**, not claimed installed.
- Registry routing and repository source-of-truth are separate; this deck changes neither.

## Official references

- [Codex AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex skill construction and discovery](https://learn.chatgpt.com/docs/build-skills)
- [Codex subagents and named TOML](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic)
- [Claude Code skills and symlinks](https://code.claude.com/docs/en/skills)
- [Claude Code custom subagents](https://code.claude.com/docs/en/sub-agents)
- [GitHub Copilot agent skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- [GitHub Copilot custom-agent config](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [GitHub Copilot custom instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support)
- [Claude AGENTS.md fallback release notes](https://github.com/anthropics/claude-code/releases)
