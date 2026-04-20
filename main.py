from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

EXERCISES = {
    "full_body": [
        {"id": "pushups", "name": "Push-ups", "default_sets": 3, "default_reps": "10-15", "mins": 6, "image": "https://img.youtube.com/vi/IODxDxX7oi4/hqdefault.jpg"},
        {"id": "bw_squat", "name": "Bodyweight Squat", "default_sets": 3, "default_reps": "15-20", "mins": 6, "image": "https://img.youtube.com/vi/aclHkVaku9U/hqdefault.jpg"},
        {"id": "db_row", "name": "Dumbbell Row", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"], "image": "https://img.youtube.com/vi/pYcpY20QaE8/hqdefault.jpg"},
        {"id": "goblet_squat", "name": "Goblet Squat", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"], "image": "https://img.youtube.com/vi/MeIiIdhvXT4/hqdefault.jpg"},
    ],
    "upper_body": [
        {"id": "pushups", "name": "Push-ups", "default_sets": 4, "default_reps": "10-15", "mins": 8, "image": "https://img.youtube.com/vi/IODxDxX7oi4/hqdefault.jpg"},
        {"id": "db_bench", "name": "Dumbbell Bench Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"], "image": "https://img.youtube.com/vi/VmB1G1K7v94/hqdefault.jpg"},
        {"id": "db_row", "name": "One-Arm Dumbbell Row", "default_sets": 4, "default_reps": "8-12 each", "mins": 12, "needs": ["dumbbells"], "image": "https://img.youtube.com/vi/pYcpY20QaE8/hqdefault.jpg"},
    ],
    "lower_body": [
        {"id": "bw_squat", "name": "Bodyweight Squat", "default_sets": 4, "default_reps": "15-20", "mins": 8, "image": "https://img.youtube.com/vi/aclHkVaku9U/hqdefault.jpg"},
        {"id": "rev_lunge", "name": "Reverse Lunge", "default_sets": 3, "default_reps": "10 each", "mins": 8, "image": "https://img.youtube.com/vi/wrwwXE_x-pQ/hqdefault.jpg"},
        {"id": "goblet_squat", "name": "Goblet Squat", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"], "image": "https://img.youtube.com/vi/MeIiIdhvXT4/hqdefault.jpg"},
    ],
    "core": [
        {"id": "plank", "name": "Plank", "default_sets": 4, "default_reps": "30-60 sec", "mins": 8, "image": "https://img.youtube.com/vi/ASdvN_XEl_c/hqdefault.jpg"},
        {"id": "deadbug", "name": "Dead Bug", "default_sets": 3, "default_reps": "10 each", "mins": 6, "image": "https://img.youtube.com/vi/4XLEnwUr8S4/hqdefault.jpg"},
        {"id": "russian_twist", "name": "Russian Twist", "default_sets": 3, "default_reps": "20 total", "mins": 6, "image": "https://img.youtube.com/vi/wkD8rjkodUI/hqdefault.jpg"},
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
        elif rule not in selected_set:
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


def exercise_card(ex):
    return f"""
    <div class="exercise-card">
      <label>
        <input type="checkbox" name="selected_exercises" value="{ex['id']}" class="pick-box" data-mins="{ex['mins']}">
        <strong>{ex['name']}</strong>
      </label>
      <p>Estimated time: ~{ex['mins']} min</p>
      <img src="{ex['image']}" alt="{ex['name']} example" />
    </div>
    """


def render_options_page(options=None, body_part="full_body", minutes=30, equipment=None):
    equipment = equipment or []
    cards_html = "".join(exercise_card(ex) for ex in options) if options else ""

    # keep ids in hidden mapping for start page
    hidden_data = ""
    if options:
        for ex in options:
            hidden_data += f'<input type="hidden" name="meta_{ex["id"]}_name" value="{ex["name"]}">'
            hidden_data += f'<input type="hidden" name="meta_{ex["id"]}_sets" value="{ex["default_sets"]}">'
            hidden_data += f'<input type="hidden" name="meta_{ex["id"]}_reps" value="{ex["default_reps"]}">'

    options_block = ""
    if options:
        options_block = f"""
        <form method="post" action="/start" class="card" style="margin-top:1rem;">
          <h2>Select Exercises (Images Only)</h2>
          <p><strong>Target time:</strong> {minutes} min</p>
          <p id="pick-status"><strong>Selected time:</strong> 0 min</p>
          <div class="grid">{cards_html}</div>

          <input type="hidden" name="target_minutes" value="{minutes}">
          {hidden_data}

          <button type="submit" style="margin-top:1rem;">Start Workout</button>
        </form>
        """

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Workout Decider</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .card {{ background:#fff; border-radius:12px; padding:1rem; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
    .equip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:.4rem; border:1px solid #e2e8f0; border-radius:10px; padding:.75rem; }}
    .grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }}
    .exercise-card {{ border:1px solid #e5e7eb; border-radius:10px; padding:.75rem; background:#fff; }}
    .exercise-card img {{ width:100%; border-radius:8px; margin-top:.5rem; }}
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
      <label><input type="checkbox" name="equipment" value="cable_machine" {checked("cable_machine", equipment)}> Cable Machine</label>
    </div>

    <p>
      <label><strong>Custom Target Minutes</strong></label><br/>
      <input type="number" name="minutes" min="5" max="180" value="{minutes}" required />
    </p>

    <button type="submit">Show Matching Exercises</button>
  </form>

  {options_block}

  <script>
    (function() {{
      var picks = document.querySelectorAll('.pick-box');
      var status = document.getElementById('pick-status');
      var target = {minutes};

      function update() {{
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
      picks.forEach(function(p) {{ p.addEventListener('change', update); }});
      update();
    }})();
  </script>
</body>
</html>
"""


def workout_row(idx, ex_id, name, sets, reps):
    set_inputs = "".join(
        f'<label><input type="checkbox" class="set-check"> Set {i}</label>'
        for i in range(1, int(sets) + 1)
    )

    return f"""
    <div class="session-card">
      <h3>{name}</h3>
      <p><strong>Default:</strong> {sets} sets x {reps}</p>

      <div class="entry-row">
        <label>Sets done: <input type="number" min="0" value="{sets}" class="sets-done"></label>
        <label>Reps done each set: <input type="text" value="{reps}" class="reps-done"></label>
      </div>

      <div class="set-track">{set_inputs}</div>

      <div class="timer-row">
        <strong>Rest timer:</strong>
        <span id="rest-{idx}" class="timer">00:00</span>
        <button type="button" onclick="startRest({idx},30)">30s</button>
        <button type="button" onclick="startRest({idx},60)">60s</button>
        <button type="button" onclick="startRest({idx},90)">90s</button>
        <button type="button" onclick="stopRest({idx})">Stop</button>
      </div>
    </div>
    """


def render_session_page(selected_ids, form_data, target_minutes):
    if not selected_ids:
        return """
        <html><body style='font-family:Arial;padding:2rem;'>
        <h2>No exercises selected.</h2>
        <p><a href='/'>Go back and select at least one exercise.</a></p>
        </body></html>
        """

    rows = []
    for idx, ex_id in enumerate(selected_ids):
        name = form_data.get(f"meta_{ex_id}_name", ex_id)
        sets = form_data.get(f"meta_{ex_id}_sets", "3")
        reps = form_data.get(f"meta_{ex_id}_reps", "10")
        rows.append(workout_row(idx, ex_id, name, sets, reps))

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Workout Session</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .session-card {{ background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:1rem; margin-bottom:1rem; }}
    .entry-row {{ display:flex; gap:1rem; flex-wrap:wrap; margin:.5rem 0; }}
    .set-track label {{ display:inline-block; margin-right:.5rem; margin-bottom:.3rem; }}
    .timer {{ font-family:monospace; font-weight:700; margin:0 .5rem; }}
    button, input {{ padding:.45rem; }}
  </style>
</head>
<body>
  <h1>Workout Session</h1>
  <p><strong>Target time:</strong> {target_minutes} min</p>
  <p>Mark sets as you complete them. Start rest timer whenever you finish a set.</p>

  {"".join(rows)}

  <p><a href="/">← Back to planner</a></p>

  <script>
    (function() {{
      var timers = {{}};

      function fmt(sec) {{
        var m = String(Math.floor(sec / 60)).padStart(2, '0');
        var s = String(sec % 60).padStart(2, '0');
        return m + ":" + s;
      }}

      window.startRest = function(id, seconds) {{
        window.stopRest(id);
        var left = seconds;
        var el = document.getElementById("rest-" + id);
        if (!el) return;
        el.textContent = fmt(left);

        timers[id] = setInterval(function() {{
          left -= 1;
          el.textContent = fmt(Math.max(left, 0));
          if (left <= 0) {{
            clearInterval(timers[id]);
            el.textContent = "DONE ✅";
          }}
        }}, 1000);
      }};

      window.stopRest = function(id) {{
        if (timers[id]) {{
          clearInterval(timers[id]);
          delete timers[id];
        }}
        var el = document.getElementById("rest-" + id);
        if (el) el.textContent = "00:00";
      }};
    }})();
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return render_options_page()


@app.post("/decide", response_class=HTMLResponse)
async def decide(
    body_part: str = Form(...),
    equipment: list[str] = Form(default=[]),
    minutes: int = Form(...)
):
    options = get_options(body_part, equipment)
    return render_options_page(
        options=options,
        body_part=body_part,
        minutes=max(1, minutes),
        equipment=equipment
    )


@app.post("/start", response_class=HTMLResponse)
async def start_workout(
    selected_exercises: list[str] = Form(default=[]),
    target_minutes: int = Form(default=30),
    # grab raw form map to recover hidden exercise metadata
    meta_pushups_name: str = Form(default=""),
    meta_pushups_sets: str = Form(default=""),
    meta_pushups_reps: str = Form(default=""),
    meta_bw_squat_name: str = Form(default=""),
    meta_bw_squat_sets: str = Form(default=""),
    meta_bw_squat_reps: str = Form(default=""),
    meta_db_row_name: str = Form(default=""),
    meta_db_row_sets: str = Form(default=""),
    meta_db_row_reps: str = Form(default=""),
    meta_goblet_squat_name: str = Form(default=""),
    meta_goblet_squat_sets: str = Form(default=""),
    meta_goblet_squat_reps: str = Form(default=""),
    meta_db_bench_name: str = Form(default=""),
    meta_db_bench_sets: str = Form(default=""),
    meta_db_bench_reps: str = Form(default=""),
    meta_rev_lunge_name: str = Form(default=""),
    meta_rev_lunge_sets: str = Form(default=""),
    meta_rev_lunge_reps: str = Form(default=""),
    meta_plank_name: str = Form(default=""),
    meta_plank_sets: str = Form(default=""),
    meta_plank_reps: str = Form(default=""),
    meta_deadbug_name: str = Form(default=""),
    meta_deadbug_sets: str = Form(default=""),
    meta_deadbug_reps: str = Form(default=""),
    meta_russian_twist_name: str = Form(default=""),
    meta_russian_twist_sets: str = Form(default=""),
    meta_russian_twist_reps: str = Form(default=""),
):
    form_data = {
        "meta_pushups_name": meta_pushups_name, "meta_pushups_sets": meta_pushups_sets, "meta_pushups_reps": meta_pushups_reps,
        "meta_bw_squat_name": meta_bw_squat_name, "meta_bw_squat_sets": meta_bw_squat_sets, "meta_bw_squat_reps": meta_bw_squat_reps,
        "meta_db_row_name": meta_db_row_name, "meta_db_row_sets": meta_db_row_sets, "meta_db_row_reps": meta_db_row_reps,
        "meta_goblet_squat_name": meta_goblet_squat_name, "meta_goblet_squat_sets": meta_goblet_squat_sets, "meta_goblet_squat_reps": meta_goblet_squat_reps,
        "meta_db_bench_name": meta_db_bench_name, "meta_db_bench_sets": meta_db_bench_sets, "meta_db_bench_reps": meta_db_bench_reps,
        "meta_rev_lunge_name": meta_rev_lunge_name, "meta_rev_lunge_sets": meta_rev_lunge_sets, "meta_rev_lunge_reps": meta_rev_lunge_reps,
        "meta_plank_name": meta_plank_name, "meta_plank_sets": meta_plank_sets, "meta_plank_reps": meta_plank_reps,
        "meta_deadbug_name": meta_deadbug_name, "meta_deadbug_sets": meta_deadbug_sets, "meta_deadbug_reps": meta_deadbug_reps,
        "meta_russian_twist_name": meta_russian_twist_name, "meta_russian_twist_sets": meta_russian_twist_sets, "meta_russian_twist_reps": meta_russian_twist_reps,
    }
    return render_session_page(selected_exercises, form_data, max(1, target_minutes))
