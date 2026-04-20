from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

# ----------------------------
# Exercise library
# ----------------------------
# equipment rules:
# - [] means no equipment needed
# - ["dumbbells"] means must have dumbbells
# - ["barbell", "squat_rack"] means must have both
# - ["bike|treadmill|rower"] means one of those is enough
EXERCISES = {
    "upper_body": [
        {"name": "Push-ups", "sets": "4", "reps": "10-15", "equipment": [], "video_id": "IODxDxX7oi4"},
        {"name": "Pike Push-ups", "sets": "3", "reps": "8-12", "equipment": [], "video_id": "qHQ_E-f5278"},
        {"name": "Dumbbell Bench Press", "sets": "4", "reps": "8-12", "equipment": ["dumbbells"], "video_id": "VmB1G1K7v94"},
        {"name": "One-Arm Dumbbell Row", "sets": "4", "reps": "8-12 each", "equipment": ["dumbbells"], "video_id": "pYcpY20QaE8"},
        {"name": "Barbell Bench Press", "sets": "4", "reps": "5-8", "equipment": ["barbell", "bench"], "video_id": "rT7DgCr-3pg"},
        {"name": "Overhead Press", "sets": "3", "reps": "6-10", "equipment": ["barbell"], "video_id": "2yjwXTZQDDI"},
    ],
    "lower_body": [
        {"name": "Bodyweight Squat", "sets": "4", "reps": "15-20", "equipment": [], "video_id": "aclHkVaku9U"},
        {"name": "Reverse Lunge", "sets": "3", "reps": "10 each", "equipment": [], "video_id": "wrwwXE_x-pQ"},
        {"name": "Goblet Squat", "sets": "4", "reps": "8-12", "equipment": ["dumbbells|kettlebell"], "video_id": "MeIiIdhvXT4"},
        {"name": "Romanian Deadlift (DB)", "sets": "4", "reps": "8-12", "equipment": ["dumbbells"], "video_id": "0YONJjY6i6Q"},
        {"name": "Back Squat", "sets": "5", "reps": "5", "equipment": ["barbell", "squat_rack"], "video_id": "ultWZbUMPL8"},
        {"name": "Deadlift", "sets": "4", "reps": "4-6", "equipment": ["barbell"], "video_id": "op9kVnSso6Q"},
    ],
    "core": [
        {"name": "Plank", "sets": "4", "reps": "30-60 sec", "equipment": [], "video_id": "ASdvN_XEl_c"},
        {"name": "Dead Bug", "sets": "3", "reps": "10 each", "equipment": [], "video_id": "4XLEnwUr8S4"},
        {"name": "Russian Twist", "sets": "3", "reps": "20 total", "equipment": ["dumbbells|kettlebell"], "video_id": "wkD8rjkodUI"},
        {"name": "Cable Crunch", "sets": "4", "reps": "12-15", "equipment": ["cable_machine"], "video_id": "AV5PmZJIrrw"},
    ],
    "full_body": [
        {"name": "Push-ups", "sets": "3", "reps": "10-15", "equipment": [], "video_id": "IODxDxX7oi4"},
        {"name": "Bodyweight Squat", "sets": "3", "reps": "15-20", "equipment": [], "video_id": "aclHkVaku9U"},
        {"name": "Goblet Squat", "sets": "4", "reps": "8-12", "equipment": ["dumbbells|kettlebell"], "video_id": "MeIiIdhvXT4"},
        {"name": "Dumbbell Row", "sets": "4", "reps": "8-12", "equipment": ["dumbbells"], "video_id": "pYcpY20QaE8"},
        {"name": "Back Squat", "sets": "4", "reps": "5-8", "equipment": ["barbell", "squat_rack"], "video_id": "ultWZbUMPL8"},
        {"name": "Bench Press", "sets": "4", "reps": "5-8", "equipment": ["barbell", "bench"], "video_id": "rT7DgCr-3pg"},
    ],
}

GOAL_FINISHERS = {
    "fat_loss": [
        {"name": "HIIT Finisher", "sets": "5 rounds", "reps": "40s on / 20s off", "equipment": [], "video_id": "ml6cT4AZdqI"}
    ],
    "endurance": [
        {"name": "Zone 2 Cardio", "sets": "1", "reps": "20-40 min", "equipment": ["bike|treadmill|rower"], "video_id": "x9Q6xg2z2iE"}
    ],
    "strength": []
}


def has_required_equipment(required_rules: list[str], selected: set[str]) -> bool:
    """
    required_rules examples:
    - []                    -> no equipment needed
    - ["dumbbells"]         -> must have dumbbells
    - ["barbell","bench"]   -> must have both
    - ["bike|treadmill"]    -> has one of these
    """
    if not required_rules:
        return True

    for rule in required_rules:
        if "|" in rule:
            options = set(rule.split("|"))
            if not (options & selected):
                return False
        else:
            if rule not in selected:
                return False
    return True


def filter_exercises_for_equipment(exercises: list[dict], equipment_items: list[str]) -> list[dict]:
    selected = {e.strip().lower() for e in equipment_items if e.strip() and e.strip().lower() != "none"}
    filtered = [ex for ex in exercises if has_required_equipment(ex["equipment"], selected)]

    # fallback if user selected gear that leaves nothing: return bodyweight-only options
    if not filtered:
        filtered = [ex for ex in exercises if ex["equipment"] == []]

    return filtered


def trim_for_time(exercises: list[dict], minutes: int) -> list[dict]:
    if minutes < 20:
        return exercises[:3]
    if minutes <= 45:
        return exercises[:4]
    return exercises[:6]


def build_plan(goal: str, body_part: str, equipment: list[str], minutes: int) -> list[dict]:
    goal = goal if goal in {"strength", "fat_loss", "endurance"} else "strength"
    body_part = body_part if body_part in EXERCISES else "full_body"
    minutes = max(1, minutes)

    base = EXERCISES[body_part]
    base = filter_exercises_for_equipment(base, equipment)
    base = trim_for_time(base, minutes)

    finishers = filter_exercises_for_equipment(GOAL_FINISHERS.get(goal, []), equipment)
    if finishers:
        base += finishers[:1]

    return base


def checked(value: str, selected: list[str]) -> str:
    return "checked" if value in selected else ""


def selected_attr(value: str, current: str) -> str:
    return "selected" if value == current else ""


def render_plan_cards(plan: list[dict]) -> str:
    cards = []
    for ex in plan:
        video = f"""
        <iframe
          width="100%"
          height="220"
          src="https://www.youtube.com/embed/{ex['video_id']}"
          title="{ex['name']} demo"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          loading="lazy"></iframe>
        """ if ex.get("video_id") else "<p>No demo available</p>"

        cards.append(f"""
        <div class="exercise-card">
          <h3>{ex['name']}</h3>
          <p><strong>Sets:</strong> {ex['sets']} &nbsp; | &nbsp; <strong>Reps/Time:</strong> {ex['reps']}</p>
          {video}
        </div>
        """)
    return "".join(cards)


def render_page(plan=None, goal="strength", body_part="full_body", minutes=30, equipment=None):
    equipment = equipment or []
    plan_html = ""
    if plan:
        plan_html = f"""
        <div class="card" style="margin-top:1rem;">
          <h2>Your Workout Plan</h2>
          <p>Only exercises that match your selected equipment are shown.</p>
          <div class="exercise-grid">
            {render_plan_cards(plan)}
          </div>
        </div>
        """

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Free Workout Decider</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .card {{ background:#fff; border-radius:12px; padding:1rem; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
    .equip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:.4rem; border:1px solid #e2e8f0; border-radius:10px; padding:.75rem; }}
    input, select, button {{ padding:.55rem; margin-top:.25rem; }}
    button {{ background:#2563eb; color:white; border:none; border-radius:8px; cursor:pointer; }}
    .exercise-grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); }}
    .exercise-card {{ border:1px solid #e5e7eb; border-radius:10px; padding:.75rem; background:#fff; }}
    h3 {{ margin-bottom:.4rem; }}
  </style>
</head>
<body>
  <h1>Free Workout Decider</h1>
  <p>Pick your goal, body part, and equipment. We’ll only show compatible exercises with demos.</p>

  <form method="post" action="/decide" class="card">
    <p>
      <label><strong>Primary Goal</strong></label><br/>
      <select name="goal" required>
        <option value="strength" {selected_attr("strength", goal)}>Build Strength</option>
        <option value="fat_loss" {selected_attr("fat_loss", goal)}>Fat Loss</option>
        <option value="endurance" {selected_attr("endurance", goal)}>Endurance</option>
      </select>
    </p>

    <p>
      <label><strong>Body Part Focus</strong></label><br/>
      <select name="body_part" required>
        <option value="full_body" {selected_attr("full_body", body_part)}>Full Body</option>
        <option value="upper_body" {selected_attr("upper_body", body_part)}>Upper Body</option>
        <option value="lower_body" {selected_attr("lower_body", body_part)}>Lower Body</option>
        <option value="core" {selected_attr("core", body_part)}>Core</option>
      </select>
    </p>

    <p><strong>Equipment Available (select all that apply)</strong></p>
    <div class="equip">
      <label><input type="checkbox" name="equipment" value="none" {checked("none", equipment)}> None</label>
      <label><input type="checkbox" name="equipment" value="dumbbells" {checked("dumbbells", equipment)}> Dumbbells</label>
      <label><input type="checkbox" name="equipment" value="kettlebell" {checked("kettlebell", equipment)}> Kettlebell</label>
      <label><input type="checkbox" name="equipment" value="resistance_bands" {checked("resistance_bands", equipment)}> Resistance Bands</label>
      <label><input type="checkbox" name="equipment" value="pullup_bar" {checked("pullup_bar", equipment)}> Pull-up Bar</label>
      <label><input type="checkbox" name="equipment" value="jump_rope" {checked("jump_rope", equipment)}> Jump Rope</label>
      <label><input type="checkbox" name="equipment" value="bike" {checked("bike", equipment)}> Exercise Bike</label>
      <label><input type="checkbox" name="equipment" value="rower" {checked("rower", equipment)}> Rower</label>
      <label><input type="checkbox" name="equipment" value="treadmill" {checked("treadmill", equipment)}> Treadmill</label>
      <label><input type="checkbox" name="equipment" value="barbell" {checked("barbell", equipment)}> Barbell</label>
      <label><input type="checkbox" name="equipment" value="squat_rack" {checked("squat_rack", equipment)}> Squat Rack</label>
      <label><input type="checkbox" name="equipment" value="bench" {checked("bench", equipment)}> Bench</label>
      <label><input type="checkbox" name="equipment" value="cable_machine" {checked("cable_machine", equipment)}> Cable Machine</label>
    </div>

    <p>
      <label><strong>Minutes Available</strong></label><br/>
      <input type="number" name="minutes" min="10" max="120" value="{minutes}" required />
    </p>

    <button type="submit">Build Workout Plan</button>
  </form>

  {plan_html}
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return render_page()


@app.post("/decide", response_class=HTMLResponse)
async def decide(
    goal: str = Form(...),
    body_part: str = Form(...),
    equipment: list[str] = Form(default=[]),
    minutes: int = Form(...)
):
    plan = build_plan(goal, body_part, equipment, minutes)
    return render_page(plan=plan, goal=goal, body_part=body_part, minutes=minutes, equipment=equipment)
