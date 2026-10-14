AI-MODIFIED - 2026-10-10T01:00Z

# Codex local rendering task — Sprint Governance Review

Use the ASDLC `asdlc-presentation` skill and the existing `asdlc/components/video-builder` implementation. Operate on the Google Drive-synced `agentic-sdlc-governance` repository on this Mac.

**Scope:** Build a detailed, full-length, locally narrated Piper + FFmpeg MP4 from all 11 slides in `docs/presentations/asdlc-sprint-governance-review/`. This is only a review artifact. Do not implement sprint governance or change branch/approval policy.

1. Read root `AGENTS.md`, canonical presentation skill and the video builder's current documentation, source and tests. Verify source synchronization and that all 11 slide folders contain one SVG plus three ordered Markdown narration parts.
2. Verify or rebuild the detailed PPTX from the source files using the canonical presentation workflow. Preserve its speaker notes and do not modify source wording or visuals.
3. Use installed Piper on this Mac. Benchmark the available `en_US-lessac-medium` voice against a high-quality locally installed voice if present. Prefer an existing high-quality model after brief listening review; if installing a model is necessary, request approval first. Do not claim a model is objectively the best without listening evidence.
4. Run a one-slide voice smoke test first, then render all 11 slides using the selected Piper voice. Narration profile is `detailed` and must preserve all narration exactly, without shortening, rewriting or ignoring a slide.
5. Preserve individual slide audio and intermediate MP4s under the presentation's ignored `build/` directory. Concatenate into one clearly named primary full-length MP4. Record model identity/hash, exact command, FFmpeg versions, per-slide timings, end-to-end synthesis/encode duration and failures.
6. Run mechanical verification: exact source text submitted, 11 ordered scenes, source files unchanged, output H.264/AAC streams and full decode, end-to-end timing, and all available tests. Verify PPTX build independently if supported by local dependencies.
7. Save a concise execution report in `build/`, explicitly distinguishing mechanical checks, agent claims and human listening/approval. Do not push, commit, merge, publish, alter source content, install paid services or modify agent governance.
8. Stop and report the blocker if any tool is missing or the existing video command only supports a hard-coded slide range; make minimal component-level changes needed to support `--first-slide 1 --last-slide 11` without changing the approved architecture.

**Acceptance:** One playable 11-slide MP4 and corresponding 11-slide detailed PPTX; human listening and content review remain pending. Do not advance any sprint state.
