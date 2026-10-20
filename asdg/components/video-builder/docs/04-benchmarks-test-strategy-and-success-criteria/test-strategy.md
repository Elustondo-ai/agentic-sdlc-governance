# 04 — Test Strategy and Success Criteria

Status: proposed tests; not yet fully executed.

## Unit tests

- Discover contiguous numbered slides and ordered Markdown parts.
- Exclude nonspoken metadata without removing narration.
- Split long text at safe boundaries; verify exact reconstruction.
- Reject unsupported sources, missing notes and unsafe output paths.
- Invalidate audio cache when voice/model/settings/text change.

## Integration tests

- TTS adapter returns audio or an explicit error.
- FFprobe confirms expected audio and video streams.
- Slide duration follows measured audio plus documented pauses.
- MP4 order matches the source slide and narration sequence.
- Build manifest maps every source part to synthesized segments.

## Human acceptance

- Listen to the complete five-slide *Agents vs Skills* video.
- Compare technical pronunciation, omitted phrases, tone and pacing.
- Confirm slides stay on screen long enough to understand their narration.
- Record approval or required corrections; do not infer approval from passing tests.

## Exit criteria

A full five-slide MP4 passes mechanical checks and a human accepts voice and narration fidelity. Cost and provider limitations are documented.
