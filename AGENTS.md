AI-MODIFIED - 2026-10-14T03:15:33Z

# Agentic SDLC repository instructions

This repository develops ASDLC: a human-governed, agent-operable software development method.
`docs/` explains the product and records its development; `asdlc/` contains reusable implementation.
Read the root README and the task-relevant source material before changing files.
Current explicit instructions from Pablo override older repository notes or recorded proposals.

## Presentation work

Use `asdlc/skills/asdlc-presentation/SKILL.md` for presentation creation, maintenance, and builds.
The `.agents` entry points to that canonical capability; do not duplicate its standard.
Presentation source folders under `docs/presentations/` are authoritative; generated exports are not.
Each presentation owns a local ignored `build/`. Never stage generated decks or previews.
Preserve original meaning, speaker notes, source references, and existing review markers.

## Reusable skills and platform discovery

- Canonical skill definitions and implementations live only under `asdlc/skills/`.
- `.agents/skills/` exposes the two skills to Codex and GitHub Copilot; `.claude/skills/` exposes them to Claude Code. Adapters are discovery entry points, **not** separate policies or implementation copies.
- For creating or validating component structure, use `asdlc/skills/asdlc-component/SKILL.md`.
- For documentation/presentations, use `asdlc/skills/asdlc-presentation/SKILL.md`.
- For video production, the presentation skill may use `asdlc/components/video-builder/`; its current eSpeak implementation is a proof of concept, not an approved high-quality narration engine.
- Before declaring a skill operational on a platform, verify its native discovery and an actual invocation on that platform. A folder or successful unit test alone is insufficient.
- Skills define capabilities; a new named agent requires a distinct responsibility boundary and separate review.

## Scope and evidence

Keep changes bounded and reviewable; preserve unrelated local work.
Distinguish implemented, tested, proposed, and human-approved states.
Do not reconstruct or renumber the lifecycle from memory; read `docs/status/lifecycle-baseline.md`.
Do not infer authorization for publication, pushes, deployment, deletion, or permission changes from a plan or a review marker.
Pablo's explicit request to perform a consequential operation applies only to that operation and its stated scope.
Never add or advance PME-APPROVED without explicit approval of the exact file state.
For native SKILL YAML, retain valid syntax and fail closed on whole-file approval until the status convention is resolved.
Report actual verification and any failed operation; never describe unexecuted work as complete.

## Local CLI bootstrap
ASDLC-owned automation uses Python >= 3.9; governed applications may use any language.
Use root `./asdg install`; if its executable bit is absent, use `python3 asdg install`.
See `asdlc/00-governance/docs/install-cli.md` for startup-file changes and limitations.
`asdg init` initializes the caller's Git root, using the existing catalogue without copying roles.
The CLI generates project hook configuration; it never grants hook trust, starts sprints, or grants approval.
`status`, `next`, guard permissions and the local dashboard share the [state engine](asdlc/00-governance/docs/state-engine.md).
