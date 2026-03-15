# stock_manager.py
"""
Manages local stock video clips from assets/clips/
and music from assets/music/.

Stock videos are scanned, auto-labelled where possible,
and you are asked once to label any unknowns.
Labels are saved to assets/clips/labels.json permanently.
"""

import os
import json
import random
import shutil

CLIPS_DIR   = os.path.join("assets", "clips")
MUSIC_DIR   = os.path.join("assets", "music")
LABELS_FILE = os.path.join(CLIPS_DIR, "labels.json")

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}

EXERCISE_KEYWORDS = [
    "squat", "lunge", "pushup", "push_up", "push-up", "pushups",
    "plank", "burpee", "crunch", "situp", "sit_up", "crunches",
    "jumping", "jump", "run", "sprint", "jog", "skip",
    "mountain", "climber", "kickback", "deadlift",
    "row", "curl", "press", "raise", "extension",
    "hip", "glute", "bridge", "stretch", "warmup",
    "tricep", "bicep", "shoulder", "chest", "back",
    "cardio", "hiit", "aerobic", "stepup", "step_up",
]


def _load_labels() -> dict:
    if os.path.exists(LABELS_FILE):
        try:
            with open(LABELS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_labels(labels: dict):
    with open(LABELS_FILE, "w") as f:
        json.dump(labels, f, indent=2)


def _auto_label(filename: str) -> str | None:
    stem = os.path.splitext(filename)[0].lower()
    stem = stem.replace("_", " ").replace("-", " ")
    for kw in EXERCISE_KEYWORDS:
        kw_clean = kw.replace("_", " ").replace("-", " ")
        if kw_clean in stem:
            return stem.title().strip()
    return None


def scan_stock_clips(folder: str = CLIPS_DIR) -> list:
    """
    Scan folder, label files, return:
        [{ "file": "clip001.mp4", "exercise": "Jumping Jacks" }, ...]
    """
    os.makedirs(folder, exist_ok=True)

    files = sorted([
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in VIDEO_EXTS
        and not f.startswith(".")
    ])

    if not files:
        return []

    labels   = _load_labels()
    results  = []
    modified = False

    print(f"\n  Found {len(files)} stock video(s) in {folder}")

    for filename in files:
        if filename in labels:
            exercise = labels[filename]
            print(f"  [saved   ]  {filename}  ->  {exercise}")
            results.append({"file": filename, "exercise": exercise})
            continue

        auto = _auto_label(filename)
        if auto:
            print(f"  [auto    ]  {filename}  ->  {auto}")
            labels[filename] = auto
            modified = True
            results.append({"file": filename, "exercise": auto})
            continue

        print(f"\n  Unlabelled: {filename}")
        print("  What exercise does this clip show? (Enter to skip)")
        user_input = input("  Exercise name: ").strip()
        if user_input:
            labels[filename] = user_input.title()
            modified = True
            results.append({"file": filename, "exercise": user_input.title()})
        else:
            print(f"  Skipping {filename}")

    if modified:
        _save_labels(labels)
        print(f"  Labels saved to {LABELS_FILE}")

    return results


def get_stock_music(folder_out: str, music_dir: str = MUSIC_DIR) -> str | None:
    """Pick a random audio file from music_dir, copy to folder_out."""
    if not os.path.exists(music_dir):
        os.makedirs(music_dir, exist_ok=True)
        return None

    tracks = [
        f for f in os.listdir(music_dir)
        if os.path.splitext(f)[1].lower() in AUDIO_EXTS
        and not f.startswith(".")
    ]

    if not tracks:
        return None

    chosen = random.choice(tracks)
    src    = os.path.join(music_dir, chosen)
    dst    = os.path.join(folder_out, "music" + os.path.splitext(chosen)[1])
    shutil.copy2(src, dst)
    print(f"  Stock music: {chosen}")
    return dst


if __name__ == "__main__":
    for c in scan_stock_clips():
        print(c)