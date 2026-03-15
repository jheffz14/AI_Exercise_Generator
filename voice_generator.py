# voice_generator.py
"""
Renders each script segment to its own MP3 file, then measures its
real duration.  Returns the enriched segment list so video_creator
can size each video segment to EXACTLY match the audio — no guessing.
"""

import os
import re
import time
from gtts import gTTS

try:
    from mutagen.mp3 import MP3 as MutagenMP3
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

try:
    from moviepy.editor import AudioFileClip as _AFC
    HAS_MOVIEPY_AUDIO = True
except ImportError:
    HAS_MOVIEPY_AUDIO = False

OUTPUT_FOLDER = "output"


def _clean_for_tts(text: str) -> str:
    """Strip emoji / non-ASCII that gTTS cannot handle."""
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s{2,}", "  ", text).strip()
    return text


def _measure_mp3(path: str) -> float:
    """Return duration in seconds. Tries mutagen first, then moviepy."""
    if HAS_MUTAGEN:
        try:
            return MutagenMP3(path).info.length
        except Exception:
            pass
    if HAS_MOVIEPY_AUDIO:
        try:
            c = _AFC(path)
            d = c.duration
            c.close()
            return d
        except Exception:
            pass
    # Rough fallback: ~2.5 words per second
    word_count = len(path.split())
    return max(2.0, word_count / 2.5)


def render_segments(segments: list, folder: str, lang: str = "en") -> list:
    """
    Render each segment's text to its own MP3, measure real duration,
    and return the enriched list with:
        "audio_path" : str   path to segment mp3
        "audio_dur"  : float real duration in seconds
    """
    os.makedirs(folder, exist_ok=True)
    audio_dir = os.path.join(folder, "audio_segments")
    os.makedirs(audio_dir, exist_ok=True)

    enriched = []
    for i, seg in enumerate(segments):
        clean    = _clean_for_tts(seg["text"])
        seg_path = os.path.join(audio_dir, f"seg_{i:03d}_{seg['type']}.mp3")

        try:
            tts = gTTS(text=clean, lang=lang, slow=False)
            tts.save(seg_path)
            duration = _measure_mp3(seg_path)
            print(f"  [{seg['type']:8s}]  {duration:5.1f}s  —  {clean[:60]}")
        except Exception as e:
            print(f"  WARNING: TTS failed for segment {i}: {e}")
            seg_path = None
            duration = 3.0

        enriched.append({**seg, "audio_path": seg_path, "audio_dur": duration})

    return enriched


def create_voice(script: str, filename: str = None, lang: str = "en") -> str:
    """Legacy single-file voice generator kept for compatibility."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    if not filename:
        filename = os.path.join(OUTPUT_FOLDER, f"voice_{int(time.time())}.mp3")
    clean = _clean_for_tts(script)
    gTTS(text=clean, lang=lang, slow=False).save(filename)
    print(f"Voice saved: {filename}")
    return filename


# ── CLI test ──────────────────────────────────────────────
if __name__ == "__main__":
    from script_generator import generate_script_segments
    segs   = generate_script_segments(["push_up_1.mp4", "squat_1.mp4"])
    result = render_segments(segs, "output/test_voice")
    for r in result:
        print(r["type"], r["audio_dur"])