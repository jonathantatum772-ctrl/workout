from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

WORKOUT_RULES = {
    "strength": {
        "none": "Bodyweight Circuit (Push-ups, Squats, Plank, Glute Bridges)",
        "basic": "Dumbbell Full-Body Strength (Goblet Squat, Rows, Press)",
        "full": "Barbell Strength Session (Squat, Press, Deadlift)",
    },
    "fat_loss": {
        "none": "No-Equipment HIIT (Jumping Jacks, Mountain Climbers, Burpees)",
        "basic": "Kettlebell + Bodyweight MetCon",
        "full": "Treadmill Intervals + Strength Circuit",
    },
    "endurance": {
        "none": "Outdoor Run/Walk Intervals",
        "basic": "Row/Bike Intervals + Core",
        "full": "Zone 2 Cardio + Accessory Work",
    },
}

BODY_PART_FOCUS = {
    "full_body": "Focus: Full Body",
    "upper_body": "Focus: Upper Body (chest, back, shoulders, arms)",
    "lower_body": "Focus: Lower Body (quads, glutes, hamstrings, calves)",
    "core": "Focus: Core (abs, obliques, lower back)",
    "push": "Focus: Push muscles (chest, shoulders, triceps)",
    "pull": "Focus: Pull muscles (back, biceps, rear delts)",
}

FULL_GYM = {"barbell", "squat_rack", "cable_machine"}
BASIC = {
    "dumbbells", "kettlebell", "resistance_bands", "pullup_bar",
    "bench", "bike", "rower", "treadmill", "jump_rope"
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


def decide_workout(goal: str, equipment_items: list[str], minutes: int, body_part: str) -> str:
    goal = goal if goal in WORKOUT_RULES else "strength"
    level = equipment_level(equipment_items)
    workout = WORKOUT_RULES[goal][level]
    minutes = max(1, minutes)
    focus = BODY_PART_FOCUS.get(body_part, BODY_PART_FOCUS["full_body"])

    if minutes < 20:
        duration = f"Quick {minutes}-Minute Version"
    elif minutes <= 45:
        duration = f"Standard {minutes}-Minute Session"
    else:
        duration = f"Extended {minutes}-Minute Session"

    extra = " + mobility cooldown" if minutes > 45 else ""
    return f"{duration}: {workout}{extra}. {focus}"


def checked(value: str, selected: list[str]) -> str:
    return "checked" if value in selected else ""


def selected_attr(value: str, current: str) -> str:
    return "selected" if value == current else ""


def render_page(
    recommendation: str | None = None,
    selected_equipment: list[str] | None = None,
    selected_body_part: str = "full_body",
) -> str:
    selected_equipment = selected_equipment or []

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Free Workout Decider</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 820px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .card {{ background:#fff; border-radius:12px; padding:1rem; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
    .equip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:.4rem; border:1px solid #e2e8f0; border-radius:10px; padding:.75rem; }}
    input, select, button {{ padding:.55rem; margin-top:.25rem; }}
    button {{ background:#2563eb; color:white; border:none; border-radius:8px; cursor:pointer; }}
  </style>
</head>
<body>
  <h1>Free Workout Decider</h1>
  <p>A free, logic-based workout recommendation tool.</p>

  <form method="post" action="/decide" class="card">
    <p>
      <label><strong>Primary Goal</strong></label><br/>
      <select name="goal" required>
        <option value="strength">Build Strength</option>
        <option value="fat_loss">Fat Loss</option>
        <option value="endurance">Endurance</option>
      </select>
    </p>

    <p>
      <label><strong>Body Part Focus</strong></label><br/>
      <select name="body_part" required>
        <option value="full_body" {selected_attr("full_body", selected_body_part)}>Full Body</option>
        <option value="upper_body" {selected_attr("upper_body", selected_body_part)}>Upper Body</option>
        <option value="lower_body" {selected_attr("lower_body", selected_body_part)}>Lower Body</option>
        <option value="core" {selected_attr("core", selected_body_part)}>Core</option>
        <option value="push" {selected_attr("push", selected_body_part)}>Push</option>
        <option value="pull" {selected_attr("pull", selected_body_part)}>Pull</option>
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
      <input type="number" name="minutes" min="10" max="120" value="30" required />
    </p>

    <button type="submit">Get Workout</button>
  </form>

  {f'<div class="card" style="margin-top:1rem;"><h2>Your Recommendation</h2><p>{recommendation}</p></div>' if recommendation else ''}
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
    recommendation = decide_workout(goal, equipment, minutes, body_part)
    return render_page(
        recommendation=recommendation,
        selected_equipment=equipment,
        selected_body_part=body_part,
    )
