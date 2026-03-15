# main.py — Fat Burn Workout Video Generator
"""
Flow:
  [1] Clip source: Pexels or Stock
  [2] Workout timing (exercise seconds, rest seconds)   ← NOW SECOND
  [3] Exercise selection: Manual or Auto (with intensity + count)
  [4] Music
  [5] Script generation
  [6] Voice render
  [7] Video build
  [8] Thumbnail
"""

import os
import datetime
from workout_config import ask_workout_config, estimate_duration
from script_generator import generate_script_segments
from voice_generator import render_segments
from video_creator import create_video
from thumbnail_generator import create_thumbnail


def make_output_folder() -> str:
    base  = "output"
    os.makedirs(base, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y%m%d")
    # Find the next number that doesn't exist yet (don't create it yet)
    count = 1
    while os.path.exists(os.path.join(base, f"{today}_FatBurn_{count}")):
        count += 1
    folder = os.path.join(base, f"{today}_FatBurn_{count}")
    os.makedirs(folder, exist_ok=True)
    return folder


def choose_clip_source() -> str:
    print("\n  How do you want to get video clips?")
    print("    [1] Pexels  — search & download from the internet")
    print("    [2] Stock   — use my own videos from assets/clips/")
    while True:
        c = input("  Enter 1 or 2: ").strip()
        if c in ("1", "2"):
            return c
        print("  Please enter 1 or 2.")


def choose_exercise_mode() -> str:
    print("\n  How do you want to choose exercises?")
    print("    [1] Manual    — I will type the exercises myself")
    print("    [2] Automatic — Let the app choose exercises for me")
    while True:
        c = input("  Enter 1 or 2: ").strip()
        if c in ("1", "2"):
            return c
        print("  Please enter 1 or 2.")


def ask_exercise_count() -> int:
    print("\n  How many exercises in the workout?")
    print("  Recommended: 5–10 for a good session")
    while True:
        raw = input("  Number of exercises [default 6]: ").strip()
        if raw == "":
            return 6
        try:
            n = int(raw)
            if 1 <= n <= 20:
                return n
            print("  Enter a number between 1 and 20.")
        except ValueError:
            print("  Please enter a whole number.")


def exercises_to_clip_input(exercises: list) -> list:
    """
    Convert exercise dicts (from auto-select) or plain strings (manual)
    to the clip_input format used by script_generator.
    If Pexels mode: returns list as-is (filenames set after download).
    """
    result = []
    for ex in exercises:
        if isinstance(ex, dict):
            # Auto-select dict: {name, intensity, muscle, pexels_query}
            import re
            safe = re.sub(r"[^a-z0-9]+", "_", ex["name"].lower()).strip("_")
            result.append({"file": f"{safe}_1.mp4", "exercise": ex["name"]})
        else:
            name = str(ex).strip()
            import re
            safe = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            result.append({"file": f"{safe}_1.mp4", "exercise": name.title()})
    return result


def print_header():
    print()
    print("=" * 58)
    print("     FAT BURN HOME WORKOUT VIDEO GENERATOR")
    print("     No equipment · Body weight only")
    print("=" * 58)


def main():
    print_header()
    folder = make_output_folder()

    # ── Step 1: Clip source ───────────────────────────────
    print("\nStep 1: Choose clip source")
    clip_source = choose_clip_source()

    # ── Step 2: Workout timing ────────────────────────────
    print("\nStep 2: Set workout timing")
    cfg = ask_workout_config()

    # ── Step 3: Exercise selection ────────────────────────
    print("\nStep 3: Choose exercises")

    if clip_source == "2":
        # Stock mode — scan clips folder, no exercise selection needed
        from stock_manager import scan_stock_clips
        print("  Scanning assets/clips/ ...")
        clip_input   = scan_stock_clips()
        clips_folder = os.path.join("assets", "clips")
        if not clip_input:
            print("  ERROR: No stock clips in assets/clips/")
            print("         Add .mp4 files there and run again.")
            return
        print(f"  {len(clip_input)} stock clips ready.")

    else:
        # Pexels mode — ask manual or auto
        ex_mode = choose_exercise_mode()

        if ex_mode == "2":
            # Auto selection
            from exercise_library import ask_intensity, auto_select_exercises
            intensity  = ask_intensity()
            ex_count   = ask_exercise_count()
            exercises  = auto_select_exercises(ex_count, intensity)

            print(f"\n  Auto-selected {len(exercises)} exercises ({intensity}):")
            for i, ex in enumerate(exercises, 1):
                print(f"    {i:2d}. {ex['name']:30s}  [{ex['intensity']}]  {ex['muscle']}")

            # Download from Pexels using precise library queries
            from pexels_downloader import download_exercises
            print("\n  Downloading clips from Pexels ...")
            clips_folder = download_exercises(exercise_list=exercises)
            # Build clip_input from actual downloaded files
            clip_input = _build_clip_input(clips_folder, exercises)

        else:
            # Manual entry
            from pexels_downloader import download_exercises
            print("\n  Enter your exercises:")
            clips_folder = download_exercises(exercise_list=None)
            clip_input   = _scan_clips_folder(clips_folder)

        if not clip_input:
            print("  ERROR: No clips available. Aborting.")
            return
        print(f"\n  {len(clip_input)} exercise clip(s) ready.")

    # ── Estimate duration ─────────────────────────────────
    est = estimate_duration(len(clip_input), cfg)
    print(f"  Estimated video length: {est}")

    # ── Step 4: Background music ──────────────────────────
    print("\nStep 4: Get background music")
    if clip_source == "2":
        from stock_manager import get_stock_music
        music_file = get_stock_music(folder)
        if not music_file:
            from music_manager import get_free_music
            music_file = get_free_music(folder)
    else:
        from music_manager import get_free_music
        music_file = get_free_music(folder)

    # ── Step 5: Generate script ───────────────────────────
    print("\nStep 5: Generate workout script")
    segments = generate_script_segments(clip_input, cfg)
    ex_count = sum(1 for s in segments if s["type"] == "exercise")
    re_count = sum(1 for s in segments if s["type"] == "rest")
    print(f"  {len(segments)} segments  ({ex_count} exercises, {re_count} rests)")

    # ── Step 6: Render AI voice ───────────────────────────
    print("\nStep 6: Render AI voice")
    enriched = render_segments(segments, folder=folder)

    # ── Step 7: Build video ───────────────────────────────
    print("\nStep 7: Build video")
    video_file = create_video(
        folder=folder,
        clips_folder=clips_folder,
        enriched_segments=enriched,
        music_file=music_file,
    )

    # ── Step 8: Thumbnail ─────────────────────────────────
    print("\nStep 8: Generate thumbnail")
    create_thumbnail(folder=folder, title="FAT BURN WORKOUT")

    print("\n" + "=" * 58)
    print(f"  DONE!   {folder}")
    print("=" * 58)


def _build_clip_input(clips_folder: str, exercises: list) -> list:
    """
    Match downloaded .mp4 files to exercise names.
    Falls back to scanning the folder if a file is missing.
    """
    import re
    result = []
    for ex in exercises:
        name = ex["name"] if isinstance(ex, dict) else str(ex)
        key  = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        # Find any file starting with this key
        matches = [
            f for f in os.listdir(clips_folder)
            if f.startswith(key) and f.endswith(".mp4")
        ]
        if matches:
            result.append({"file": matches[0], "exercise": name})
        else:
            # Clip may have failed to download — skip gracefully
            print(f"  WARNING: no clip found for '{name}' — skipping")
    return result


def _scan_clips_folder(clips_folder: str) -> list:
    """Scan a clips folder and derive exercise names from filenames."""
    import re
    files  = sorted([f for f in os.listdir(clips_folder) if f.endswith(".mp4")])
    result = []
    for f in files:
        stem   = os.path.splitext(f)[0]
        parts  = stem.split("_")
        if parts and parts[-1].isdigit():
            parts = parts[:-1]
        name = " ".join(parts).replace("-", " ").title()
        result.append({"file": f, "exercise": name})
    return result


if __name__ == "__main__":
    main()