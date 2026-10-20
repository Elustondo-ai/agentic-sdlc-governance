# 03 — System Model

Status: initial draft; human review pending.

## Concepts

- **Presentation:** ordered collection of logical slides.
- **Slide:** visual source and ordered narration parts.
- **Narration part:** Markdown text with a declared order and source path.
- **Speech segment:** provider-sized text chunk derived without paraphrasing.
- **Voice profile:** provider, model, voice, language, pace and settings.
- **Media segment:** rendered visual paired with synthesized audio duration.
- **Build manifest:** trace from source hashes to speech requests and output files.

## Processing sequence

1. Discover slides and validate source paths and ordering.
2. Parse selected narration profile; exclude metadata from spoken text.
3. Split long narration at safe boundaries without changing text content.
4. Synthesize/cache audio by source text and voice settings.
5. Probe audio duration; render each visual; assemble ordered video segments.
6. Encode MP4 and optional subtitles; verify streams and manifest coverage.
7. Report warnings and require human review for speech fidelity.

## Component interfaces

- Input: presentation directory, narration profile, voice profile, output settings.
- Output: MP4 path, manifest path, verification results, warnings and cost evidence.
- Failure: invalid source, unsupported format, TTS failure, missing audio, encoder failure.

## Ownership

The component owns media production; the presentation skill owns task guidance. Humans own approval and publication decisions.
