# 04 — Benchmarks and Reference Alternatives

Status: benchmark plan only; no comparative results claimed.

## Alternatives

| Candidate | Role | Principal trade-off |
| --- | --- | --- |
| Google Vids | Existing workflow baseline | Manual conversion and possible script condensation |
| Local eSpeak | Functional baseline | Offline and cheap, but voice quality is limited |
| Piper or other local TTS | Open/local candidate | No per-call charge; model quality and setup vary |
| Google Cloud TTS | Managed voice candidate | Quality and cloud integration vs usage charges |
| OpenAI speech API | Managed voice candidate | Voice flexibility vs API cost and limits |

## Benchmark material

Use the same excerpt from *Agents vs Skills*, including technical terms such as Codex, ASDG, API, and Markdown. Do not compare different scripts as though voice alone changed.

## Measures

- Listener rating: naturalness, pacing, clarity, pronunciation (1–5).
- Transcript alignment: omitted, inserted or substituted words, reviewed manually.
- Generation latency: elapsed time for the identical script.
- Cost: currency and units per 1,000 narration characters; record assumptions.
- Operational fit: offline ability, privacy, licensing, caching and failure handling.

## Decision rule

Choose a voice only after listening to comparable samples and recording quality, cost and operational constraints. No automatic winner is assumed.
