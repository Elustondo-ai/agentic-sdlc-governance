# 01 — Context and Domain Analysis

Status: initial draft; review pending.

## Domain
ASDLC presentations are maintained as versioned slide visuals and authored Markdown narration. A presentation can produce an introductory PPTX, a detailed PPTX, and a narrated video. Google Vids currently requires manual conversion and may substitute a shorter generated script.

## Stakeholders and systems
- Author/reviewer: maintains intended meaning and approves a result.
- Presentation skill: orchestrates source selection and build profiles.
- Video-builder component: renders visuals, synthesizes audio, assembles and checks media.
- TTS provider: local or managed external speech synthesis, replaceable by adapter.
- Consumer: watches an MP4, optionally with subtitles.

## Boundaries
- Inputs: numbered slide folders, SVG, ordered Markdown narration, voice/build settings.
- Outputs: local MP4, optional captions, audio cache and provenance manifest.
- Excluded initially: editing visuals, generating new scripts, hosting or publishing videos.

## Known constraints and uncertainty
- Preserve complete authored narration; TTS may impose per-request size limits.
- Text-to-audio fidelity requires checking beyond a text checksum.
- Voice quality, provider cost, and technical-term pronunciation are unmeasured.
- The earlier eSpeak/FFmpeg proof of concept is a prototype, not an accepted product.
