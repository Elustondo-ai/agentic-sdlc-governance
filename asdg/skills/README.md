# ASDG reusable skills

The full skills live here; platform discovery files are thin routing adapters.

| Skill | Canonical definition | Codex / Copilot | Claude Code |
| --- | --- | --- | --- |
| Component creation | [asdg-component](asdg-component/SKILL.md) | [.agents adapter](../../.agents/skills/asdg-component/SKILL.md) | [.claude adapter](../../.claude/skills/asdg-component/SKILL.md) |
| Presentations | [asdg-presentation](asdg-presentation/SKILL.md) | [.agents adapter](../../.agents/skills/asdg-presentation/SKILL.md) | [.claude adapter](../../.claude/skills/asdg-presentation/SKILL.md) |

For actual procedure and implementation, always follow the canonical `SKILL.md` and its supporting files.
Do not duplicate source tooling in discovery folders. A change to instructions or implementation is made here and picked up through adapters.

The presentation workflow can call the separate `asdg/components/video-builder` component for video export. That component is currently at proof-of-concept maturity, with voice selection, fidelity testing and production validation outstanding.

GitHub Copilot CLI discovers both adapter trees but deduplicates by skill `name`: `.agents/skills/` takes precedence over `.claude/skills/`. Keep the metadata identical, as verified by the adapter test.

Native discovery in Codex, GitHub Copilot, and Claude Code must each be smoke-tested in their own runtime; file presence is not proof of invocation.
