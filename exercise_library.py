# exercise_library.py
"""
Library of body-weight, no-machine fat-burn home exercises.
Organised by intensity: EASY, MEDIUM, INTENSE.

Used for automatic exercise selection.
Each exercise has:
  - name        : display name and Pexels search key
  - intensity   : "easy" | "medium" | "intense"
  - muscle      : primary muscle group (for variety balancing)
  - pexels_query: best search phrase for Pexels (no-machine, body only)
"""

import random

# ─────────────────────────────────────────────────────────
# EXERCISE LIBRARY — body weight, home, NO MACHINE
# ─────────────────────────────────────────────────────────
EXERCISES = [

    # ── EASY ─────────────────────────────────────────────
    {"name": "Arm Circles",         "intensity": "easy",   "muscle": "shoulders",
     "pexels_query": "arm circles exercise warmup bodyweight"},
    {"name": "Neck Rolls",          "intensity": "easy",   "muscle": "neck",
     "pexels_query": "neck roll stretch exercise warmup"},
    {"name": "Shoulder Rolls",      "intensity": "easy",   "muscle": "shoulders",
     "pexels_query": "shoulder roll exercise warmup"},
    {"name": "Marching In Place",   "intensity": "easy",   "muscle": "legs",
     "pexels_query": "marching in place exercise cardio"},
    {"name": "Standing Side Bend",  "intensity": "easy",   "muscle": "core",
     "pexels_query": "standing side bend stretch exercise"},
    {"name": "Hip Circles",         "intensity": "easy",   "muscle": "hips",
     "pexels_query": "hip circles exercise mobility"},
    {"name": "Wall Sit",            "intensity": "easy",   "muscle": "legs",
     "pexels_query": "wall sit exercise legs bodyweight"},
    {"name": "Standing Calf Raise", "intensity": "easy",   "muscle": "calves",
     "pexels_query": "calf raise exercise standing bodyweight"},
    {"name": "Glute Bridge",        "intensity": "easy",   "muscle": "glutes",
     "pexels_query": "glute bridge exercise floor bodyweight"},
    {"name": "Superman",            "intensity": "easy",   "muscle": "back",
     "pexels_query": "superman exercise back extension floor"},
    {"name": "Cat Cow Stretch",     "intensity": "easy",   "muscle": "back",
     "pexels_query": "cat cow stretch exercise yoga floor"},
    {"name": "Leg Swing",           "intensity": "easy",   "muscle": "hips",
     "pexels_query": "leg swing exercise dynamic stretch"},
    {"name": "Step Touch",          "intensity": "easy",   "muscle": "legs",
     "pexels_query": "step touch exercise cardio low impact"},
    {"name": "Torso Twist",         "intensity": "easy",   "muscle": "core",
     "pexels_query": "torso twist exercise standing core"},
    {"name": "Inchworm",            "intensity": "easy",   "muscle": "full body",
     "pexels_query": "inchworm exercise stretch bodyweight"},

    # ── MEDIUM ────────────────────────────────────────────
    {"name": "Jumping Jacks",       "intensity": "medium", "muscle": "full body",
     "pexels_query": "jumping jacks exercise cardio bodyweight"},
    {"name": "High Knees",          "intensity": "medium", "muscle": "legs",
     "pexels_query": "high knees exercise running cardio"},
    {"name": "Squats",              "intensity": "medium", "muscle": "legs",
     "pexels_query": "squat exercise bodyweight fitness no equipment"},
    {"name": "Lunges",              "intensity": "medium", "muscle": "legs",
     "pexels_query": "lunge exercise bodyweight legs fitness"},
    {"name": "Push Ups",            "intensity": "medium", "muscle": "chest",
     "pexels_query": "push up exercise bodyweight floor fitness"},
    {"name": "Crunches",            "intensity": "medium", "muscle": "abs",
     "pexels_query": "crunch exercise abs bodyweight floor"},
    {"name": "Mountain Climbers",   "intensity": "medium", "muscle": "full body",
     "pexels_query": "mountain climber exercise cardio bodyweight floor"},
    {"name": "Plank",               "intensity": "medium", "muscle": "core",
     "pexels_query": "plank exercise core bodyweight floor"},
    {"name": "Butt Kicks",          "intensity": "medium", "muscle": "legs",
     "pexels_query": "butt kicks exercise running cardio"},
    {"name": "Side Lunges",         "intensity": "medium", "muscle": "legs",
     "pexels_query": "side lunge exercise lateral legs bodyweight"},
    {"name": "Russian Twist",       "intensity": "medium", "muscle": "abs",
     "pexels_query": "russian twist exercise abs bodyweight floor"},
    {"name": "Donkey Kicks",        "intensity": "medium", "muscle": "glutes",
     "pexels_query": "donkey kick exercise glute bodyweight floor"},
    {"name": "Fire Hydrants",       "intensity": "medium", "muscle": "glutes",
     "pexels_query": "fire hydrant exercise hip glute bodyweight"},
    {"name": "Reverse Lunges",      "intensity": "medium", "muscle": "legs",
     "pexels_query": "reverse lunge exercise bodyweight legs"},
    {"name": "Flutter Kicks",       "intensity": "medium", "muscle": "abs",
     "pexels_query": "flutter kick exercise abs bodyweight floor"},
    {"name": "Leg Raises",          "intensity": "medium", "muscle": "abs",
     "pexels_query": "leg raise exercise abs bodyweight floor"},
    {"name": "Speed Skaters",       "intensity": "medium", "muscle": "legs",
     "pexels_query": "speed skater exercise cardio lateral jump"},
    {"name": "Bear Crawl",          "intensity": "medium", "muscle": "full body",
     "pexels_query": "bear crawl exercise bodyweight floor"},
    {"name": "Hip Thrust",          "intensity": "medium", "muscle": "glutes",
     "pexels_query": "hip thrust exercise glute bodyweight floor"},
    {"name": "Tricep Dips",         "intensity": "medium", "muscle": "arms",
     "pexels_query": "tricep dip exercise arms bodyweight chair"},
    {"name": "Sit Ups",             "intensity": "medium", "muscle": "abs",
     "pexels_query": "sit up exercise abs bodyweight floor"},
    {"name": "Step Ups",            "intensity": "medium", "muscle": "legs",
     "pexels_query": "step up exercise legs bodyweight"},

    # ── INTENSE ───────────────────────────────────────────
    {"name": "Burpees",             "intensity": "intense", "muscle": "full body",
     "pexels_query": "burpee exercise full body fitness training"},
    {"name": "Jump Squats",         "intensity": "intense", "muscle": "legs",
     "pexels_query": "jump squat exercise plyometric bodyweight"},
    {"name": "Jumping Lunges",      "intensity": "intense", "muscle": "legs",
     "pexels_query": "jump lunge exercise plyometric legs"},
    {"name": "Box Jumps",           "intensity": "intense", "muscle": "legs",
     "pexels_query": "box jump exercise plyometric legs"},
    {"name": "Sprint In Place",     "intensity": "intense", "muscle": "full body",
     "pexels_query": "sprint in place exercise running cardio intense"},
    {"name": "Tuck Jumps",          "intensity": "intense", "muscle": "full body",
     "pexels_query": "tuck jump exercise plyometric cardio"},
    {"name": "Explosive Push Ups",  "intensity": "intense", "muscle": "chest",
     "pexels_query": "explosive push up plyometric clap push up exercise"},
    {"name": "Plank Jacks",         "intensity": "intense", "muscle": "full body",
     "pexels_query": "plank jack exercise cardio bodyweight"},
    {"name": "Broad Jumps",         "intensity": "intense", "muscle": "legs",
     "pexels_query": "broad jump exercise plyometric legs bodyweight"},
    {"name": "Spiderman Push Ups",  "intensity": "intense", "muscle": "chest",
     "pexels_query": "spiderman push up exercise bodyweight"},
    {"name": "Skater Jumps",        "intensity": "intense", "muscle": "legs",
     "pexels_query": "skater jump exercise lateral plyometric cardio"},
    {"name": "Bear Plank Shoulder Tap", "intensity": "intense", "muscle": "core",
     "pexels_query": "shoulder tap plank exercise core bodyweight"},
    {"name": "Squat Pulse",         "intensity": "intense", "muscle": "legs",
     "pexels_query": "squat pulse exercise legs bodyweight intense"},
    {"name": "Hollow Body Hold",    "intensity": "intense", "muscle": "core",
     "pexels_query": "hollow body hold exercise core abs"},
    {"name": "V Ups",               "intensity": "intense", "muscle": "abs",
     "pexels_query": "v up exercise abs bodyweight floor"},
]


INTENSITY_LEVELS = {
    "easy":    {"label": "Easy",    "emoji": "🟢", "desc": "Low impact, beginner friendly"},
    "medium":  {"label": "Medium",  "emoji": "🟡", "desc": "Moderate intensity, fat burning"},
    "intense": {"label": "Intense", "emoji": "🔴", "desc": "High intensity, maximum calorie burn"},
}

# Intensity mix ratios for each level
INTENSITY_MIXES = {
    "easy":    {"easy": 0.7, "medium": 0.3, "intense": 0.0},
    "medium":  {"easy": 0.2, "medium": 0.6, "intense": 0.2},
    "intense": {"easy": 0.0, "medium": 0.3, "intense": 0.7},
}


def get_by_intensity(level: str) -> list:
    """Return all exercises matching intensity level."""
    return [e for e in EXERCISES if e["intensity"] == level]


def auto_select_exercises(count: int, level: str) -> list:
    """
    Auto-select `count` exercises for given intensity level.
    Uses a mix ratio to keep variety while matching the desired intensity.
    Ensures no same muscle group back-to-back.
    Returns list of exercise dicts.
    """
    level = level.lower()
    mix   = INTENSITY_MIXES.get(level, INTENSITY_MIXES["medium"])

    # Build weighted pool
    pool = []
    for intensity, ratio in mix.items():
        if ratio <= 0:
            continue
        exercises = get_by_intensity(intensity)
        n         = max(1, round(count * ratio)) if ratio > 0 else 0
        random.shuffle(exercises)
        pool.extend(exercises[:n])

    # Fill if short
    random.shuffle(pool)
    if len(pool) < count:
        all_ex = EXERCISES.copy()
        random.shuffle(all_ex)
        for ex in all_ex:
            if ex not in pool:
                pool.append(ex)
            if len(pool) >= count:
                break

    # Anti-consecutive-muscle filter
    selected = []
    last_muscle = None
    remaining   = pool.copy()

    for _ in range(count):
        # Try to pick one that doesn't repeat last muscle group
        candidates = [e for e in remaining if e["muscle"] != last_muscle]
        if not candidates:
            candidates = remaining
        if not candidates:
            break
        pick = random.choice(candidates)
        selected.append(pick)
        remaining.remove(pick)
        last_muscle = pick["muscle"]

    return selected[:count]


def ask_intensity() -> str:
    """Ask user to choose workout intensity. Returns 'easy', 'medium', or 'intense'."""
    print("\n  Choose workout intensity:")
    for key, info in INTENSITY_LEVELS.items():
        print(f"    [{list(INTENSITY_LEVELS.keys()).index(key)+1}] {info['emoji']} {info['label']:8s} — {info['desc']}")
    while True:
        raw = input("  Enter 1, 2, or 3: ").strip()
        mapping = {"1": "easy", "2": "medium", "3": "intense"}
        if raw in mapping:
            chosen = mapping[raw]
            info   = INTENSITY_LEVELS[chosen]
            print(f"  Selected: {info['emoji']} {info['label']}")
            return chosen
        print("  Please enter 1, 2, or 3.")


if __name__ == "__main__":
    level     = ask_intensity()
    exercises = auto_select_exercises(6, level)
    print(f"\nSelected {len(exercises)} exercises for {level} workout:")
    for i, ex in enumerate(exercises, 1):
        print(f"  {i}. {ex['name']:30s}  [{ex['intensity']:7s}]  {ex['muscle']}")
