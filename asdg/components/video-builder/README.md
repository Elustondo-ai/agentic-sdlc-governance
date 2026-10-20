# Video Builder

Component scaffold created using `asdg-component` skill.

**Responsibility:** produce narrated MP4 files from ASDG SVG and Markdown presentation sources. The `asdg-presentation` skill remains the agent-facing workflow; the video builder owns implementation and tests.

`docs/` contains 00 Governance and twelve official ASDG stages. `types/` accepts language-neutral contracts; `src/` contains implementation; `tests/` contains verification.

The legacy `src/build_video.py` eSpeak plumbing prototype remains available. Its test import and fixture paths are repaired. eSpeak is never selected by the new Piper command.

## Local Piper experiment

`src/build_piper_video.py` reads SVG and Markdown through the canonical presentation skill's source loader. It passes the complete selected narration to Piper without summarization, renders original SVGs using installed `rsvg-convert`, and assembles H.264/AAC MP4 using FFmpeg. This is a local POC; it has no cache, publication workflow, or voice-quality acceptance.

Requires Python >= 3.9, `piper-tts==1.8.0`, `defusedxml==0.7.1`, FFmpeg/FFprobe, `rsvg-convert`, and a Piper `.onnx` voice with matching `.onnx.json`. Obtain approval before installing missing dependencies. The current test environment and voice live in the presentation's ignored `build/`.

From the repository root:

```sh
docs/presentations/codex-agent-skills-and-adapters/build/piper-venv/bin/python -m unittest discover -s asdg/components/video-builder/tests -v
docs/presentations/codex-agent-skills-and-adapters/build/piper-venv/bin/python asdg/components/video-builder/src/build_piper_video.py docs/presentations/codex-agent-skills-and-adapters --piper-model docs/presentations/codex-agent-skills-and-adapters/build/voices/en_US-lessac-medium.onnx --first-slide 9 --last-slide 13 --profile detailed
```

Outputs live under that presentation's `build/piper-09-13-detailed/`: MP4, original-numbered PNG/WAV/scene clips, exact narration text, concat order, and `manifest.json`. Each scene retains measured narration plus 0.65 seconds rounded up to a whole frame. The manifest records source and model hashes, configuration, stream probes, and timings. A successful build verifies stream counts, duration tolerances, unchanged sources, full text submitted, ordered assembly, and full MP4 decoding. These checks cannot establish spoken fidelity or voice quality; listen to the whole video before accepting it.

On this Mac, the absolute installed Piper data path exceeds its bundled phonemizer's path buffer and synthesis initially failed. The command passes a shorter relative path to the same bundled data and fails explicitly if that path is still too long. Piper uses this internal phonemizer with neural ONNX synthesis; it does not invoke the legacy eSpeak voice adapter. Final slide order is checked by decoded-frame RGB similarity (mean absolute difference at most 1 out of 255); exact frame hashes are unsuitable because AAC priming and adjacent H.264 frames can produce small differences.

The historical `docs/06-viable-proof-of-concept/poc-b1-piper-ffmpeg/build_local_video.py` remains a separate PPTX-input prototype. Use the source-first command above for this experiment.

## Convert an existing PPTX

Pass `--deck PATH` to the same command to use embedded PNG visuals and complete speaker-note bodies directly, without generating or changing any PPTX. The current adapter supports the ASDG single-image slides on a white 16:9 canvas, preserving image placement and margins. Cropped, rotated, multi-shape and explicit-background slides fail rather than silently lose content. The ZIP's presentation relationships determine slide order; notes-body extraction retains paragraph breaks and excludes other placeholders. Only an explicitly marked reference-metadata section is excluded from speech and retained in the full notes export. No new Python dependency is needed.

```sh
docs/presentations/codex-agent-skills-and-adapters/build/piper-venv/bin/python asdg/components/video-builder/src/build_piper_video.py docs/presentations/asdg-introduction --deck docs/presentations/asdg-introduction/build/asdg-introduction.pptx --piper-model docs/presentations/codex-agent-skills-and-adapters/build/voices/en_US-lessac-medium.onnx --first-slide 1 --last-slide 5
```

Output: `docs/presentations/asdg-introduction/build/piper-01-05-pptx-asdg-introduction/`. The manifest records the input deck hash, embedded image/notes XML hashes, picture geometry, complete submitted narration, voice/settings, audio/video durations, final frame checks and full decode verification. This is an MP4 conversion experiment, not a PowerPoint renderer for arbitrary decks or a validation of benchmark voice quality.

No Git commit, push, Drive upload, or human approval is implied.
