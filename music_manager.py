# music_manager.py
"""
Gets background music for the workout video.

Fixes:
  - BUG FIX: was always returning the first cached track (power_beats) because
    the loop returned immediately on any cached file, never trying others.
  - Now tracks the last-used song in assets/music/last_used.txt and skips it,
    guaranteeing a different track every run.
  - Replaced track list with higher-energy, more hype workout music.
"""

import os
import random
import shutil
import requests

MUSIC_DIR      = os.path.join("assets", "music")
LAST_USED_FILE = os.path.join(MUSIC_DIR, "last_used.txt")
AUDIO_EXTS     = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}

# ── High-energy hype workout tracks (CC0 from Pixabay) ───
FREE_TRACKS = [
    {
        "name": "hype_beast",
        "url":  "https://cdn.pixabay.com/download/audio/2022/10/25/audio_946f0a8b9d.mp3",
        "desc": "Hard-hitting bass drops and driving beat"
    },
    {
        "name": "fire_workout",
        "url":  "https://cdn.pixabay.com/download/audio/2022/03/10/audio_270f30c9c8.mp3",
        "desc": "Fast tempo energetic pump-up"
    },
    {
        "name": "beast_mode",
        "url":  "https://cdn.pixabay.com/download/audio/2022/08/02/audio_884fe92c21.mp3",
        "desc": "Intense workout beats"
    },
    {
        "name": "cardio_rush",
        "url":  "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0c6ff1c93.mp3",
        "desc": "High BPM cardio energy"
    },
    {
        "name": "power_surge",
        "url":  "https://cdn.pixabay.com/download/audio/2023/03/09/audio_c8fd84bd60.mp3",
        "desc": "Electronic power surge"
    },
    {
        "name": "adrenaline",
        "url":  "https://cdn.pixabay.com/download/audio/2022/11/22/audio_febc508520.mp3",
        "desc": "Adrenaline rush workout"
    },
    {
        "name": "max_effort",
        "url":  "https://cdn.pixabay.com/download/audio/2023/01/27/audio_4a7f2e31e7.mp3",
        "desc": "Maximum effort driving track"
    },
    {
        "name": "turbo_pump",
        "url":  "https://cdn.pixabay.com/download/audio/2022/12/14/audio_dbbf981e0e.mp3",
        "desc": "Turbo charged pump-up"
    },
]


def _load_last_used() -> str:
    if os.path.exists(LAST_USED_FILE):
        try:
            return open(LAST_USED_FILE).read().strip()
        except Exception:
            pass
    return ""


def _save_last_used(name: str):
    os.makedirs(MUSIC_DIR, exist_ok=True)
    with open(LAST_USED_FILE, "w") as f:
        f.write(name)


def _cached_tracks() -> list:
    result = []
    for t in FREE_TRACKS:
        path = os.path.join(MUSIC_DIR, f"{t['name']}.mp3")
        if os.path.exists(path) and os.path.getsize(path) > 10_000:
            result.append(t)
    return result


def get_free_music(folder: str) -> str | None:
    """
    Pick a hype workout track — always different from last run.

    Priority:
      1. User's own files in assets/music/ (randomly, skipping last used)
      2. A cached free track that wasn't used last time
      3. Download a new free track that wasn't used last time
      4. Any cached track as fallback
      5. Silent fallback
    """
    os.makedirs(MUSIC_DIR, exist_ok=True)
    os.makedirs(folder, exist_ok=True)

    last_used  = _load_last_used()
    free_names = {t["name"] for t in FREE_TRACKS}

    # ── 1. User stock files ───────────────────────────────
    stock = [
        f for f in os.listdir(MUSIC_DIR)
        if os.path.splitext(f)[1].lower() in AUDIO_EXTS
        and not f.startswith(".")
        and os.path.splitext(f)[0] not in free_names
        and f != "last_used.txt"
    ]
    if stock:
        fresh = [f for f in stock if os.path.splitext(f)[0] != last_used]
        chosen = random.choice(fresh if fresh else stock)
        src = os.path.join(MUSIC_DIR, chosen)
        dst = os.path.join(folder, "music" + os.path.splitext(chosen)[1])
        shutil.copy2(src, dst)
        _save_last_used(os.path.splitext(chosen)[0])
        print(f"  Music: {chosen}")
        return dst

    # ── 2. Fresh cached track (not last used) ─────────────
    cached       = _cached_tracks()
    fresh_cached = [t for t in cached if t["name"] != last_used]

    if fresh_cached:
        chosen_track = random.choice(fresh_cached)
        src = os.path.join(MUSIC_DIR, f"{chosen_track['name']}.mp3")
        dst = os.path.join(folder, "music.mp3")
        shutil.copy2(src, dst)
        _save_last_used(chosen_track["name"])
        print(f"  Music: {chosen_track['name']} — {chosen_track['desc']}")
        return dst

    # ── 3. Download a new track (not last used) ───────────
    not_downloaded = [
        t for t in FREE_TRACKS
        if t["name"] != last_used
        and not os.path.exists(os.path.join(MUSIC_DIR, f"{t['name']}.mp3"))
    ]
    random.shuffle(not_downloaded)

    for track in not_downloaded:
        path = _download_track(track)
        if path:
            dst = os.path.join(folder, "music.mp3")
            shutil.copy2(path, dst)
            _save_last_used(track["name"])
            print(f"  Music: {track['name']} — {track['desc']}")
            return dst

    # ── 4. Any cached track (even if reused) ──────────────
    if cached:
        chosen_track = random.choice(cached)
        src = os.path.join(MUSIC_DIR, f"{chosen_track['name']}.mp3")
        dst = os.path.join(folder, "music.mp3")
        shutil.copy2(src, dst)
        _save_last_used(chosen_track["name"])
        print(f"  Music: {chosen_track['name']} (only cached track)")
        return dst

    # ── 5. Download anything ──────────────────────────────
    pool = FREE_TRACKS.copy()
    random.shuffle(pool)
    for track in pool:
        path = _download_track(track)
        if path:
            dst = os.path.join(folder, "music.mp3")
            shutil.copy2(path, dst)
            _save_last_used(track["name"])
            return dst

    print("  WARNING: No music available — using silence")
    return _make_silence(folder)


def _download_track(track: dict) -> str | None:
    cached = os.path.join(MUSIC_DIR, f"{track['name']}.mp3")
    print(f"  Downloading: {track['name']} ...")
    try:
        r = requests.get(
            track["url"], stream=True, timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if r.status_code == 200:
            with open(cached, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            if os.path.getsize(cached) > 10_000:
                print(f"  Downloaded: {track['name']}")
                return cached
            os.remove(cached)
    except Exception as e:
        print(f"  Failed: {track['name']}: {e}")
    return None


def _make_silence(folder):
    try:
        from pydub import AudioSegment
        path = os.path.join(folder, "music.mp3")
        AudioSegment.silent(duration=180_000).export(path, format="mp3")
        return path
    except Exception:
        return None


if __name__ == "__main__":
    result = get_free_music("output/test_music")
    print("Result:", result)