from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

FULL_GYM = {"barbell", "squat_rack", "cable_machine"}
BASIC = {
    "dumbbells", "kettlebell", "resistance_bands", "pullup_bar",
    "bench", "bike", "rower", "treadmill", "jump_rope"
}

# exercise libraries by body part + equipment level
WORKOUT_LIBRARY = {
    "upper_body": {
        "none": [
            ("Push-ups", "4", "10-15"),
            ("Pike Push-ups", "3", "8-12"),
            ("Chair Dips", "3", "10-15"),
            ("Plank Shoulder Taps", "3", "20 taps"),
        ],
        "basic": [
            ("Dumbbell Bench Press", "4", "8-12"),
            ("One-Arm Dumbbell Row", "4", "8-12 each"),
            ("Dumbbell Shoulder Press", "3", "8-12"),
            ("Biceps Curl", "3", "10-15"),
            ("Triceps Overhead Extension", "3", "10-15"),
        ],
        "full": [
            ("Barbell Bench Press", "4", "5-8"),
            ("Lat Pulldown", "4", "8-12"),
            ("Seated Cable Row", "3", "8-12"),
            ("Overhead Press", "3", "6-10"),
            ("Cable Triceps Pushdown", "3", "10-15"),
        ],
    },
    "lower_body": {
        "none": [
            ("Bodyweight Squat", "4", "15-20"),
            ("Reverse Lunge", "3", "10-12 each"),
            ("Glute Bridge", "4", "12-20"),
            ("Wall Sit", "3", "30-60 sec"),
        ],
        "basic": [
            ("Goblet Squat", "4", "8-12"),
            ("Romanian Deadlift (DB)", "4", "8-12"),
            ("Step-ups", "3", "10 each"),
            ("Kettlebell Swing", "3", "15-20"),
        ],
        "full": [
            ("Back Squat", "5", "5"),
            ("Deadlift", "4", "4-6"),
            ("Leg Press", "3", "10-12"),
            ("Hamstring Curl", "3", "10-15"),
            ("Standing Calf Raise", "3", "12-20"),
        ],
    },
    "core": {
        "none": [
            ("Plank", "4", "30-60 sec"),
            ("Dead Bug", "3", "10 each"),
            ("Bicycle Crunch", "3", "20 total"),
            ("Side Plank", "3", "20-40 sec each"),
        ],
        "basic": [
            ("Weighted Sit-up", "4", "10-15"),
            ("Russian Twist", "3", "20 total"),
            ("Dumbbell Side Bend", "3", "12 each"),
            ("Mountain Climbers", "3", "30-45 sec"),
        ],
        "full": [
            ("Cable Crunch", "4", "12-15"),
            ("Hanging Knee Raise", "4", "8-12"),
            ("Ab Wheel Rollout", "3", "8-12"),
            ("Pallof Press", "3", "10 each"),
        ],
    },
    "full_body": {
        "none": [
            ("Push-ups", "3", "10-15"),
            ("Bodyweight Squat", "3", "15-20"),
            ("Reverse Lunge", "3", "10 each"),
            ("Plank", "3", "30-60 sec"),
        ],
        "basic": [
            ("Goblet Squat", "4", "8-12"),
            ("Dumbbell Row", "4", "8-12"),
            ("Dumbbell Press", "3", "8-12"),
            ("Kettlebell Swing", "3", "15"),
            ("Plank", "3", "45 sec"),
        ],
        "full": [
            ("Back Squat", "4", "5-8"),
            ("Bench Press", "4", "5-8"),
            ("Barbell Row", "4", "6-10"),
            ("Romanian Deadlift", "3", "8-10"),
            ("Cable Core Rotation", "3", "12 each"),
        ],
    },
}

CARDIO_FINISHERS = {
    "fat_loss": [
        ("Jump Rope / Fast Feet", "5 rounds", "40s on / 20s off"),
        ("Burpees", "5 rounds", "8-12 reps"),
    ],
    "endurance": [
        ("Zone 2 Cardio (bike/treadmill/run)", "1", "20-40 min steady"),
        ("Optional Tempo Intervals", "4", "2 min hard / 2 min easy"),
    ],
}


def equipment_level(items: list[str]) -> str:
    normalized = {x.strip().lower() for x in items if x.strip()}
    if not normalized or normalized == {"none"}:
        return "none"
    if normalized & FULL_GYM:
        return "full"
    if normalized & BASIC:
        return "basic"
    return "none"


def trim_for_time(exercises, minutes: int):
    # quick version keeps fewer exercises
    if minutes < 20:
        return exercises[:3]
    if minutes <= 45:
        return exercises[:4]
    return exercises  # full list


def build_plan(goal: str, body_part: str, equipment_items: list[str], minutes: int):
    goal = goal if goal in {"strength", "fat_loss", "endurance"} else "strength"
    body_part = body_part if body_part in WORKOUT_LIBRARY else "full_body"
    level = equipment_level(equipment_items)

    base = WORKOUT_LIBRARY[body_part][level]
    base = trim_for_time(base, minutes)

    # add goal-specific finishers
    if goal in CARDIO_FINISHERS:
        base = base + CARDIO_FINISHERS[goal][:1]

    return base, level


def checked(value: str, selected: list[str]) -> str:
    return "checked" if value in selected else ""


def selected_attr(value: str, current: str) -> str:
    return "selected" if value == current else ""


def render_plan_rows(plan):
    return "".join(
        f"<tr><td>{ex}</td><td>{sets}</td><td>{reps}</td></tr>"
        for ex, sets, reps in plan
    )


def render_page(
    plan=None,
    selected_equipment=None,
    selected_body_part="full_body",
    selected_goal="strength",
    minutes=30,
    level_label="none",
):
    selected_equipment = selected_equipment or []
    plan_html = ""
    if plan:
        plan_html = f"""
        <div class="card" style="margin-top:1rem;">
          <h2>Your Workout Plan</h2>
          <p><strong>Equipment tier detected:</strong> {level_label}</p>
          <table>
            <thead><tr><th>Exercise</th><th>Sets</th><th>Reps / Time</th></tr></thead>
            <tbody>{render_plan_rows(plan)}</tbody>
          </table>
        </div>
        """

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Free Workout Decider</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .card {{ background:#fff; border-radius:12px; padding:1rem; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
    .equip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:.4rem; border:1px solid #e2e8f0; border-radius:10px; padding:.75rem; }}
    input, select, button {{ padding:.55rem; margin-top:.25rem; }}
    button {{ background:#2563eb; color:white; border:none; border-radius:8px; cursor:pointer; }}
    table {{ width:100%; border-collapse:collapse; margin-top:.75rem; }}
    th, td {{ text-align:left; padding:.55rem; border-bottom:1px solid #e5e7eb; }}
  </style>
</head>
<body>
  <h1>Free Workout Decider</h1>
  <p>A free, logic-based workout recommendation tool.</p>

  <form method="post" action="/decide" class="card">
    <p>
      <label><strong>Primary Goal</strong></label><br/>
      <select name="goal" required>
        <option value="strength" {selected_attr("strength", selected_goal)}>Build Strength</option>
        <option value="fat_loss" {selected_attr("fat_loss", selected_goal)}>Fat Loss</option>
        <option value="endurance" {selected_attr("endurance", selected_goal)}>Endurance</option>
      </select>
    </p>

    <p>
      <label><strong>Body Part Focus</strong></label><br/>
      <select name="body_part" required>
        <option value="full_body" {selected_attr("full_body", selected_body_part)}>Full Body</option>
        <option value="upper_body" {selected_attr("upper_body", selected_body_part)}>Upper Body</option>
        <option value="lower_body" {selected_attr("lower_body", selected_body_part)}>Lower Body</option>
        <option value="core" {selected_attr("core", selected_body_part)}>Core</option>
      </select>
    </p>

    <p><strong>Equipment Available (select all that apply)</strong></p>
    <div class="equip">
      <label><input type="checkbox" name="equipment" value="none" {checked("none", selected_equipment)}> None</label>
      <label><input type="checkbox" name="equipment" value="dumbbells" {checked("dumbbells", selected_equipment)}> Dumbbells</label>
      <label><input type="checkbox" name="equipment" value="kettlebell" {checked("kettlebell", selected_equipment)}> Kettlebell</label>
      <label><input type="checkbox" name="equipment" value="resistance_bands" {checked("resistance_bands", selected_equipment)}> Resistance Bands</label>
      <label><input type="checkbox" name="equipment" value="pullup_bar" {checked("pullup_bar", selected_equipment)}> Pull-up Bar</label>
      <label><input type="checkbox" name="equipment" value="jump_rope" {checked("jump_rope", selected_equipment)}> Jump Rope</label>
      <label><input type="checkbox" name="equipment" value="bike" {checked("bike", selected_equipment)}> Exercise Bike</label>
      <label><input type="checkbox" name="equipment" value="rower" {checked("rower", selected_equipment)}> Rower</label>
      <label><input type="checkbox" name="equipment" value="treadmill" {checked("treadmill", selected_equipment)}> Treadmill</label>
      <label><input type="checkbox" name="equipment" value="barbell" {checked("barbell", selected_equipment)}> Barbell</label>
      <label><input type="checkbox" name="equipment" value="squat_rack" {checked("squat_rack", selected_equipment)}> Squat Rack</label>
      <label><input type="checkbox" name="equipment" value="cable_machine" {checked("cable_machine", selected_equipment)}> Cable Machine</label>
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
    plan, level = build_plan(goal, body_part, equipment, minutes)
    return render_page(
        plan=plan,
        selected_equipment=equipment,
        selected_body_part=body_part,
        selected_goal=goal,
        minutes=minutes,
        level_label=level,
    )
