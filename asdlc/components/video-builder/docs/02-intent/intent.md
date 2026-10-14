# 02 — Intent

Status: proposed; human review pending.

## Purpose
Produce reviewable, natural-sounding narrated videos directly from ASDLC presentation sources, without dependence on Google Vids for routine builds.

## Desired outcomes
- One authoritative presentation source produces PPTX and MP4 representations.
- The full selected narration is spoken in order, without silent summarization.
- Each visual stays visible for its actual audio duration.
- A rebuild of unchanged inputs can reuse cached audio safely.
- The voice provider is replaceable without rewriting the presentation.
- Errors, costs, and unverifiable claims are explicit.

## Principles
- Preserve source meaning; do not rewrite narration during export.
- Keep component mechanics separate from the presentation skill's instructions.
- Use open tooling for assembly and benchmark voice engines before selection.
- Treat automated checks and human listening as complementary evidence.

## Success criteria (proposed)
- Correct slide order and narration-part order in a five-slide test deck.
- H.264/AAC MP4 with audio duration aligned to displayed visuals.
- No missing narration segments in the synthesis request manifest.
- Human reviewer accepts pronunciation, clarity, pacing and content fidelity.
- Generated outputs stay in presentation-local `build/` and out of Git.

## Non-goals for first release
Automatic publishing, background jobs, voice cloning, and video animation.
