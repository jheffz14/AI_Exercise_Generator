# workout_config.py
"""
Asks the user for workout timing settings ONCE at the start.
Returns a WorkoutConfig object that every module uses.

Settings collected:
  - exercise_duration  : how many seconds each exercise clip plays  (e.g. 30)
  - rest_duration      : how many seconds the REST card shows        (e.g. 15)

These values flow through:
  script_generator  → narration says "do X for 30 seconds"
  video_creator     → clip loops/trims to exactly that duration
  voice_generator   → audio measured and synced as usual
"""


class WorkoutConfig:
    def __init__(self, exercise_duration: int, rest_duration: int):
        self.exercise_duration = exercise_duration   # seconds
        self.rest_duration     = rest_duration       # seconds

    def __repr__(self):
        return (f"WorkoutConfig("
                f"exercise={self.exercise_duration}s, "
                f"rest={self.rest_duration}s)")


def ask_workout_config() -> WorkoutConfig:
    """Interactively ask the user for timing settings."""

    print("\n" + "-" * 45)
    print("  WORKOUT TIMING SETTINGS")
    print("-" * 45)

    # ── Exercise duration ──────────────────────────────
    print("\nHow long should each exercise last?")
    print("  Common choices: 20, 30, 40, 45, 60 seconds")
    while True:
        raw = input("  Exercise duration (seconds) [default 30]: ").strip()
        if raw == "":
            ex_dur = 30
            break
        try:
            ex_dur = int(raw)
            if ex_dur < 5:
                print("  Minimum is 5 seconds. Try again.")
                continue
            if ex_dur > 300:
                print("  Maximum is 300 seconds (5 min). Try again.")
                continue
            break
        except ValueError:
            print("  Please enter a whole number.")

    # ── Rest duration ──────────────────────────────────
    print(f"\nHow long should the REST period be between exercises?")
    print("  Common choices: 10, 15, 20, 30 seconds")
    while True:
        raw = input("  Rest duration (seconds) [default 15]: ").strip()
        if raw == "":
            rest_dur = 15
            break
        try:
            rest_dur = int(raw)
            if rest_dur < 0:
                print("  Cannot be negative.")
                continue
            if rest_dur > 120:
                print("  Maximum is 120 seconds. Try again.")
                continue
            break
        except ValueError:
            print("  Please enter a whole number.")

    cfg = WorkoutConfig(exercise_duration=ex_dur, rest_duration=rest_dur)
    print(f"\n  Settings: {ex_dur}s exercise  /  {rest_dur}s rest")

    # Show estimated total time
    print("  (Total time will depend on number of exercises)")

    return cfg


def estimate_duration(num_exercises: int, cfg: WorkoutConfig) -> str:
    """Return a human-readable estimated video duration string."""
    intro_s  = 8    # approximate intro narration
    outro_s  = 6
    ex_total = num_exercises * cfg.exercise_duration
    rest_total = (num_exercises - 1) * cfg.rest_duration if num_exercises > 1 else 0
    total    = intro_s + ex_total + rest_total + outro_s
    mins     = total // 60
    secs     = total % 60
    if mins > 0:
        return f"~{mins}m {secs}s"
    return f"~{secs}s"


if __name__ == "__main__":
    cfg = ask_workout_config()
    print(cfg)
    print("Estimated for 5 exercises:", estimate_duration(5, cfg))
