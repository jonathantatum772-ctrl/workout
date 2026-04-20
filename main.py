from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

# ------------------------------------------------------------
# Large Exercise Library (no images/videos)
# ------------------------------------------------------------
EXERCISES = {
    "full_body": [
        {"id": "pushups", "name": "Push-ups", "default_sets": 3, "default_reps": "10-15", "mins": 6},
        {"id": "bw_squat", "name": "Bodyweight Squat", "default_sets": 3, "default_reps": "15-20", "mins": 6},
        {"id": "walking_lunge", "name": "Walking Lunge", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "mountain_climbers", "name": "Mountain Climbers", "default_sets": 3, "default_reps": "30-45 sec", "mins": 6},
        {"id": "burpees", "name": "Burpees", "default_sets": 3, "default_reps": "8-12", "mins": 8},
        {"id": "db_thruster", "name": "Dumbbell Thruster", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "db_row", "name": "Dumbbell Row", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "goblet_squat", "name": "Goblet Squat", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"]},
        {"id": "kb_swing", "name": "Kettlebell Swing", "default_sets": 4, "default_reps": "12-20", "mins": 10, "needs": ["kettlebell"]},
        {"id": "barbell_complex", "name": "Barbell Complex", "default_sets": 5, "default_reps": "6 each move", "mins": 15, "needs": ["barbell"]},
        {"id": "front_squat", "name": "Front Squat", "default_sets": 4, "default_reps": "5-8", "mins": 12, "needs": ["barbell", "squat_rack"]},
        {"id": "bench_press", "name": "Bench Press", "default_sets": 4, "default_reps": "5-8", "mins": 12, "needs": ["barbell", "bench"]},
    ],
    "upper_body": [
        {"id": "pushups", "name": "Push-ups", "default_sets": 4, "default_reps": "10-15", "mins": 8},
        {"id": "diamond_pushups", "name": "Diamond Push-ups", "default_sets": 3, "default_reps": "8-12", "mins": 7},
        {"id": "pike_pushups", "name": "Pike Push-ups", "default_sets": 3, "default_reps": "8-12", "mins": 7},
        {"id": "chair_dips", "name": "Chair Dips", "default_sets": 3, "default_reps": "10-15", "mins": 7},
        {"id": "band_row", "name": "Resistance Band Row", "default_sets": 4, "default_reps": "12-15", "mins": 9, "needs": ["resistance_bands"]},
        {"id": "band_press", "name": "Resistance Band Chest Press", "default_sets": 4, "default_reps": "10-15", "mins": 9, "needs": ["resistance_bands"]},
        {"id": "db_bench", "name": "Dumbbell Bench Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "db_incline_press", "name": "Dumbbell Incline Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells", "bench"]},
        {"id": "db_shoulder_press", "name": "Dumbbell Shoulder Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "db_lateral_raise", "name": "Dumbbell Lateral Raise", "default_sets": 3, "default_reps": "12-15", "mins": 8, "needs": ["dumbbells"]},
        {"id": "db_bicep_curl", "name": "Dumbbell Bicep Curl", "default_sets": 3, "default_reps": "10-15", "mins": 8, "needs": ["dumbbells"]},
        {"id": "db_tricep_ext", "name": "Dumbbell Tricep Extension", "default_sets": 3, "default_reps": "10-15", "mins": 8, "needs": ["dumbbells"]},
        {"id": "pullups", "name": "Pull-ups", "default_sets": 4, "default_reps": "AMRAP", "mins": 10, "needs": ["pullup_bar"]},
        {"id": "barbell_row", "name": "Barbell Row", "default_sets": 4, "default_reps": "6-10", "mins": 10, "needs": ["barbell"]},
        {"id": "overhead_press", "name": "Overhead Press", "default_sets": 4, "default_reps": "5-8", "mins": 10, "needs": ["barbell"]},
        {"id": "bench_press", "name": "Bench Press", "default_sets": 5, "default_reps": "5", "mins": 12, "needs": ["barbell", "bench"]},
        {"id": "cable_row", "name": "Cable Row", "default_sets": 4, "default_reps": "10-12", "mins": 10, "needs": ["cable_machine"]},
        {"id": "lat_pulldown", "name": "Lat Pulldown", "default_sets": 4, "default_reps": "10-12", "mins": 10, "needs": ["cable_machine"]},
    ],
    "lower_body": [
        {"id": "bw_squat", "name": "Bodyweight Squat", "default_sets": 4, "default_reps": "15-20", "mins": 8},
        {"id": "split_squat", "name": "Split Squat", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "reverse_lunge", "name": "Reverse Lunge", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "glute_bridge", "name": "Glute Bridge", "default_sets": 4, "default_reps": "12-20", "mins": 8},
        {"id": "wall_sit", "name": "Wall Sit", "default_sets": 3, "default_reps": "45-60 sec", "mins": 7},
        {"id": "step_ups", "name": "Step-ups", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "goblet_squat", "name": "Goblet Squat", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"]},
        {"id": "db_rdl", "name": "Dumbbell Romanian Deadlift", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "db_lunge", "name": "Dumbbell Walking Lunge", "default_sets": 3, "default_reps": "10 each leg", "mins": 10, "needs": ["dumbbells"]},
        {"id": "kb_swing", "name": "Kettlebell Swing", "default_sets": 4, "default_reps": "15-20", "mins": 10, "needs": ["kettlebell"]},
        {"id": "back_squat", "name": "Back Squat", "default_sets": 5, "default_reps": "5", "mins": 12, "needs": ["barbell", "squat_rack"]},
        {"id": "front_squat", "name": "Front Squat", "default_sets": 4, "default_reps": "5-8", "mins": 12, "needs": ["barbell", "squat_rack"]},
        {"id": "deadlift", "name": "Deadlift", "default_sets": 4, "default_reps": "4-6", "mins": 12, "needs": ["barbell"]},
        {"id": "hip_thrust", "name": "Barbell Hip Thrust", "default_sets": 4, "default_reps": "8-12", "mins": 12, "needs": ["barbell", "bench"]},
        {"id": "cable_kickback", "name": "Cable Kickback", "default_sets": 3, "default_reps": "12-15 each", "mins": 9, "needs": ["cable_machine"]},
        {"id": "calf_raise", "name": "Standing Calf Raise", "default_sets": 4, "default_reps": "15-20", "mins": 7},
    ],
    "core": [
        {"id": "plank", "name": "Plank", "default_sets": 4, "default_reps": "30-60 sec", "mins": 8},
        {"id": "side_plank", "name": "Side Plank", "default_sets": 3, "default_reps": "30-45 sec each", "mins": 7},
        {"id": "deadbug", "name": "Dead Bug", "default_sets": 3, "default_reps": "10 each side", "mins": 6},
        {"id": "bird_dog", "name": "Bird Dog", "default_sets": 3, "default_reps": "10 each side", "mins": 6},
        {"id": "mountain_climbers", "name": "Mountain Climbers", "default_sets": 3, "default_reps": "30-45 sec", "mins": 6},
        {"id": "bicycle_crunch", "name": "Bicycle Crunch", "default_sets": 3, "default_reps": "20 total", "mins": 6},
        {"id": "russian_twist", "name": "Russian Twist", "default_sets": 3, "default_reps": "20 total", "mins": 6},
        {"id": "leg_raises", "name": "Leg Raises", "default_sets": 3, "default_reps": "10-15", "mins": 7},
        {"id": "hollow_hold", "name": "Hollow Body Hold", "default_sets": 3, "default_reps": "20-40 sec", "mins": 6},
        {"id": "ab_rollout", "name": "Ab Rollout", "default_sets": 3, "default_reps": "8-12", "mins": 8, "needs": ["barbell"]},
        {"id": "cable_crunch", "name": "Cable Crunch", "default_sets": 4, "default_reps": "12-15", "mins": 9, "needs": ["cable_machine"]},
        {"id": "pallof_press", "name": "Pallof Press", "default_sets": 3, "default_reps": "10 each side", "mins": 8, "needs": ["resistance_bands|cable_machine"]},
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
      <p>Suggested: {ex['default_sets']} sets x {ex['default_reps']}</p>
      <p>Estimated time: ~{ex['mins']} min</p>
    </div>
    """


def render_options_page(options=None, body_part="full_body", minutes=30, equipment=None):
    equipment = equipment or []
    cards_html = "".join(exercise_card(ex) for ex in options) if options else ""

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
          <h2>Select Exercises</h2>
          <p><strong>Target time:</strong> {minutes} min</p>
          <p id="pick-status"><strong>Selected time:</strong> 0 min</p>

          <div style="margin-bottom:1rem;">
            <button type="submit">Start Workout</button>
          </div>

          <div class="grid">{cards_html}</div>

          <input type="hidden" name="target_minutes" value="{minutes}">
          {hidden_data}
        </form>
        """

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
    .grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }}
    .exercise-card {{ border:1px solid #e5e7eb; border-radius:10px; padding:.75rem; background:#fff; }}
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
      <label><input type="checkbox" name="equipment" value="resistance_bands" {checked("resistance_bands", equipment)}> Resistance Bands</label>
      <label><input type="checkbox" name="equipment" value="pullup_bar" {checked("pullup_bar", equipment)}> Pull-up Bar</label>
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
      <p><strong>Suggested:</strong> {sets} sets x {reps}</p>

      <div class="entry-row">
        <label>Sets done:
          <input type="number" min="0" value="{sets}" class="sets-done">
        </label>
        <label>Reps done each set:
          <input type="text" value="{reps}" class="reps-done">
        </label>
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
  <p>Mark sets as completed and start rest timer whenever you finish a set.</p>

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

    # metadata passthrough for available ids
    meta_pushups_name: str = Form(default=""), meta_pushups_sets: str = Form(default=""), meta_pushups_reps: str = Form(default=""),
    meta_bw_squat_name: str = Form(default=""), meta_bw_squat_sets: str = Form(default=""), meta_bw_squat_reps: str = Form(default=""),
    meta_walking_lunge_name: str = Form(default=""), meta_walking_lunge_sets: str = Form(default=""), meta_walking_lunge_reps: str = Form(default=""),
    meta_mountain_climbers_name: str = Form(default=""), meta_mountain_climbers_sets: str = Form(default=""), meta_mountain_climbers_reps: str = Form(default=""),
    meta_burpees_name: str = Form(default=""), meta_burpees_sets: str = Form(default=""), meta_burpees_reps: str = Form(default=""),
    meta_db_thruster_name: str = Form(default=""), meta_db_thruster_sets: str = Form(default=""), meta_db_thruster_reps: str = Form(default=""),
    meta_db_row_name: str = Form(default=""), meta_db_row_sets: str = Form(default=""), meta_db_row_reps: str = Form(default=""),
    meta_goblet_squat_name: str = Form(default=""), meta_goblet_squat_sets: str = Form(default=""), meta_goblet_squat_reps: str = Form(default=""),
    meta_kb_swing_name: str = Form(default=""), meta_kb_swing_sets: str = Form(default=""), meta_kb_swing_reps: str = Form(default=""),
    meta_barbell_complex_name: str = Form(default=""), meta_barbell_complex_sets: str = Form(default=""), meta_barbell_complex_reps: str = Form(default=""),
    meta_front_squat_name: str = Form(default=""), meta_front_squat_sets: str = Form(default=""), meta_front_squat_reps: str = Form(default=""),
    meta_bench_press_name: str = Form(default=""), meta_bench_press_sets: str = Form(default=""), meta_bench_press_reps: str = Form(default=""),
    meta_diamond_pushups_name: str = Form(default=""), meta_diamond_pushups_sets: str = Form(default=""), meta_diamond_pushups_reps: str = Form(default=""),
    meta_pike_pushups_name: str = Form(default=""), meta_pike_pushups_sets: str = Form(default=""), meta_pike_pushups_reps: str = Form(default=""),
    meta_chair_dips_name: str = Form(default=""), meta_chair_dips_sets: str = Form(default=""), meta_chair_dips_reps: str = Form(default=""),
    meta_band_row_name: str = Form(default=""), meta_band_row_sets: str = Form(default=""), meta_band_row_reps: str = Form(default=""),
    meta_band_press_name: str = Form(default=""), meta_band_press_sets: str = Form(default=""), meta_band_press_reps: str = Form(default=""),
    meta_db_bench_name: str = Form(default=""), meta_db_bench_sets: str = Form(default=""), meta_db_bench_reps: str = Form(default=""),
    meta_db_incline_press_name: str = Form(default=""), meta_db_incline_press_sets: str = Form(default=""), meta_db_incline_press_reps: str = Form(default=""),
    meta_db_shoulder_press_name: str = Form(default=""), meta_db_shoulder_press_sets: str = Form(default=""), meta_db_shoulder_press_reps: str = Form(default=""),
    meta_db_lateral_raise_name: str = Form(default=""), meta_db_lateral_raise_sets: str = Form(default=""), meta_db_lateral_raise_reps: str = Form(default=""),
    meta_db_bicep_curl_name: str = Form(default=""), meta_db_bicep_curl_sets: str = Form(default=""), meta_db_bicep_curl_reps: str = Form(default=""),
    meta_db_tricep_ext_name: str = Form(default=""), meta_db_tricep_ext_sets: str = Form(default=""), meta_db_tricep_ext_reps: str = Form(default=""),
    meta_pullups_name: str = Form(default=""), meta_pullups_sets: str = Form(default=""), meta_pullups_reps: str = Form(default=""),
    meta_barbell_row_name: str = Form(default=""), meta_barbell_row_sets: str = Form(default=""), meta_barbell_row_reps: str = Form(default=""),
    meta_overhead_press_name: str = Form(default=""), meta_overhead_press_sets: str = Form(default=""), meta_overhead_press_reps: str = Form(default=""),
    meta_cable_row_name: str = Form(default=""), meta_cable_row_sets: str = Form(default=""), meta_cable_row_reps: str = Form(default=""),
    meta_lat_pulldown_name: str = Form(default=""), meta_lat_pulldown_sets: str = Form(default=""), meta_lat_pulldown_reps: str = Form(default=""),
    meta_split_squat_name: str = Form(default=""), meta_split_squat_sets: str = Form(default=""), meta_split_squat_reps: str = Form(default=""),
    meta_reverse_lunge_name: str = Form(default=""), meta_reverse_lunge_sets: str = Form(default=""), meta_reverse_lunge_reps: str = Form(default=""),
    meta_glute_bridge_name: str = Form(default=""), meta_glute_bridge_sets: str = Form(default=""), meta_glute_bridge_reps: str = Form(default=""),
    meta_wall_sit_name: str = Form(default=""), meta_wall_sit_sets: str = Form(default=""), meta_wall_sit_reps: str = Form(default=""),
    meta_step_ups_name: str = Form(default=""), meta_step_ups_sets: str = Form(default=""), meta_step_ups_reps: str = Form(default=""),
    meta_db_rdl_name: str = Form(default=""), meta_db_rdl_sets: str = Form(default=""), meta_db_rdl_reps: str = Form(default=""),
    meta_db_lunge_name: str = Form(default=""), meta_db_lunge_sets: str = Form(default=""), meta_db_lunge_reps: str = Form(default=""),
    meta_back_squat_name: str = Form(default=""), meta_back_squat_sets: str = Form(default=""), meta_back_squat_reps: str = Form(default=""),
    meta_deadlift_name: str = Form(default=""), meta_deadlift_sets: str = Form(default=""), meta_deadlift_reps: str = Form(default=""),
    meta_hip_thrust_name: str = Form(default=""), meta_hip_thrust_sets: str = Form(default=""), meta_hip_thrust_reps: str = Form(default=""),
    meta_cable_kickback_name: str = Form(default=""), meta_cable_kickback_sets: str = Form(default=""), meta_cable_kickback_reps: str = Form(default=""),
    meta_calf_raise_name: str = Form(default=""), meta_calf_raise_sets: str = Form(default=""), meta_calf_raise_reps: str = Form(default=""),
    meta_plank_name: str = Form(default=""), meta_plank_sets: str = Form(default=""), meta_plank_reps: str = Form(default=""),
    meta_side_plank_name: str = Form(default=""), meta_side_plank_sets: str = Form(default=""), meta_side_plank_reps: str = Form(default=""),
    meta_deadbug_name: str = Form(default=""), meta_deadbug_sets: str = Form(default=""), meta_deadbug_reps: str = Form(default=""),
    meta_bird_dog_name: str = Form(default=""), meta_bird_dog_sets: str = Form(default=""), meta_bird_dog_reps: str = Form(default=""),
    meta_bicycle_crunch_name: str = Form(default=""), meta_bicycle_crunch_sets: str = Form(default=""), meta_bicycle_crunch_reps: str = Form(default=""),
    meta_russian_twist_name: str = Form(default=""), meta_russian_twist_sets: str = Form(default=""), meta_russian_twist_reps: str = Form(default=""),
    meta_leg_raises_name: str = Form(default=""), meta_leg_raises_sets: str = Form(default=""), meta_leg_raises_reps: str = Form(default=""),
    meta_hollow_hold_name: str = Form(default=""), meta_hollow_hold_sets: str = Form(default=""), meta_hollow_hold_reps: str = Form(default=""),
    meta_ab_rollout_name: str = Form(default=""), meta_ab_rollout_sets: str = Form(default=""), meta_ab_rollout_reps: str = Form(default=""),
    meta_cable_crunch_name: str = Form(default=""), meta_cable_crunch_sets: str = Form(default=""), meta_cable_crunch_reps: str = Form(default=""),
    meta_pallof_press_name: str = Form(default=""), meta_pallof_press_sets: str = Form(default=""), meta_pallof_press_reps: str = Form(default=""),
):
    form_data = {k: v for k, v in locals().items() if k.startswith("meta_")}
    return render_session_page(selected_exercises, form_data, max(1, target_minutes))
