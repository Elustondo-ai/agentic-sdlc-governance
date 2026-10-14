# 03 — Use Cases

Status: initial draft; acceptance pending.

## UC-01 — Build a narrated presentation
Given a valid five-slide presentation and a selected voice, the author requests a video. The builder produces an MP4, reports actual durations, and preserves narration order.

## UC-02 — Select narration depth
The author chooses `intro` or `detailed`. Only the selected Markdown parts are spoken; unrelated metadata is excluded. The build manifest records the profile.

## UC-03 — Split long narration
A narration part exceeds a provider request limit. The builder creates ordered speech chunks, concatenates audio, and records each chunk's source mapping. It must not summarize.

## UC-04 — Rebuild after a small edit
One slide's narration changes. The builder regenerates affected audio while reusing valid cached segments elsewhere. The manifest reflects new source hashes.

## UC-05 — Switch voice providers
The author chooses a different voice provider. Source Markdown and SVG remain unchanged; provider-specific failures and cost are surfaced.

## UC-06 — Reject a defective result
The reviewer hears an omitted sentence or wrong technical pronunciation. The result is marked unaccepted; the voice configuration or synthesis process is corrected before another review.

## UC-07 — Fail safely
Missing source files, invalid order, unavailable TTS, or encoder errors yield a non-success result without modifying the source presentation.

## Out of scope
Video hosting, publishing, AI-authored replacement scripts and autonomous approval.
