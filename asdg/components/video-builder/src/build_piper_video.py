"""Experimental local Piper + FFmpeg builder using canonical presentation sources."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SKILL = REPO / 'asdg/skills/asdg-presentation'
sys.path.insert(0, str(SKILL / 'types'))
sys.path.insert(0, str(SKILL / 'src'))
from sources import discover, read_notes


def run(args):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stderr[-4000:]}')
    return result.stdout


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams',
                          '-show_format', '-of', 'json', path]))


def select_slides(root, first, last, profile):
    slides = discover(root, profile)
    if not 1 <= first <= last <= len(slides):
        raise ValueError('Slide range is outside the source presentation')
    return slides[first - 1:last]


def check_media(path, expected, fps=24):
    media = probe(path)
    kinds = [s['codec_type'] for s in media['streams']]
    if sorted(kinds) != ['audio', 'video']:
        raise RuntimeError(f'Expected one audio and one video stream: {path}')
    seconds = float(media['format']['duration'])
    if abs(seconds - expected) > 2 / fps + 0.1:
        raise RuntimeError(f'Duration mismatch: {path}: {seconds} vs {expected}')
    return media


def frame_hash(path, seconds):
    frames = run(['ffmpeg', '-v', 'error', '-ss', str(seconds), '-i', path,
                  '-map', '0:v:0', '-frames:v', '1', '-f', 'framemd5', '-'])
    rows = [line for line in frames.splitlines() if line and not line.startswith('#')]
    if len(rows) != 1:
        raise RuntimeError(f'Could not decode verification frame: {path}')
    return rows[0].split(',')[-1].strip()


def frame_difference(scene, target, seconds):
    import numpy as np
    def pixels(path, when):
        data = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(when),
                                        '-i', str(path), '-map', '0:v:0', '-frames:v', '1',
                                        '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
        if len(data) != 1920 * 1080 * 3:
            raise RuntimeError('Unexpected decoded frame size')
        return np.frombuffer(data, dtype=np.uint8).astype(np.int16)
    return float(np.mean(np.abs(pixels(scene, 1.0) - pixels(target, seconds))))


def build(root, model, first=9, last=13, profile='detailed', length_scale=1.0, deck=None):
    from piper import PiperVoice, SynthesisConfig
    from piper.phonemize_espeak import ESPEAK_DATA_DIR
    for cmd in (('ffmpeg', 'ffprobe') if deck else ('ffmpeg', 'ffprobe', 'rsvg-convert')):
        if not shutil.which(cmd):
            raise RuntimeError(f'Missing required tool: {cmd}')
    root = root.resolve(strict=True)
    model = model.resolve(strict=True)
    config = Path(str(model) + '.json')
    if not config.is_file():
        raise ValueError('Piper model requires matching .onnx.json configuration')
    deck = deck.resolve(strict=True) if deck else None
    deck_hash = sha(deck) if deck else None
    slides = None if deck else select_slides(root, first, last, profile)
    output = root / 'build'
    if output.is_symlink():
        raise ValueError('Presentation build directory must not be a symlink')
    output.mkdir(exist_ok=True)
    suffix = f'pptx-{deck.stem}' if deck else profile
    output = output / f'piper-{first:02d}-{last:02d}-{suffix}'
    output.mkdir(exist_ok=True)
    if output.is_symlink():
        raise ValueError('Output directory must not be a symlink')
    if deck:
        from pptx_sources import extract
        slides = extract(deck, output, first, last)
    # The bundled phonemizer has a small C path buffer. Deep Drive paths
    # otherwise fall back to the wheel's nonexistent build-machine directory.
    phonemizer_data = os.path.relpath(ESPEAK_DATA_DIR)
    if len(os.fsencode(phonemizer_data)) >= 140:
        raise RuntimeError('Run from the repository root to shorten Piper data paths')
    voice = PiperVoice.load(str(model), use_cuda=False, espeak_data_dir=phonemizer_data)
    settings = SynthesisConfig(length_scale=length_scale, noise_scale=0.667,
                               noise_w_scale=0.8, normalize_audio=True)
    entries, clips = [], []
    elapsed = 0.0
    for slide in slides:
        prefix = output / f'{slide.number:02d}'
        image, audio, clip = (Path(str(prefix) + ext) for ext in ('.png', '.wav', '.mp4'))
        script = Path(str(prefix) + '-narration.txt')
        script.write_text(slide.narration, encoding='utf-8')
        # No summary, paraphrase, path cleanup or punctuation replacement.
        parts = [slide.narration] if deck else [read_notes(p)[1] for p in slide.note_files]
        if '\n\n'.join(parts) != script.read_text(encoding='utf-8'):
            raise RuntimeError('Narration coverage mismatch')
        if deck:
            placement = slide.pptx_parts['placement_emu']
            x = round(placement['x'] * 1920 / placement['slide_width'])
            y = round(placement['y'] * 1080 / placement['slide_height'])
            width = round(placement['width'] * 1920 / placement['slide_width'])
            height = round(placement['height'] * 1080 / placement['slide_height'])
            width, height = min(width, 1920 - x), min(height, 1080 - y)
            run(['ffmpeg', '-y', '-v', 'error', '-i', slide.visual, '-vf',
                 f'scale={width}:{height},pad=1920:1080:{x}:{y}:white',
                 '-frames:v', '1', image])
        else:
            run(['rsvg-convert', '--width', '1920', '--keep-aspect-ratio',
                 '--output', image, slide.visual])
        print(f'Synthesizing slide {slide.number}: {len(slide.narration)} characters', flush=True)
        with wave.open(str(audio), 'wb') as wav:
            voice.synthesize_wav(slide.narration, wav, syn_config=settings)
        with wave.open(str(audio), 'rb') as wav:
            seconds = wav.getnframes() / wav.getframerate()
            if seconds <= 0:
                raise RuntimeError('Empty synthesized audio')
            audio_info = {'sample_rate': wav.getframerate(), 'frames': wav.getnframes(),
                          'channels': wav.getnchannels()}
        # Round up to a complete video frame and retain a 0.65-second end pause.
        import math
        scene_seconds = math.ceil((seconds + 0.65) * 24) / 24
        run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-framerate', '24',
             '-i', image, '-i', audio, '-vf',
             'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white,format=yuv420p',
             '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
             '-r', '24', '-c:a', 'aac', '-b:a', '128k', '-af', 'apad',
             '-t', f'{scene_seconds:.6f}', '-movflags', '+faststart', clip])
        media = check_media(clip, scene_seconds)
        clips.append(clip)
        entries.append({'slide': slide.number, 'folder': slide.folder.name,
                        'visual_sha256': sha(slide.visual), 'render_sha256': sha(image),
                        'narration_sources': [{'file': p.name, 'sha256': sha(p),
                                               'characters': len(text)}
                                              for p, text in zip(slide.note_files, parts)],
                        'script_sha256': sha(script), 'characters': len(slide.narration),
                        'coverage': 'exact PPTX speaker narration passed to Piper' if deck else 'exact canonical narration passed to Piper',
                        'pptx_parts': slide.pptx_parts if deck else None,
                        'audio_sha256': sha(audio), 'audio': audio_info,
                        'audio_seconds': seconds, 'planned_video_seconds': scene_seconds,
                        'video_seconds': float(media['format']['duration']),
                        'start_seconds': elapsed})
        elapsed += scene_seconds
    concat = output / 'concat.txt'
    concat.write_text(''.join(f"file '{p.name}'\n" for p in clips))
    target = output / f'{root.name}-{first:02d}-{last:02d}-{suffix}-piper.mp4'
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0',
         '-i', concat, '-c', 'copy', '-movflags', '+faststart', target])
    media = check_media(target, elapsed)
    run(['ffmpeg', '-v', 'error', '-i', target, '-f', 'null', '-'])
    for entry, clip in zip(entries, clips):
        difference = frame_difference(clip, target, entry['start_seconds'] + 1.0)
        # AAC priming can shift the selected frame by one frame; still-image
        # H.264 quantization can vary slightly between adjacent frames.
        if difference > 1.0:
            raise RuntimeError(f"Final video slide order mismatch: {entry['slide']}")
        entry['final_frame_mean_absolute_rgb_difference'] = difference
    for slide in slides:
        entry = next(e for e in entries if e['slide'] == slide.number)
        if sha(slide.visual) != entry['visual_sha256'] or any(
                sha(p) != e['sha256'] for p, e in zip(slide.note_files, entry['narration_sources'])):
            raise RuntimeError('Source changed during build')
    if deck and sha(deck) != deck_hash:
        raise RuntimeError('PPTX changed during build')
    manifest = {'status': 'experimental-local-poc', 'tts_provider': 'piper',
                'piper_version': importlib.metadata.version('piper-tts'),
                'python': sys.version, 'model': str(model), 'model_sha256': sha(model),
                'phonemizer_data_path': phonemizer_data,
                'model_config_sha256': sha(config), 'model_config': json.loads(config.read_text()),
                'settings': {'length_scale': length_scale, 'noise_scale': 0.667,
                             'noise_w_scale': 0.8, 'normalize_audio': True,
                             'use_cuda': False, 'end_pause_seconds': 0.65,
                             'resolution': '1920x1080', 'fps': 24, 'crf': 23,
                             'preset': 'ultrafast', 'audio_bitrate': '128k'},
                'tools': {cmd: run([cmd, '-version' if cmd == 'ffmpeg' else '--version']).splitlines()[0]
                          for cmd in (('ffmpeg',) if deck else ('ffmpeg', 'rsvg-convert'))},
                'input_mode': 'existing-pptx' if deck else 'svg-markdown',
                'input_deck': str(deck) if deck else None, 'input_deck_sha256': deck_hash,
                'narration_profile': 'existing-pptx-notes' if deck else profile, 'slides': entries,
                'output': str(target), 'video_sha256': sha(target),
                'media': media, 'expected_seconds': elapsed,
                'verified': ['exact PPTX text coverage' if deck else 'exact canonical text coverage', 'source hashes unchanged',
                             'ordered concat and decoded frame similarity for every slide',
                             'audio/video streams and durations', 'full MP4 decode'],
                'human_listening_review': 'pending; pronunciation, omissions, pacing and voice quality unvalidated'}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(target, flush=True)
    return target, manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('presentation', type=Path)
    parser.add_argument('--piper-model', type=Path, required=True)
    parser.add_argument('--first-slide', type=int, default=9)
    parser.add_argument('--last-slide', type=int, default=13)
    parser.add_argument('--profile', choices=('intro', 'detailed'), default='detailed')
    parser.add_argument('--length-scale', type=float, default=1.0)
    parser.add_argument('--deck', type=Path, help='Existing ASDG image-based PPTX: use its embedded visuals and notes')
    args = parser.parse_args()
    build(args.presentation, args.piper_model, args.first_slide, args.last_slide,
          args.profile, args.length_scale, args.deck)
