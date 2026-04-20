import json
from datetime import datetime
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

# ------------------------------------------------------------
# Exercise library (no images/videos)
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
    ],
    "upper_body": [
        {"id": "pushups", "name": "Push-ups", "default_sets": 4, "default_reps": "10-15", "mins": 8},
        {"id": "diamond_pushups", "name": "Diamond Push-ups", "default_sets": 3, "default_reps": "8-12", "mins": 7},
        {"id": "pike_pushups", "name": "Pike Push-ups", "default_sets": 3, "default_reps": "8-12", "mins": 7},
        {"id": "chair_dips", "name": "Chair Dips", "default_sets": 3, "default_reps": "10-15", "mins": 7},
        {"id": "db_bench", "name": "Dumbbell Bench Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "db_shoulder_press", "name": "Dumbbell Shoulder Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "db_bicep_curl", "name": "Dumbbell Bicep Curl", "default_sets": 3, "default_reps": "10-15", "mins": 8, "needs": ["dumbbells"]},
        {"id": "pullups", "name": "Pull-ups", "default_sets": 4, "default_reps": "AMRAP", "mins": 10, "needs": ["pullup_bar"]},
        {"id": "barbell_row", "name": "Barbell Row", "default_sets": 4, "default_reps": "6-10", "mins": 10, "needs": ["barbell"]},
    ],
    "lower_body": [
        {"id": "bw_squat", "name": "Bodyweight Squat", "default_sets": 4, "default_reps": "15-20", "mins": 8},
        {"id": "reverse_lunge", "name": "Reverse Lunge", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "glute_bridge", "name": "Glute Bridge", "default_sets": 4, "default_reps": "12-20", "mins": 8},
        {"id": "step_ups", "name": "Step-ups", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "goblet_squat", "name": "Goblet Squat", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"]},
        {"id": "db_rdl", "name": "Dumbbell Romanian Deadlift", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "back_squat", "name": "Back Squat", "default_sets": 5, "default_reps": "5", "mins": 12, "needs": ["barbell", "squat_rack"]},
        {"id": "deadlift", "name": "Deadlift", "default_sets": 4, "default_reps": "4-6", "mins": 12, "needs": ["barbell"]},
    ],
    "core": [
        {"id": "plank", "name": "Plank", "default_sets": 4, "default_reps": "30-60 sec", "mins": 8},
        {"id": "side_plank", "name": "Side Plank", "default_sets": 3, "default_reps": "30-45 sec each", "mins": 7},
        {"id": "deadbug", "name": "Dead Bug", "default_sets": 3, "default_reps": "10 each side", "mins": 6},
        {"id": "bicycle_crunch", "name": "Bicycle Crunch", "default_sets": 3, "default_reps": "20 total", "mins": 6},
        {"id": "leg_raises", "name": "Leg Raises", "default_sets": 3, "default_reps": "10-15", "mins": 7},
        {"id": "cable_crunch", "name": "Cable Crunch", "default_sets": 4, "default_reps": "12-15", "mins": 9, "needs": ["cable_machine"]},
    ],
}


def has_equipment(exercise: dict, selected: list[str]) -> bool:
    needs = exercise.get("needs", [])
    if not needs:
        return True

    selected_set = {x.strip().lower() for x in selected if x.strip() and x.lower() != "none"}

    for rule in needs:
        if "|" in rule:
            options = set(rule.split("|"))
            if not (options & selected_set):
                return False
        elif rule not in selected_set:
            return False
    return True


def get_filtered_options(body_part: str, equipment: list[str]) -> list[dict]:
    body = body_part if body_part in EXERCISES else "full_body"
    options = [e for e in EXERCISES[body] if has_equipment(e, equipment)]
    if not options:
        options = [e for e in EXERCISES[body] if "needs" not in e]
    return options


def selected_attr(value: str, current: str) -> str:
    return "selected" if value == current else ""


def checked(value: str, selected: list[str]) -> str:
    return "checked" if value in selected else ""


def render_planner_page(
    options: list[dict] | None = None,
    body_part: str = "full_body",
    minutes: int = 30,
    equipment: list[str] | None = None,
) -> str:
    equipment = equipment or []
    options = options or []

    option_cards = ""
    if options:
        for ex in options:
            option_cards += f"""
            <div class="exercise-card">
              <label>
                <input type="checkbox" name="selected_exercises" value="{ex['id']}" class="pick-box" data-mins="{ex['mins']}">
                <strong>{ex['name']}</strong>
              </label>
              <p>Suggested: {ex['default_sets']} sets x {ex['default_reps']}</p>
              <p>Estimated time: ~{ex['mins']} min</p>
            </div>
            """

    options_block = ""
    if options:
        payload = json.dumps(options).replace('"', "&quot;")
        options_block = f"""
        <form method="post" action="/start" class="card" style="margin-top:1rem;">
          <h2>Select Exercises</h2>
          <p><strong>Target time:</strong> {minutes} min</p>
          <p id="pick-status"><strong>Selected time:</strong> 0 min</p>
          <div class="grid">{option_cards}</div>

          <input type="hidden" name="target_minutes" value="{minutes}">
          <input type="hidden" name="exercise_payload" value="{payload}">
          <button type="submit" style="margin-top:1rem;">Start Workout</button>
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
    .equip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:.4rem; border:1px solid #e2e8f0; border-radius:10px; padding:.75rem; }}
    .grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }}
    .exercise-card {{ border:1px solid #e5e7eb; border-radius:10px; padding:.75rem; background:#fff; }}
    .history-item {{ border:1px solid #e5e7eb; border-radius:8px; padding:.6rem; margin-bottom:.5rem; background:#fff; }}
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

    <p><strong>Equipment (select all you have)</strong></p>
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

  <div class="card" style="margin-top:1rem;">
    <h2>Workout History</h2>
    <div id="history-list"></div>
    <button type="button" id="clear-history-btn">Clear History</button>
  </div>

  <script>
    (function() {{
      // selected time counter
      var picks = document.querySelectorAll('.pick-box');
      var status = document.getElementById('pick-status');
      var target = {minutes};

      function updateSelectedTime() {{
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

      picks.forEach(function(p) {{ p.addEventListener('change', updateSelectedTime); }});
      updateSelectedTime();

      // history render
      var historyList = document.getElementById("history-list");
      var clearBtn = document.getElementById("clear-history-btn");

      function renderHistory() {{
        if (!historyList) return;
        var items = [];
        try {{
          items = JSON.parse(localStorage.getItem("workout_history") || "[]");
        }} catch (e) {{
          items = [];
        }}

        if (!items.length) {{
          historyList.innerHTML = "<p>No saved workouts yet.</p>";
          return;
        }}

        var html = "";
        items.slice().reverse().forEach(function(item) {{
          var ex = (item.exercises || []).join(", ");
          html += "<div class='history-item'>" +
                    "<p><strong>Completed:</strong> " + (item.completed_at || "-") + "</p>" +
                    "<p><strong>Target:</strong> " + item.target_minutes + " min</p>" +
                    "<p><strong>Actual duration:</strong> " + item.actual_duration + "</p>" +
                    "<p><strong>Exercises:</strong> " + ex + "</p>" +
                  "</div>";
        }});
        historyList.innerHTML = html;
      }}

      if (clearBtn) {{
        clearBtn.addEventListener("click", function() {{
          localStorage.removeItem("workout_history");
          renderHistory();
        }});
      }}

      renderHistory();
    }})();
  </script>
</body>
</html>
    """


def render_session_page(selected_ids: list[str], payload: list[dict], target_minutes: int) -> str:
    if not selected_ids:
        return """
        <html><body style='font-family:Arial;padding:2rem;'>
          <h2>No exercises selected.</h2>
          <p><a href='/'>Go back and select at least one exercise.</a></p>
        </body></html>
        """

    by_id = {e["id"]: e for e in payload}
    selected = [by_id[eid] for eid in selected_ids if eid in by_id]

    if not selected:
        return """
        <html><body style='font-family:Arial;padding:2rem;'>
          <h2>Selected exercises were not found.</h2>
          <p><a href='/'>Go back to planner.</a></p>
        </body></html>
        """

    rows_html = ""
    selected_names = [ex["name"] for ex in selected]

    for ex_idx, ex in enumerate(selected):
        sets = max(1, int(ex.get("default_sets", 3)))
        reps_default = ex.get("default_reps", "10")

        set_items = ""
        for set_idx in range(1, sets + 1):
            set_id = f"{ex_idx}-{set_idx}"
            set_items += f"""
            <div class="set-item">
              <label><input type="checkbox" class="set-done" data-setid="{set_id}" data-rest="60"> Set {set_idx}</label>
              <label>Reps done: <input type="number" min="0" value="0" class="set-reps"></label>

              <label>Custom rest (sec):
                <input type="number" min="5" value="60" class="custom-rest-input" id="custom-rest-{set_id}">
              </label>

              <span id="rest-{set_id}" class="set-timer">00:00</span>

              <button type="button" onclick="startSetRest('{set_id}', 30)">30s</button>
              <button type="button" onclick="startSetRest('{set_id}', 60)">60s</button>
              <button type="button" onclick="startSetRest('{set_id}', 90)">90s</button>
              <button type="button" onclick="startCustomRest('{set_id}')">Custom</button>
              <button type="button" onclick="stopSetRest('{set_id}')">Stop</button>
            </div>
            """

        rows_html += f"""
        <div class="session-card">
          <h3>{ex["name"]}</h3>
          <p><strong>Suggested:</strong> {sets} sets x {reps_default}</p>
          <div class="set-list">{set_items}</div>
        </div>
        """

    exercises_json = json.dumps(selected_names).replace('"', "&quot;")
    started_at = datetime.utcnow().isoformat()

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Workout Session</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .session-card {{ background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:1rem; margin-bottom:1rem; }}
    .set-list {{ display:grid; gap:.6rem; }}
    .set-item {{ display:flex; align-items:center; gap:.6rem; flex-wrap:wrap; border:1px solid #e5e7eb; border-radius:8px; padding:.5rem; }}
    .set-timer {{ font-family:monospace; font-weight:700; min-width:60px; }}
    .workout-timer {{ font-family:monospace; font-weight:700; font-size:1.2rem; margin-left:.5rem; }}
    button, input {{ padding:.45rem; }}
  </style>
</head>
<body>
  <h1>Workout Session</h1>
  <p><strong>Target time:</strong> {target_minutes} min</p>

  <div style="margin: .8rem 0 1rem 0;">
    <button type="button" id="start-workout-btn">▶ Start Workout</button>
    <button type="button" id="pause-workout-btn">⏸ Pause</button>
    <button type="button" id="reset-workout-btn">↺ Reset</button>
    <button type="button" id="complete-workout-btn">✅ Complete & Save Workout</button>
    <span id="workout-countdown" class="workout-timer">00:00</span>
  </div>

  <p>Check sets one-by-one. Checking a set auto-starts a 60s rest timer.</p>

  {rows_html}

  <p><a href="/">← Back to planner</a></p>

  <script>
    (function() {{
      var totalSeconds = {max(1, target_minutes)} * 60;
      var remaining = totalSeconds;
      var workoutInterval = null;
      var startedAt = "{started_at}";
      var hasStarted = false;

      var display = document.getElementById("workout-countdown");
      var startBtn = document.getElementById("start-workout-btn");
      var pauseBtn = document.getElementById("pause-workout-btn");
      var resetBtn = document.getElementById("reset-workout-btn");
      var completeBtn = document.getElementById("complete-workout-btn");

      function fmt(sec) {{
        var m = String(Math.floor(sec / 60)).padStart(2, "0");
        var s = String(sec % 60).padStart(2, "0");
        return m + ":" + s;
      }}

      function updateDisplay() {{
        if (display) display.textContent = fmt(Math.max(remaining, 0));
      }}
      updateDisplay();

      if (startBtn) {{
        startBtn.addEventListener("click", function() {{
          if (workoutInterval) return;
          hasStarted = true;
          workoutInterval = setInterval(function() {{
            remaining -= 1;
            updateDisplay();
            if (remaining <= 0) {{
              clearInterval(workoutInterval);
              workoutInterval = null;
              if (display) display.textContent = "DONE ✅";
            }}
          }}, 1000);
        }});
      }}

      if (pauseBtn) {{
        pauseBtn.addEventListener("click", function() {{
          if (workoutInterval) {{
            clearInterval(workoutInterval);
            workoutInterval = null;
          }}
        }});
      }}

      if (resetBtn) {{
        resetBtn.addEventListener("click", function() {{
          if (workoutInterval) {{
            clearInterval(workoutInterval);
            workoutInterval = null;
          }}
          remaining = totalSeconds;
          hasStarted = false;
          updateDisplay();
        }});
      }}

      // per-set rest timers
      var setTimers = {{}};

      function setFmt(sec) {{
        var m = String(Math.floor(sec / 60)).padStart(2, "0");
        var s = String(sec % 60).padStart(2, "0");
        return m + ":" + s;
      }}

      window.startSetRest = function(setId, seconds) {{
        window.stopSetRest(setId);
        var left = seconds;
        var el = document.getElementById("rest-" + setId);
        if (!el) return;
        el.textContent = setFmt(left);

        setTimers[setId] = setInterval(function() {{
          left -= 1;
          el.textContent = setFmt(Math.max(left, 0));
          if (left <= 0) {{
            clearInterval(setTimers[setId]);
            delete setTimers[setId];
            el.textContent = "DONE ✅";
          }}
        }}, 1000);
      }};

      window.stopSetRest = function(setId) {{
        if (setTimers[setId]) {{
          clearInterval(setTimers[setId]);
          delete setTimers[setId];
        }}
        var el = document.getElementById("rest-" + setId);
        if (el) el.textContent = "00:00";
      }};

      window.startCustomRest = function(setId) {{
        var input = document.getElementById("custom-rest-" + setId);
        var sec = 60;
        if (input && input.value) {{
          sec = Number(input.value);
        }}
        if (!sec || sec < 5) sec = 5;
        window.startSetRest(setId, sec);
      }};

      // auto-start 60s rest when a set is checked
      var setChecks = document.querySelectorAll(".set-done");
      setChecks.forEach(function(cb) {{
        cb.addEventListener("change", function() {{
          var setId = cb.getAttribute("data-setid");
          if (cb.checked) {{
            window.startSetRest(setId, 60);
          }} else {{
            window.stopSetRest(setId);
          }}
        }});
      }});

      // save workout to localStorage history
      if (completeBtn) {{
        completeBtn.addEventListener("click", function() {{
          if (workoutInterval) {{
            clearInterval(workoutInterval);
            workoutInterval = null;
          }}

          var now = new Date();
          var completedAt = now.toLocaleString();
          var actualSeconds = totalSeconds - remaining;
          if (!hasStarted) actualSeconds = 0;

          var mins = Math.floor(actualSeconds / 60);
          var secs = actualSeconds % 60;
          var actualDuration = String(mins).padStart(2, "0") + ":" + String(secs).padStart(2, "0");

          var item = {{
            completed_at: completedAt,
            completed_at_iso: now.toISOString(),
            started_at_utc: startedAt,
            target_minutes: {max(1, target_minutes)},
            actual_duration: actualDuration,
            exercises: {exercises_json}
          }};

          var history = [];
          try {{
            history = JSON.parse(localStorage.getItem("workout_history") || "[]");
          }} catch (e) {{
            history = [];
          }}

          history.push(item);
          localStorage.setItem("workout_history", JSON.stringify(history));

          alert("Workout saved! You can view it on the planner page history.");
        }});
      }}
    }})();
  </script>
</body>
</html>
    """


@app.get("/", response_class=HTMLResponse)
async def home():
    return render_planner_page()


@app.post("/decide", response_class=HTMLResponse)
async def decide(
    body_part: str = Form(...),
    equipment: list[str] = Form(default=[]),
    minutes: int = Form(...)
):
    options = get_filtered_options(body_part, equipment)
    return render_planner_page(
        options=options,
        body_part=body_part,
        minutes=max(1, minutes),
        equipment=equipment,
    )


@app.post("/start", response_class=HTMLResponse)
async def start_workout(
    selected_exercises: list[str] = Form(default=[]),
    target_minutes: int = Form(default=30),
    exercise_payload: str = Form(default="[]"),
):
    try:
        payload = json.loads(exercise_payload)
        if not isinstance(payload, list):
            payload = []
    except Exception:
        payload = []

    return render_session_page(
        selected_ids=selected_exercises,
        payload=payload,
        target_minutes=max(1, target_minutes),
    )
