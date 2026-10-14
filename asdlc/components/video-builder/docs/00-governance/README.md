# Video Builder — Governance

Status: initial AI-authored draft; human review pending.

## Scope
- Component: `asdlc/components/video-builder`.
- Agent-facing workflow: `asdlc/skills/asdlc-presentation`.
- Inputs remain authoritative SVG visuals and Markdown narration.
- Generated audio, MP4, subtitles and manifests belong in each presentation's `build/`.

## Rules
- Do not modify source slides or speaker notes during a build.
- Never silently summarize, reorder, duplicate or omit narration.
- Keep TTS credentials out of source control; report paid-service usage.
- A successful encode does not establish faithful speech or human approval.
- Human review is required before declaring a video approved or publishing it.
- Commit, push, deployment and publication require separate authorization.

## Markdown convention
- **Proposed for this component:** maximum 50 physical lines per Markdown file.
- Split substantial material into linked, meaningful documents rather than compressing paragraphs.
- The convention is evidenced in the Formalization Gradient slide plan; repository-wide enforcement remains unverified.
- Do not alter Codex `SKILL.md` YAML front matter merely to satisfy review-status formatting.
