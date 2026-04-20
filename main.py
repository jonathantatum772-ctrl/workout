from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

EXERCISES = {
    "full_body": [
        {"name": "Push-ups", "sets": 3, "reps": "10-15", "mins": 6},
        {"name": "Bodyweight Squat", "sets": 3, "reps": "15-20", "mins": 6},
        {"name": "Dumbbell Row", "sets": 4, "reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"name": "Goblet Squat", "sets": 4, "reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"]},
    ],
    "upper_body": [
        {"name": "Push-ups", "sets": 4, "reps": "10-15", "mins": 8},
        {"name": "Dumbbell Bench Press", "sets": 4, "reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"name": "One-Arm Dumbbell Row", "sets": 4, "reps": "8-12 each", "mins": 12, "needs": ["dumbbells"]},
    ],
    "lower_body": [
        {"name": "Bodyweight Squat", "sets": 4, "reps": "15-20", "mins": 8},
        {"name": "Reverse Lunge", "sets": 3, "reps": "10 each", "mins": 8},
        {"name": "Goblet Squat", "sets": 4, "reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"]},
    ],
    "core": [
        {"name": "Plank", "sets": 4, "reps": "30-60 sec", "mins": 8},
        {"name": "Dead Bug", "sets": 3, "reps": "10 each", "mins": 6},
        {"name": "Russian Twist", "sets": 3, "reps": "20 total", "mins": 6},
    ],
}


def has_equipment(exercise, selected):
    needs = exercise.get("needs", [])
    if not needs:
        return True
    selected_set = set(x.strip().lower() for x in selected if x.strip() and x.lower() != "none")
    for rule in needs:
        if "|" in rule:
            options = set(rule.split("|"))
            if not (options & selected_set):
                return False
        else:
            if rule not in selected_set:
                return False
    return True


def get_options(body_part, equipment):
    body = body_part if body_part in EXERCISES else "full_body"
    options = [e for e in EXERCISES[body] if has_equipment(e, equipment)]
    if not options:
        options = [e for e in EXERCISES[body] if "needs" not in e]
    return options


def selected_attr(value, current):
    return "selected" if value == current else ""


def checked(value, selected):
    return "checked" if value in selected else ""


def build_exercise_html(options):
    blocks = []
    for i, ex in enumerate(options):
        set_boxes = []
        for s in range(1, ex["sets"] + 1):
            set_boxes.append(
                f'<label><input type="checkbox" class="set-box"> Set {s}</label>'
            )
        set_boxes_html = " ".join(set_boxes)

        blocks.append(
            f"""
            <div class="exercise-card">
              <div class="row">
                <label><input type="checkbox" class="exercise-pick" data-mins="{ex['mins']}"> <strong>{ex['name']}</strong></label>
                <span class="chip">~{ex['mins']} min</span>
              </div>
              <p>Sets: {ex['sets']} | Reps/Time: {ex['reps']}</p>
              <div>{set_boxes_html}</div>
              <div class="timer-row">
                <span id="timer-{i}" class="timer">00:00</span>
                <button type="button" onclick="startTimer({i},30)">30s</button>
                <button type="button" onclick="startTimer({i},60)">60s</button>
                <button type="button" onclick="startTimer({i},90)">90s</button>
                <button type="button" onclick="stopTimer({i})">Stop</button>
              </div>
            </div>
            """
        )
    return "\n".join(blocks)


def render_page(options=None, body_part="full_body", minutes=30, equipment=None):
    equipment = equipment or []
    options_html = ""
    if options:
        options_html = f"""
        <div class="card" style="margin-top:1rem;">
          <h2>Pick Exercises Until You Hit Your Time</h2>
          <p><strong>Target:</strong> {minutes} min</p>
          <p id="time-status"><strong>Selected time:</strong> 0 min</p>
          <div class="grid">
            {build_exercise_html(options)}
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
    body {{ font-family: Arial, sans-serif; max-width: 980px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .card {{ background:#fff; border-radius:12px; padding:1rem; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
    .equip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:.4rem; border:1px solid #e2e8f0; border-radius:10px; padding:.75rem; }}
    .grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); }}
    .exercise-card {{ border:1px solid #e5e7eb; border-radius:10px; padding:.75rem; background:#fff; }}
    .row {{ display:flex; justify-content:space-between; align-items:center; gap:0.5rem; }}
    .chip {{ background:#eef2ff; border-radius:999px; padding:0.2rem 0.6rem; font-size:0.8rem; }}
    .timer {{ font-family: monospace; font-weight: bold; margin-right: .5rem; }}
    .timer-row button {{ margin-right:.35rem; }}
    input, select, button {{ padding:.5rem; }}
  </style>
</head>
<body>
  <h1>Free Workout Decider</h1>

  <form method="post" action="/decide" class="card">
    <p>
      <label><strong>Body Part</strong></label><br/>
      <select name="body_part" required>
        <option value="full_body" {selected_attr("full_body", body_part)}>Full Body</option>
        <option value="upper_body" {selected_attr("upper_body", body_part)}>Upper Body</option>
        <option value="lower_body" {selected_attr("lower_body", body_part)}>Lower Body</option>
        <option value="core" {selected_attr("core", body_part)}>Core</option>
      </select>
    </p>

    <p><strong>Equipment</strong></p>
    <div class="equip">
      <label><input type="checkbox" name="equipment" value="none" {checked("none", equipment)}> None</label>
      <label><input type="checkbox" name="equipment" value="dumbbells" {checked("dumbbells", equipment)}> Dumbbells</label>
      <label><input type="checkbox" name="equipment" value="kettlebell" {checked("kettlebell", equipment)}> Kettlebell</label>
      <label><input type="checkbox" name="equipment" value="barbell" {checked("barbell", equipment)}> Barbell</label>
      <label><input type="checkbox" name="equipment" value="bench" {checked("bench", equipment)}> Bench</label>
      <label><input type="checkbox" name="equipment" value="squat_rack" {checked("squat_rack", equipment)}> Squat Rack</label>
    </div>

    <p>
      <label><strong>Target Minutes</strong></label><br/>
      <input type="number" name="minutes" min="10" max="120" value="{minutes}" required />
    </p>

    <button type="submit">Show Exercise Options</button>
  </form>

  {options_html}

  <script>
    (function() {{
      var target = {minutes};
      var picks = document.querySelectorAll('.exercise-pick');
      var status = document.getElementById('time-status');

      function updateTime() {{
        if (!status) return;
        var total = 0;
        picks.forEach(function(p) {{
          if (p.checked) total += Number(p.dataset.mins || 0);
        }});
        if (total >= target) {{
          status.innerHTML = "<strong>Selected time:</strong> " + total + " min ✅ target met";
        }} else {{
          status.innerHTML = "<strong>Selected time:</strong> " + total + " min (need " + (target - total) + " more)";
        }}
      }}

      picks.forEach(function(p) {{
        p.addEventListener('change', updateTime);
      }});
      updateTime();

      var timers = {{}};

      function fmt(sec) {{
        var m = String(Math.floor(sec / 60)).padStart(2, '0');
        var s = String(sec % 60).padStart(2, '0');
        return m + ":" + s;
      }}

      window.startTimer = function(exId, duration) {{
        window.stopTimer(exId);
        var left = duration;
        var el = document.getElementById("timer-" + exId);
        if (!el) return;
        el.textContent = fmt(left);

        timers[exId] = setInterval(function() {{
          left -= 1;
          el.textContent = fmt(Math.max(left, 0));
          if (left <= 0) {{
            clearInterval(timers[exId]);
            el.textContent = "DONE ✅";
          }}
        }}, 1000);
      }};

      window.stopTimer = function(exId) {{
        if (timers[exId]) {{
          clearInterval(timers[exId]);
          delete timers[exId];
        }}
        var el = document.getElementById("timer-" + exId);
        if (el) el.textContent = "00:00";
      }};
    }})();
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return render_page()


@app.post("/decide", response_class=HTMLResponse)
async def decide(
    body_part: str = Form(...),
    equipment: list[str] = Form(default=[]),
    minutes: int = Form(...)
):
    options = get_options(body_part, equipment)
    return render_page(options=options, body_part=body_part, minutes=minutes, equipment=equipment)
