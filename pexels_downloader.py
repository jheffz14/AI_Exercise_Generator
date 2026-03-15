# pexels_downloader.py
"""
Downloads exercise clips from Pexels.

Improvements:
  - Uses precise pexels_query from exercise_library (bodyweight, home, no machine)
  - Adds BODYWEIGHT_SUFFIX to every query
  - Hard-rejects gym machines, equipment, nature, brand names
  - No-repeat history per exercise
  - Accepts exercise dicts (auto-select) OR plain name strings (manual)
"""

import os
import re
import json
import random
import requests
import datetime

PEXELS_API_KEY = "Your PEXELS API"
CLIPS_BASE     = os.path.join("assets", "clips")
HISTORY_FILE   = os.path.join(CLIPS_BASE, "pexels_history.json")

QUERY_MAP = {
    "burpee":            "burpee exercise fitness training bodyweight",
    "burpees":           "burpee exercise fitness training bodyweight",
    "squat":             "squat exercise bodyweight no equipment fitness",
    "squats":            "squat exercise bodyweight no equipment fitness",
    "push up":           "push up exercise bodyweight floor fitness",
    "push ups":          "push up exercise bodyweight floor fitness",
    "pushup":            "pushup exercise bodyweight floor fitness",
    "pushups":           "pushup exercise bodyweight floor fitness",
    "jumping jack":      "jumping jacks exercise cardio bodyweight",
    "jumping jacks":     "jumping jacks exercise cardio bodyweight",
    "plank":             "plank exercise core bodyweight floor",
    "lunge":             "lunge exercise bodyweight legs fitness",
    "lunges":            "lunge exercise bodyweight legs fitness",
    "mountain climber":  "mountain climber exercise cardio bodyweight",
    "mountain climbers": "mountain climber exercise cardio bodyweight",
    "crunch":            "crunch exercise abs bodyweight floor",
    "crunches":          "crunch exercise abs bodyweight floor",
    "sit up":            "sit up exercise abs bodyweight floor",
    "sit ups":           "sit up exercise abs bodyweight floor",
    "high knees":        "high knees exercise running cardio",
    "butt kicks":        "butt kicks exercise running cardio",
    "jump squat":        "jump squat exercise plyometric bodyweight",
    "jump squats":       "jump squat exercise plyometric bodyweight",
    "glute bridge":      "glute bridge exercise bodyweight floor",
    "hip thrust":        "hip thrust exercise glute bodyweight floor",
    "russian twist":     "russian twist exercise abs bodyweight floor",
    "leg raise":         "leg raise exercise abs bodyweight floor",
    "flutter kick":      "flutter kicks exercise abs bodyweight",
    "donkey kick":       "donkey kick exercise glute bodyweight",
    "fire hydrant":      "fire hydrant exercise hip glute bodyweight",
    "wall sit":          "wall sit exercise legs bodyweight",
    "superman":          "superman exercise back extension floor",
    "inchworm":          "inchworm exercise stretch bodyweight",
    "speed skater":      "speed skater exercise lateral cardio",
    "box jump":          "box jump exercise plyometric legs",
    "bear crawl":        "bear crawl exercise bodyweight floor",
    "tricep dip":        "tricep dip exercise arms bodyweight",
    "step up":           "step up exercise legs bodyweight",
    "tuck jump":         "tuck jump exercise plyometric cardio",
    "jumping lunge":     "jump lunge exercise plyometric legs bodyweight",
    "v up":              "v up exercise abs bodyweight floor",
    "plank jack":        "plank jack exercise cardio bodyweight",
}

FITNESS_KEYWORDS = {
    "exercise", "workout", "fitness", "training", "sport", "athlete",
    "body", "health", "cardio", "aerobic", "bodyweight", "strength",
    "active", "fit", "motion", "sweat", "gym", "jumping", "running",
    "push", "pull", "squat", "plank", "stretch", "floor", "mat", "home",
}

REJECT_HARD = {
    "seed", "plant", "garden", "flower", "tree", "nature", "animal",
    "food", "cooking", "beach", "ocean", "sky", "thunder", "lightning",
    "storm", "rain", "snow", "landscape", "building", "car", "office",
    "dumbbell", "barbell", "kettlebell", "treadmill", "cable machine",
    "weight machine", "gym machine", "spin bike", "elliptical",
    "burpee seed", "burpee seeds",
}

REJECT_SOFT = {
    "bench press", "weight rack", "pulley", "rowing machine",
}


def _build_queries(exercise) -> list:
    if isinstance(exercise, dict):
        base = exercise.get("pexels_query", f"{exercise['name']} exercise bodyweight")
        name = exercise["name"]
        return [
            base,
            f"{name} exercise bodyweight home no equipment",
            f"{name} bodyweight fitness",
        ]
    key    = exercise.lower().strip()
    mapped = QUERY_MAP.get(key)
    if mapped:
        return [mapped, f"{exercise} exercise bodyweight", f"{exercise} exercise"]
    title  = key.title()
    return [
        f"{title} exercise bodyweight home workout",
        f"{title} fitness bodyweight no equipment",
        f"{title} exercise",
    ]


def _score(video: dict, name: str) -> int:
    score = 0
    words = set(name.lower().split())
    url   = (video.get("url") or "").lower()
    user  = (video.get("user", {}).get("name") or "").lower()
    tags  = " ".join(t.get("title", "") for t in video.get("tags", [])).lower()
    text  = f"{url} {user} {tags}"

    for kw in REJECT_HARD:
        if kw in text:
            return -999
    for word in words:
        if len(word) > 3 and word in text:
            score += 30
    for kw in FITNESS_KEYWORDS:
        if kw in text:
            score += 4
    for kw in REJECT_SOFT:
        if kw in text:
            score -= 20

    if video.get("width", 0) > video.get("height", 0):
        score += 10

    dur = video.get("duration", 0)
    if 5 <= dur <= 45:
        score += 20
    elif 45 < dur <= 90:
        score += 5
    elif dur > 90:
        score -= 15

    for vf in video.get("video_files", []):
        if vf.get("width", 0) >= 1280:
            score += 5
            break
    return score


def _best_file(files: list) -> dict | None:
    if not files:
        return None
    good = [v for v in files if v.get("width", 0) <= 1920 and v.get("link")]
    pool = good or [v for v in files if v.get("link")]
    return max(pool, key=lambda x: x.get("width", 0)) if pool else None


def _load_history() -> dict:
    os.makedirs(CLIPS_BASE, exist_ok=True)
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_history(h: dict):
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f, indent=2)


def _hkey(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _fetch_best(exercise, needed: int, headers: dict, used_ids: list) -> list:
    name     = exercise["name"] if isinstance(exercise, dict) else str(exercise)
    queries  = _build_queries(exercise)
    seen_ids = set()
    all_vids = []

    for query in queries:
        fetch_n = min(20, max(needed * 6, 15))
        url     = (f"https://api.pexels.com/videos/search"
                   f"?query={requests.utils.quote(query)}"
                   f"&per_page={fetch_n}&orientation=landscape")
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            for vid in resp.json().get("videos", []):
                vid_id = vid.get("id")
                if vid_id and vid_id not in seen_ids:
                    seen_ids.add(vid_id)
                    s = _score(vid, name)
                    if s > -900:
                        vid["_score"] = s
                        all_vids.append(vid)
        except Exception as e:
            print(f"    Query failed: {e}")

        fresh_good = [v for v in all_vids
                      if v["_score"] >= 25 and v.get("id") not in used_ids]
        if len(fresh_good) >= needed:
            break

    all_vids.sort(key=lambda v: v["_score"], reverse=True)
    fresh  = [v for v in all_vids if v.get("id") not in used_ids]
    reused = [v for v in all_vids if v.get("id") in used_ids]
    result = fresh[:needed] if fresh else reused[:needed]

    if result:
        score_str = result[0]['_score']
        print(f"    Score:{score_str:4d}  Fresh:{len(fresh)}  Used:{len(reused)}  Total:{len(all_vids)}")
        if result[0]["_score"] < 15:
            print(f"    WARNING: Low confidence for '{name}' — consider a stock clip")
    return result


def download_exercises(exercise_list: list = None) -> str:
    os.makedirs(CLIPS_BASE, exist_ok=True)
    today        = datetime.datetime.now().strftime("%Y%m%d")
    count        = len([d for d in os.listdir(CLIPS_BASE) if d.startswith(today)]) + 1
    clips_folder = os.path.join(CLIPS_BASE, f"{today}_video_{count}")
    os.makedirs(clips_folder, exist_ok=True)

    if exercise_list is None:
        print("\nEnter exercises (comma-separated).")
        print("Example: push ups, squats, jumping jacks, burpees, plank")
        raw          = input("Exercises: ")
        exercise_list = [e.strip() for e in raw.split(",") if e.strip()]

    if not exercise_list:
        print("  No exercises.")
        return clips_folder

    raw = input("How many video clips per exercise? (default 1): ").strip()
    try:
        per_exercise = max(1, int(raw))
    except ValueError:
        per_exercise = 1

    headers  = {"Authorization": PEXELS_API_KEY}
    history  = _load_history()
    total_ok = 0

    for exercise in exercise_list:
        name     = exercise["name"] if isinstance(exercise, dict) else str(exercise)
        key      = _hkey(name)
        used_ids = history.get(key, [])
        print(f"\n  [{name}]  (used before: {len(used_ids)})")

        videos = _fetch_best(exercise, per_exercise, headers, used_ids)
        if not videos:
            print(f"  No results for '{name}' — skipping.")
            continue

        for i, vid in enumerate(videos, start=1):
            vf = _best_file(vid.get("video_files", []))
            if not vf:
                continue
            filename = os.path.join(clips_folder, f"{key}_{i}.mp4")
            if os.path.exists(filename) and os.path.getsize(filename) > 5_000:
                print(f"  Already downloaded.")
                total_ok += 1
                continue
            print(f"  Downloading {vf.get('width',0)}x{vf.get('height',0)} → {os.path.basename(filename)}")
            try:
                r = requests.get(vf["link"], stream=True, timeout=60)
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                vid_id = vid.get("id")
                if vid_id:
                    history.setdefault(key, [])
                    if vid_id not in history[key]:
                        history[key].append(vid_id)
                total_ok += 1
                print(f"  Saved.")
            except Exception as e:
                print(f"  Failed: {e}")

    _save_history(history)
    print(f"\n  Done — {total_ok} clips in: {clips_folder}")
    return clips_folder


if __name__ == "__main__":
    folder = download_exercises()
    print("Folder:", folder)