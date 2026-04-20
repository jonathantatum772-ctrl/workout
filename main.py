from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

# ---------------------------------
# Exercise Library (estimated minutes per set included)
# ---------------------------------
EXERCISES = {
    "upper_body": [
        {"name": "Push-ups", "equipment": [], "sets": 4, "reps": "10-15", "mins_per_set": 2, "video_id": "IODxDxX7oi4"},
        {"name": "Pike Push-ups", "equipment": [], "sets": 3, "reps": "8-12", "mins_per_set": 2, "video_id": "qHQ_E-f5278"},
        {"name": "Dumbbell Bench Press", "equipment": ["dumbbells"], "sets": 4, "reps": "8-12", "mins_per_set": 3, "video_id": "VmB1G1K7v94"},
        {"name": "One-Arm DB Row", "equipment": ["dumbbells"], "sets": 4, "reps": "8-12 each", "mins_per_set": 3, "video_id": "pYcpY20QaE8"},
        {"name": "Barbell Bench Press", "equipment": ["barbell", "bench"], "sets": 4, "reps": "5-8", "mins_per_set": 3, "video_id": "rT7DgCr-3pg"},
        {"name": "Overhead Press", "equipment": ["barbell"], "sets": 3, "reps": "6-10", "mins_per_set": 3, "video_id": "2yjwXTZQDDI"},
    ],
    "lower_body": [
        {"name": "Bodyweight Squat", "equipment": [], "sets": 4, "reps": "15-20", "mins_per_set": 2, "video_id": "aclHkVaku9U"},
        {"name": "Reverse Lunge", "equipment": [], "sets": 3, "reps": "10 each", "mins_per_set": 2, "video_id": "wrwwXE_x-pQ"},
        {"name": "Goblet Squat", "equipment": ["dumbbells|kettlebell"], "sets": 4, "reps": "8-12", "mins_per_set": 3, "video_id": "MeIiIdhvXT4"},
        {"name": "DB Romanian Deadlift", "equipment": ["dumbbells"], "sets": 4, "reps": "8-12", "mins_per_set": 3, "video_id": "0YONJjY6i6Q"},
        {"name": "Back Squat", "equipment": ["barbell", "squat_rack"], "sets": 5, "reps": "5", "mins_per_set": 3, "video_id": "ultWZbUMPL8"},
        {"name": "Deadlift", "equipment": ["barbell"], "sets": 4, "reps": "4-6", "mins_per_set": 3, "video_id": "op9kVnSso6Q"},
    ],
    "core": [
        {"name": "Plank", "equipment": [], "sets": 4, "reps": "30-60 sec", "mins_per_set": 2, "video_id": "ASdvN_XEl_c"},
        {"name": "Dead Bug", "equipment": [], "sets": 3, "reps": "10 each", "mins_per_set": 2, "video_id": "4XLEnwUr8S4"},
        {"name": "Russian Twist", "equipment": ["dumbbells|kettlebell"], "sets": 3, "reps": "20 total", "mins_per_set": 2, "video_id": "wkD8rjkodUI"},
        {"name": "Cable Crunch", "equipment": ["cable_machine"], "sets": 4, "reps": "12-15", "mins_per_set": 3, "video_id": "AV5PmZJIrrw"},
    ],
    "full_body": [
        {"name": "Push-ups", "equipment": [], "sets": 3, "reps": "10-15", "mins_per_set": 2, "video_id": "IODxDxX7oi4"},
        {"name": "Bodyweight Squat", "equipment": [], "sets": 3, "reps": "15-20", "mins_per_set": 2, "video_id": "aclHkVaku9U"},
        {"name": "Goblet Squat", "equipment": ["dumbbells|kettlebell"], "sets": 4, "reps": "8-12", "mins_per_set": 3, "video_id": "MeIiIdhvXT4"},
        {"name": "Dumbbell Row", "equipment": ["dumbbells"], "sets": 4, "reps": "8-12", "mins_per_set": 3, "video_id": "pYcpY20QaE8"},
        {"name": "Back Squat", "equipment": ["barbell", "squat_rack"], "sets": 4, "reps": "5-8", "mins_per_set": 3, "video_id": "ultWZbUMPL8"},
        {"name": "Bench Press", "equipment": ["barbell", "bench"], "sets": 4, "reps": "5-8", "mins_per_set": 3, "video_id": "rT7DgCr-3pg"},
    ],
}

FULL_GYM = {"barbell", "squat_rack", "cable_machine", "bench"}
BASIC = {
    "dumbbells", "kettlebell", "resistance_bands", "pullup_bar",
    "bike", "rower", "treadmill", "jump_rope"
}


def has_required_equipment(required_rules: list[str], selected: set[str]) -> bool:
    if not required_rules:
        return True
    for rule in required_rules:
        if "|" in rule:
            options = set(rule.split("|"))
            if not (options & selected):
                return False
        elif rule not in selected:
            return False
    return True


def filtered_options(body_part: str, equipment_items: list[str]) -> list[dict]:
    body_part = body_part if body_part in EXERCISES else "full_body"
    selected = {x.strip().lower() for x in equipment_items if x.strip() and x.lower() != "none"}
    options = [e for e in EXERCISES[body_part] if has_required_equipment(e["equipment"], selected)]
    if not options:
        options = [e for e in EXERCISES[body_part] if not e["equipment"]]
    return options


def checked(value: str, selected: list[str]) -> str:
    return "checked" if value in selected else ""


def selected_attr(value: str, current: str) -> str:
    return "selected" if value == current else ""


def render_exercise_cards(options: list[dict], target_minutes: int) -> str:
    cards = []
    for i, ex in enumerate(options):
        est_total = ex["sets"] * ex["mins_per_set"]
        set_boxes = "".join(
            f'<label><input type="checkbox" class="set-box" data-ex="{i}"> Set {s}</label>'
            for s in range(1, ex["sets"] + 1)
        )
        cards.append(f"""
        <div class="exercise-card">
          <div class="row">
            <label>
              <input type="checkbox" class="exercise-pick" data-mins="{est_total}" data-ex="{i}" />
              <strong>{ex["name"]}</strong>
            </label>
            <span class="chip">~{est_total} min</span>
          </div>
          <p>Sets: {ex["sets"]} | Reps/Time: {ex["reps"]}</p>

          <iframe width="100%" height="220"
            src="https://www.youtube.com/embed/{ex["video_id"]}"
            title="{ex["name"]} demo"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen loading="lazy"></iframe>

          <div class="set-track">
            <p><strong>Track Sets</strong></p>
            {set_boxes}
          </div>

          <div class="rest-timer">
            <p><strong>Rest Timer</strong> <span id="timer-{i}" class="timer">00:00</span></p>
            <button type="button" onclick="startTimer({i}, 30)">30s</button>
            <button type="button" onclick="startTimer({i}, 60)">60s</button>
            <button type="button" onclick="startTimer({i}, 90)">90s</button>
            <button type="button" onclick="stopTimer({i})">Stop</button>
          </div>
        </div>
        """)
    return f"""
    <div class="card" style="margin-top:1rem;">
      <h2>Pick Your Exercises</h2>
      <p>Target time: <strong>{target_minutes} min</strong></p>
      <p id="time-status"><strong>Selected time:</strong> 0 min</p>
      <div class="exercise-grid">
        {''.join(cards)}
      </div>
    </div>
    """


def render_page(
    options=None,
    goal="strength",
    body_part="full_body",
    minutes=30,
    equipment=None
):
    equipment = equipment or []
    options_html = render_exercise_cards(options, minutes) if options else ""

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Free Workout Decider</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .card {{ background:#fff; border-radius:12px; padding:1rem; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
    .equip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:.4rem; border:1px solid #e2e8f0; border-radius:10px; padding:.75rem; }}
    input, select, button {{ padding:.55rem; margin-top:.25rem; }}
    button {{ background:#2563eb; color:white; border:none; border-radius:8px; cursor:pointer; }}
    .exercise-grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); }}
    .exercise-card {{ border:1px solid #e5e7eb; border-radius:10px; padding:.75rem; background:#fff; }}
    .row {{ display:flex; justify-content:space-between; align-items:center; gap:0.5rem; }}
    .chip {{ background:#eef2ff; color:#3730a3; border-radius:999px; padding:0.2rem 0.6rem; font-size:0.8rem; }}
    .set-track label {{ display:inline-block; margin-right:.5rem; margin-bottom:.25rem; }}
    .timer {{ font-family:monospace; font-weight:700; margin-left:.3rem; }}
    .ok {{ color: #166534; }}
    .warn {{ color: #991b1b; }}
  </style>
</head>
<body>
  <h1>Free Workout Decider</h1>
  <p>Select goal/body part/equipment, then pick exercises until you hit your target time.</p>

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
      <label><input type="checkbox" name="equipment" value="bike" {checked("bike", equipment)}> Bike</label>
      <label><input type="checkbox" name="equipment" value="rower" {checked("rower", equipment)}> Rower</label>
      <label><input type="checkbox" name="equipment" value="treadmill" {checked("treadmill", equipment)}> Treadmill</label>
      <label><input type="checkbox" name="equipment" value="barbell" {checked("barbell", equipment)}> Barbell</label>
      <label><input type="checkbox" name="equipment" value="squat_rack" {checked("squat_rack", equipment)}> Squat Rack</label>
      <label><input type="checkbox" name="equipment" value="bench" {checked("bench", equipment)}> Bench</label>
      <label><input type="checkbox" name="equipment" value="cable_machine" {checked("cable_machine", equipment)}> Cable Machine</label>
    </div>

    <p>
      <label><strong>Target Workout Time (minutes)</strong></label><br/>
      <input type="number" name="minutes" min="10" max="120" value="{minutes}" required />
    </p>

    <button type="submit">Show Matching Exercises</button>
  </form>

  {options_html}

  <script>
    // ----- time matching logic -----
    const target = {minutes};
    const picks = document.querySelectorAll('.exercise-pick');
    const status = document.getElementById('time-status');

    function updateSelectedTime() {{
      if (!status) return;
      let total = 0;
      picks.forEach(p => {{
        if (p.checked) total += Number(p.dataset.mins || 0);
      }});
      if (total >= target) {{
        status.innerHTML = `<strong>Selected time:</strong> ${total} min ✅ target met`;
        status.className = 'ok';
      }} else {{
        status.innerHTML = `<strong>Selected time:</strong> ${total} min (need ${target - total} more)`;
        status.className = 'warn';
      }}
    }}

    picks.forEach(p => p.addEventListener('change', updateSelectedTime));
    updateSelectedTime();

    // ----- set tracking persistence -----
    const setBoxes = document.querySelectorAll('.set-box');
    setBoxes.forEach((box, idx) => {{
      const key = 'setbox-' + idx;
      box.checked = localStorage.getItem(key) === '1';
      box.addEventListener('change', () => {{
        localStorage.setItem(key, box.checked ? '1' : '0');
      }});
    }});

    // ----- rest timers -----
    const timers = {{}};

    function fmt(sec) {{
      const m = String(Math.floor(sec / 60)).padStart(2, '0');
      const s = String(sec % 60).padStart(2, '0');
      return `${{m}}:${{s}}`;
    }}

    window.startTimer = function(exId, duration) {{
      stopTimer(exId);
      let left = duration;
      const el = document.getElementById(`timer-${{exId}}`);
      if (!el) return;
      el.textContent = fmt(left);

      timers[exId] = setInterval(() => {{
        left -= 1;
        el.textContent = fmt(Math.max(left, 0));
        if (left <= 0) {{
          clearInterval(timers[exId]);
          el.textContent = "DONE ✅";
          try {{ new Audio("https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg").play(); }} catch (e) {{}}
        }}
      }}, 1000);
    }}

    window.stopTimer = function(exId) {{
      if (timers[exId]) {{
        clearInterval(timers[exId]);
        delete timers[exId];
      }}
      const el = document.getElementById(`timer-${{exId}}`);
      if (el) el.textContent = "00:00";
    }}
  </script>
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
    options = filtered_options(body_part, equipment)
    return render_page(options=options, goal=goal, body_part=body_part, minutes=minutes, equipment=equipment)
