# ASDG B1 — Five-slide local video POC

Status: mechanical preview **completed** with eSpeak + FFmpeg; **Piper speech evaluation pending**. No voice-quality acceptance is implied.

## Inputs

The source is the detailed *Codex Agents, Skills & Platform Adapters* presentation, **slides 9–13**, with their full authored PowerPoint speaker notes. `slides/` holds PNG visual renders, `notes/` holds extracted text, and `source/` holds the original input deck. The exported PNG images are visual reproductions, not the canonical editable SVGs. Source presentation files remain authoritative.

## Run Piper on macOS

1. Use Python >= 3.9 and install FFmpeg if absent (`brew install ffmpeg`).
2. Install Python dependencies (`python3 -m pip install python-pptx piper-tts`).
3. Download the Piper voice model and matching `.onnx.json` from [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium).
4. From this folder run:

```sh
python3 build_local_video.py --deck /absolute/path/codex-agent-skills-and-adapters-detailed.pptx --tts piper --piper-model /absolute/path/en_US-lessac-medium.onnx
```

The `--deck` option is required when running the repository copy outside this package. The input deck must be the existing detailed presentation build. Output: `build/last-five-slides-piper.mp4` and `build/manifest-piper.json`.

## Mechanical fallback, NOT a Piper benchmark

```sh
python3 build_local_video.py --tts espeak
```

The `espeak` mode verifies extraction, audio/video muxing, order, and playback—not acceptable voice naturalness. It generates `build/last-five-slides-espeak.mp4`.

## Evidence and next gate

- Five slides 9–13 and their full speaker notes were extracted from the detailed PPTX.
- FFmpeg assembled the five still visuals with eSpeak narration into an eight-minute MP4. The eSpeak voice is intentionally **not** the intended production voice.
- Piper is not installed in the remote execution environment, and a model could not be downloaded from there. Piper narration was not generated or tested here.
- Next gate: run Piper locally and listen to several minutes, checking fatigue, intelligibility, pronunciation, missing words and pacing before accepting B1.

Outputs, voice models and credentials should stay untracked under `build/` or local caches. Do not distribute a model binary without checking its license.
