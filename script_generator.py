# script_generator.py
"""
Generates workout narration segments with:
  - Richer exercise-specific coaching cues (not generic)
  - Proper timing: "30 seconds, go!"
  - Varied motivational lines per exercise type
  - Better fat-burn focused language
"""

import os
import random


# ── Intro variations ──────────────────────────────────────
INTROS = [
    "Welcome to your Fat Burn Home Workout! No equipment, no excuses. I am your coach today and we are going to work every muscle in your body. Get ready!",
    "Hey everyone! Welcome to your Fat Burn session. This is a high intensity home workout — no gym needed. Just bring your energy and let us torch some calories together!",
    "What is up! It is time for your Fat Burn Workout. Short, intense, and incredibly effective. We are burning fat and building endurance today. Stay with me the whole way!",
    "Welcome! Today is your full body fat burn session. Every exercise targets multiple muscle groups to maximize your calorie burn. No equipment needed — just you and your effort!",
    "Ready to sweat? This is your home fat burn workout. We are going through powerful exercises that will boost your metabolism and keep your body burning calories even after we finish!",
]

COUNTDOWNS = [
    "Starting in 3. 2. 1. Let us go!",
    "Get into position. 3. 2. 1. Go!",
    "Here we go in 3. 2. 1. Move!",
    "Are you ready? 3. 2. 1. Start!",
]

# ── Exercise-specific coaching cues ───────────────────────
# Key = exercise name (lowercase), Value = list of coaching phrases
EXERCISE_CUES = {
    "jumping jacks": [
        "Arms wide, legs wide — keep that rhythm! Jump those feet out and bring those arms up overhead!",
        "Full range of motion! Arms all the way up, feet all the way out. This is pure cardio!",
        "Stay light on your feet! Soft knees, fast pace. Jumping jacks get your heart rate up fast!",
    ],
    "squat": [
        "Feet shoulder width apart! Push your hips back and down. Keep that chest up and drive through your heels!",
        "Deep squat! Go below parallel if you can. Squeeze those glutes at the top. This builds power!",
        "Keep your weight in your heels! Knees tracking over your toes. Feel those quads burning!",
    ],
    "squats": [
        "Feet shoulder width apart! Chest up, core tight. Push those hips back — deep squat!",
        "Power through those heels! Squeeze at the top every rep. Squats are the king of exercises!",
    ],
    "push up": [
        "Hands just outside shoulder width! Body in a straight line from head to heels. Lower your chest to the floor!",
        "Core tight the whole time! Do not let those hips sag. Full range of motion — chest touches the ground!",
        "Control the descent! Lower for 2, press up fast. Feel every rep in your chest and triceps!",
    ],
    "push ups": [
        "Hands just outside shoulder width! Body straight, core braced. Full chest to floor!",
        "No sagging hips! Tight core, tight glutes. This works your entire upper body!",
    ],
    "burpee": [
        "Squat down, kick those feet back, do a push up, jump those feet back in, then explode up with a jump! Full body power!",
        "This is the ultimate fat burner! Down to the floor, push up, feet in, jump up, reach for the sky!",
        "Burpees hit everything! Legs, chest, core, cardio — all in one move. Push through the burn!",
    ],
    "burpees": [
        "The king of fat burn exercises! Drop down, push up, jump up. Explosive and powerful!",
        "Every burpee burns massive calories! Keep the tempo up — down, up, jump!",
    ],
    "plank": [
        "Elbows under shoulders! Body in a perfect straight line. Squeeze your core like someone is about to punch you!",
        "Do not let those hips drop or rise! Breathe steadily. Your core is working hard right now!",
        "Hold strong! The plank builds unbreakable core strength. Squeeze everything — abs, glutes, legs!",
    ],
    "lunge": [
        "Big step forward! Back knee drops to just above the floor. Front knee stays over your ankle!",
        "Alternate legs each rep! Keep your torso upright. Feel the stretch and burn in those quads!",
        "Long stride, deep drop! Push through that front heel to stand back up. Balance and power!",
    ],
    "lunges": [
        "Big step, deep drop! Knee hovers above the floor. Alternate legs with control!",
        "Keep your upper body tall! Core braced. These sculpt your legs and glutes beautifully!",
    ],
    "mountain climber": [
        "Hands under shoulders, hips level! Drive those knees toward your chest as fast as you can. Cardio and core together!",
        "Keep that core tight! The faster you go, the more fat you burn. Running in a plank position!",
        "Pump those knees! Keep your hips down. Mountain climbers are a full body cardio blast!",
    ],
    "mountain climbers": [
        "Fast knees, tight core, level hips! This is cardio and abs combined into one killer move!",
        "Drive those knees in fast! Keep your back flat. Mountain climbers torch calories instantly!",
    ],
    "high knees": [
        "Drive those knees up to hip height! Pump your arms and stay on the balls of your feet. Pure cardio!",
        "Knees up, arms pumping! This is running in place but harder. Get that heart rate flying!",
        "Higher! Get those knees up! Stay light on your feet and keep the pace fast. Feel that burn!",
    ],
    "crunch": [
        "Feet flat on the floor, hands behind your head! Curl up using your abs — do not pull on your neck!",
        "Slow and controlled! Squeeze those abs at the top. Lower back stays in contact with the floor!",
        "Feel every crunch in your core! No swinging — pure abdominal contraction every single rep!",
    ],
    "crunches": [
        "Hands behind your head, elbows wide! Curl up with your abs. Short, sharp contractions!",
        "Squeeze the abs hard at the top! Slow down, do not rush. Quality beats quantity!",
    ],
    "sit up": [
        "Feet flat, arms across your chest! Curl all the way up and lower back down with control!",
        "Full range of motion! Touch your elbows to your knees at the top. Exhale as you rise!",
    ],
    "sit ups": [
        "All the way up, all the way down! Breathe out on the way up. Core engaged throughout!",
        "Control the descent! Do not just fall back. Every inch of this move is working your abs!",
    ],
    "jump squat": [
        "Squat down deep, then explode up as high as you can! Land softly with bent knees. Plyometric power!",
        "Hips back, deep squat, then launch! This is plyometric training — it spikes your heart rate and burns fat fast!",
    ],
    "jump squats": [
        "Deep squat, explosive jump! Land softly. This builds power and burns calories at the same time!",
        "Lower, lower, then explode! Soft landing, straight back into the next squat. Keep the power!",
    ],
    "glute bridge": [
        "Feet flat on the floor, hips width apart! Drive your hips up and squeeze your glutes hard at the top!",
        "Hold at the top for a second! Really squeeze those glutes. Lower slow, drive up fast!",
    ],
    "hip thrust": [
        "Upper back on the ground, feet planted! Thrust those hips up and hold the squeeze at the top!",
        "Drive through your heels! Hips fully extended at the top — maximum glute contraction!",
    ],
    "russian twist": [
        "Lean back at 45 degrees, feet off the floor! Rotate side to side — touch the floor each time!",
        "Twist from your waist, not your arms! Keep your back straight. This targets your obliques hard!",
    ],
    "leg raise": [
        "Flat on your back, hands under your hips! Raise those legs up to 90 degrees and lower slow!",
        "Do not let your feet touch the floor! Keep constant tension on your lower abs. Control every inch!",
    ],
    "flutter kick": [
        "Legs just off the floor, small rapid kicks! Keep your lower back pressed down. Pure lower ab burn!",
        "Short and fast kicks! The closer to the floor, the harder it is. Keep going!",
    ],
    "donkey kick": [
        "On all fours, drive one heel up toward the ceiling! Squeeze your glute hard at the top each rep!",
        "Hips stay square to the floor! Only your leg moves. This perfectly isolates the glute muscles!",
    ],
    "fire hydrant": [
        "On all fours, lift your knee out to the side like a dog! Keep your hips level and squeeze at the top!",
        "Slow and controlled! This targets the hip abductors and outer glutes that squats miss!",
    ],
    "wall sit": [
        "Back flat against the wall, thighs parallel to the floor! Hold that position and breathe!",
        "Do not let those thighs come up! Hold the 90 degree position. This burns your quads deeply!",
    ],
    "tricep dip": [
        "Hands on a chair behind you, elbows bending straight back! Lower down and press back up!",
        "Keep your hips close to the chair! Elbows go straight back — not flared out. Feel those triceps!",
    ],
    "bicep curl": [
        "Palms up, elbows pinned to your sides! Curl all the way up and lower all the way down. Full range!",
        "No swinging! Let your biceps do all the work. Squeeze hard at the top of every curl!",
    ],
    "running": [
        "Pump those arms, drive your knees! This is pure cardio. Maintain a strong, steady pace!",
        "Heel to toe, strong arm drive! Running burns more calories per minute than almost any other exercise!",
    ],
    "high knees run": [
        "Knees up to hip height! Arms pumping hard. Stay on the balls of your feet for speed!",
        "Drive those knees higher! The faster you go, the more fat you burn. Push your limits!",
    ],
    "bear crawl": [
        "Hands and feet on the floor, knees just hovering! Crawl forward — opposite hand and foot together!",
        "Keep your hips low and level! This works your shoulders, core, and legs simultaneously!",
    ],
    "inchworm": [
        "Bend at the hips, walk your hands out to a plank, do a push up, then walk hands back! Full body warmup!",
        "Slow and deliberate! Each inchworm works your hamstrings, core, chest, and shoulders all at once!",
    ],
    "speed skater": [
        "Leap side to side on one foot! Reach your opposite hand toward the floor. Pure lateral cardio!",
        "Big jumps side to side! This works your inner and outer thighs while spiking your heart rate!",
    ],
    "box jump": [
        "Swing your arms for momentum! Explode up onto the box or jump and land softly. Plyometric power!",
        "Soft landing, full squat position! Box jumps build explosive leg strength and burn serious calories!",
    ],
    "pike push up": [
        "Hips high in a pike position! Lower your head toward the floor between your hands. Shoulder press movement!",
        "This targets your shoulders like an overhead press! Keep your legs straight and core braced!",
    ],
    "lateral raise": [
        "Arms out to the side, raise to shoulder height! Slow and controlled. Feel those deltoids working!",
        "Do not swing! Raise with control and lower slow. Your shoulder muscles are under tension the whole time!",
    ],
}

# Generic motivational lines (used when exercise not in EXERCISE_CUES)
GENERIC_MOTIVATIONS = [
    "Keep that pace up! Every second counts. You are burning fat right now!",
    "Strong and steady! Your body is working hard. Do not quit on yourself!",
    "Push through! The discomfort is temporary. The results are permanent!",
    "You are doing incredible! Stay focused and keep moving!",
    "Breathe through it! You are stronger than you think!",
    "Last few seconds! Give it absolutely everything you have got!",
    "No stopping! Each rep brings you closer to your goal. Keep going!",
    "Feel that burn! That is fat leaving your body right now!",
]

REST_LINES = [
    "Rest! Shake out your arms and legs. Catch your breath — next exercise coming up soon.",
    "Take a breath! Walk it off and stay loose. Your next exercise is coming up fast.",
    "Active rest! Keep moving gently. Shake it out. You are doing amazing so far.",
    "Rest period! Breathe deep and recover. The harder the rest feels, the harder you worked.",
    "Recover! Roll your shoulders, shake your legs. Get ready because the next exercise is coming!",
]

OUTROS = [
    "Incredible work! You just completed a full fat burn home workout! Your metabolism will be elevated for hours. Drink some water, stretch it out, and I will see you in the next one!",
    "That is a wrap! You gave everything today and your body will thank you for it. Subscribe for more home workouts and I will see you tomorrow!",
    "You crushed it! That was a serious calorie-burning session. Cool down, hydrate well, and come back tomorrow for another round. You are building a great habit!",
    "Fantastic effort! That is how you burn fat at home with zero equipment. Like this video if it helped you, subscribe for daily workouts, and I will see you next time!",
    "Well done on finishing! Every workout like this builds your fitness and burns fat for hours afterward. Rest up, eat clean, and come back strong tomorrow!",
]


def _clean_name_from_file(filename: str) -> str:
    name  = os.path.splitext(filename)[0]
    parts = name.split("_")
    if parts and parts[-1].isdigit():
        parts = parts[:-1]
    return " ".join(parts).replace("-", " ").title()


def _resolve_clips(clip_files: list) -> list:
    resolved = []
    for item in clip_files:
        if isinstance(item, dict):
            resolved.append({
                "file":     item["file"],
                "exercise": item.get("exercise") or _clean_name_from_file(item["file"]),
            })
        else:
            resolved.append({
                "file":     item,
                "exercise": _clean_name_from_file(item),
            })
    return resolved


def _get_exercise_cue(exercise: str) -> str:
    """Get a specific coaching cue for this exercise, or a generic one."""
    key  = exercise.lower().strip()
    cues = EXERCISE_CUES.get(key)
    if cues:
        return random.choice(cues)
    # Try partial match
    for k, v in EXERCISE_CUES.items():
        if k in key or key in k:
            return random.choice(v)
    return random.choice(GENERIC_MOTIVATIONS)


def generate_script_segments(clip_files: list, cfg=None) -> list:
    if cfg is None:
        ex_dur   = 30
        rest_dur = 15
    else:
        ex_dur   = cfg.exercise_duration
        rest_dur = cfg.rest_duration

    if not clip_files:
        return [{"type": "intro", "text": "Welcome to your Fat Burn Workout!", "file": None}]

    clips     = _resolve_clips(clip_files)
    segments  = []
    rest_pool = REST_LINES.copy()
    random.shuffle(rest_pool)

    # ── Intro ──────────────────────────────────────────
    intro_text = random.choice(INTROS) + "  " + random.choice(COUNTDOWNS)
    segments.append({"type": "intro", "text": intro_text, "file": None})

    # ── Exercises ──────────────────────────────────────
    for idx, clip in enumerate(clips):
        cue = _get_exercise_cue(clip["exercise"])
        ex_text = (
            f"Go!  {clip['exercise']}!  "
            f"{ex_dur} seconds!  "
            f"{cue}"
        )
        segments.append({
            "type":          "exercise",
            "text":          ex_text,
            "file":          clip["file"],
            "exercise":      clip["exercise"],
            "clip_duration": ex_dur,
        })

        if idx < len(clips) - 1:
            rest_text = rest_pool[idx % len(rest_pool)]
            segments.append({
                "type":          "rest",
                "text":          rest_text,
                "file":          None,
                "rest_duration": rest_dur,
            })

    # ── Outro ──────────────────────────────────────────
    segments.append({"type": "outro", "text": random.choice(OUTROS), "file": None})

    return segments


if __name__ == "__main__":
    from workout_config import WorkoutConfig
    cfg   = WorkoutConfig(30, 15)
    clips = ["push_up_1.mp4", "jumping_jacks_1.mp4", "squat_1.mp4"]
    for s in generate_script_segments(clips, cfg):
        dur = f"  clip={s.get('clip_duration')}s" if s.get("clip_duration") else \
              f"  rest={s.get('rest_duration')}s" if s.get("rest_duration") else ""
        print(f"[{s['type']:8s}]{dur}  {s['text'][:80]}")