import json
from datetime import datetime
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

EXERCISES = {
    "full_body": [
        {"id": "pushups", "name": "Push-ups", "default_sets": 3, "default_reps": "10-15", "mins": 6},
        {"id": "bw_squat", "name": "Bodyweight Squat", "default_sets": 3, "default_reps": "15-20", "mins": 6},
        {"id": "walking_lunge", "name": "Walking Lunge", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "db_row", "name": "Dumbbell Row", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "goblet_squat", "name": "Goblet Squat", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"]},
    ],
    "upper_body": [
        {"id": "pushups", "name": "Push-ups", "default_sets": 4, "default_reps": "10-15", "mins": 8},
        {"id": "db_bench", "name": "Dumbbell Bench Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "db_shoulder_press", "name": "Dumbbell Shoulder Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "pullups", "name": "Pull-ups", "default_sets": 4, "default_reps": "AMRAP", "mins": 10, "needs": ["pullup_bar"]},
    ],
    "lower_body": [
        {"id": "bw_squat", "name": "Bodyweight Squat", "default_sets": 4, "default_reps": "15-20", "mins": 8},
        {"id": "reverse_lunge", "name": "Reverse Lunge", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "glute_bridge", "name": "Glute Bridge", "default_sets": 4, "default_reps": "12-20", "mins": 8},
        {"id": "goblet_squat", "name": "Goblet Squat", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"]},
    ],
    "core": [
        {"id": "plank", "name": "Plank", "default_sets": 4, "default_reps": "30-60 sec", "mins": 8},
        {"id": "side_plank", "name": "Side Plank", "default_sets": 3, "default_reps": "30-45 sec each", "mins": 7},
        {"id": "deadbug", "name": "Dead Bug", "default_sets": 3, "default_reps": "10 each side", "mins": 6},
        {"id": "bicycle_crunch", "name": "Bicycle Crunch", "default_sets": 3, "default_reps": "20 total", "mins": 6},
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


def render_planner_page(options=None, body_part="full_body", minutes=30, equipment=None):
    options = options or []
    equipment = equipment or []

    cards = ""
    for ex in options:
        cards += f"""
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
          <div class="grid">{cards}</div>
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
  <title>Workout Planner</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .card {{ background:#fff; border-radius:12px; padding:1rem; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
    .equip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:.4rem; border:1px solid #e2e8f0; border-radius:10px; padding:.75rem; }}
    .grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }}
    .exercise-card {{ border:1px solid #e5e7eb; border-radius:10px; padding:.75rem; background:#fff; }}
    .history-item {{ border:1px solid #e5e7eb; border-radius:8px; padding:.6rem; margin-bottom:.6rem; background:#fff; }}
    .history-ex {{ margin: .4rem 0 .2rem 1rem; }}
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

  <div class="card" style="margin-top:1rem;">
    <h2>Past Workouts</h2>
    <div id="history-list"></div>
    <button type="button" id="clear-history-btn">Clear History</button>
  </div>

  <script>
    (function() {{
      var picks = document.querySelectorAll(".pick-box");
      var status = document.getElementById("pick-status");
      var target = {minutes};

      function updateSelectedTime() {{
        if (!status) return;
        var total = 0;
        picks.forEach(function(p) {{
          if (p.checked) total += Number(p.dataset.mins || 0);
        }});
        status.innerHTML = total >= target
          ? "<strong>Selected time:</strong> " + total + " min ✅ target met"
          : "<strong>Selected time:</strong> " + total + " min (need " + (target - total) + " more)";
      }}
      picks.forEach(function(p) {{ p.addEventListener("change", updateSelectedTime); }});
      updateSelectedTime();

      var historyList = document.getElementById("history-list");
      var clearBtn = document.getElementById("clear-history-btn");

      function renderHistory() {{
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
          var exHtml = "";
          (item.exercise_logs || []).forEach(function(ex) {{
            exHtml += "<div class='history-ex'>" +
                      "<p><strong>" + ex.name + "</strong></p>" +
                      "<p>Planned sets: " + ex.planned_sets + " | Completed sets: " + ex.completed_sets + "</p>" +
                      "<p>Reps by set: " + (ex.reps_by_set || []).join(", ") + "</p>" +
                      "</div>";
          }});

          html += "<div class='history-item'>" +
                  "<p><strong>Completed:</strong> " + (item.completed_at || "-") + "</p>" +
                  "<p><strong>Target:</strong> " + item.target_minutes + " min | <strong>Actual:</strong> " + item.actual_duration + "</p>" +
                  exHtml +
                  "</div>";
        }});

        historyList.innerHTML = html;
      }}

      clearBtn.addEventListener("click", function() {{
        localStorage.removeItem("workout_history");
        renderHistory();
      }});

      renderHistory();
    }})();
  </script>
</body>
</html>
    """


def render_session_page(selected_ids, payload, target_minutes):
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
          <h2>Selected exercises not found.</h2>
          <p><a href='/'>Back</a></p>
        </body></html>
        """

    rows = ""
    for ex_idx, ex in enumerate(selected):
        sets = max(1, int(ex.get("default_sets", 3)))
        reps_default = ex.get("default_reps", "10")
        set_rows = ""

        for s in range(1, sets + 1):
            sid = f"{ex_idx}-{s}"
            set_rows += f"""
            <div class="set-item" data-setid="{sid}">
              <label><input type="checkbox" class="set-done"> Set {s}</label>
              <label>Reps done: <input type="number" min="0" value="0" class="set-reps"></label>
              <label>Custom rest (sec): <input type="number" min="5" value="60" class="custom-rest-input"></label>
              <span id="rest-{sid}" class="set-timer">00:00</span>
              <button type="button" class="rest-btn" data-seconds="30">30s</button>
              <button type="button" class="rest-btn" data-seconds="60">60s</button>
              <button type="button" class="rest-btn" data-seconds="90">90s</button>
              <button type="button" class="rest-custom-btn">Custom</button>
              <button type="button" class="rest-stop-btn">Stop</button>
            </div>
            """

        rows += f"""
        <div class="session-card" data-exercise-name="{ex['name']}" data-planned-sets="{sets}">
          <h3>{ex["name"]}</h3>
          <p><strong>Suggested:</strong> {sets} sets x {reps_default}</p>
          <button type="button" class="delete-ex-btn">🗑 Delete Exercise</button>
          <div class="set-list">{set_rows}</div>
        </div>
        """

    started_at = datetime.utcnow().isoformat()

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Workout Session</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 980px; margin: 2rem auto; padding: 0 1rem; background:#f5f7fb; }}
    .session-card {{ background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:1rem; margin-bottom:1rem; }}
    .set-list {{ display:grid; gap:.6rem; margin-top:.6rem; }}
    .set-item {{ display:flex; align-items:center; gap:.6rem; flex-wrap:wrap; border:1px solid #e5e7eb; border-radius:8px; padding:.5rem; }}
    .set-timer {{ font-family:monospace; font-weight:700; min-width:60px; }}
    .workout-timer {{ font-family:monospace; font-weight:700; font-size:1.2rem; margin-left:.5rem; }}
    .add-box {{ background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:1rem; margin-bottom:1rem; }}
    button, input {{ padding:.45rem; }}
  </style>
</head>
<body>
  <h1>Workout Session</h1>
  <p><strong>Target time:</strong> {target_minutes} min</p>

  <div style="margin:.8rem 0 1rem 0;">
    <button type="button" id="start-workout-btn">▶ Start Workout</button>
    <button type="button" id="pause-workout-btn">⏸ Pause</button>
    <button type="button" id="reset-workout-btn">↺ Reset</button>
    <button type="button" id="complete-workout-btn">✅ Complete & Save Workout</button>
    <span id="workout-countdown" class="workout-timer">00:00</span>
  </div>

  <div class="add-box">
    <h3>Add Exercise Mid-Workout</h3>
    <label>Exercise Name: <input type="text" id="new-ex-name" placeholder="e.g. Tricep Dips"></label>
    <label>Sets: <input type="number" min="1" value="3" id="new-ex-sets"></label>
    <label>Default reps: <input type="text" value="10-12" id="new-ex-reps"></label>
    <button type="button" id="add-ex-btn">Add Exercise</button>
  </div>

  <p>Checking a set uses the custom rest input for that set and starts the timer.</p>
  <div id="session-container">
    {rows}
  </div>

  <p><a href="/">← Back to planner</a></p>

  <script>
    (function() {{
      var totalSeconds = {max(1, target_minutes)} * 60;
      var remaining = totalSeconds;
      var workoutInterval = null;
      var hasStarted = false;
      var startedAt = "{started_at}";
      var setTimers = {{}};
      var dynamicExerciseIdx = 1000;

      var display = document.getElementById("workout-countdown");
      var startBtn = document.getElementById("start-workout-btn");
      var pauseBtn = document.getElementById("pause-workout-btn");
      var resetBtn = document.getElementById("reset-workout-btn");
      var completeBtn = document.getElementById("complete-workout-btn");
      var container = document.getElementById("session-container");

      function fmt(sec) {{
        var m = String(Math.floor(sec / 60)).padStart(2, "0");
        var s = String(sec % 60).padStart(2, "0");
        return m + ":" + s;
      }}

      function updateDisplay() {{
        display.textContent = fmt(Math.max(remaining, 0));
      }}
      updateDisplay();

      startBtn.addEventListener("click", function() {{
        if (workoutInterval) return;
        hasStarted = true;
        workoutInterval = setInterval(function() {{
          remaining -= 1;
          updateDisplay();
          if (remaining <= 0) {{
            clearInterval(workoutInterval);
            workoutInterval = null;
            display.textContent = "DONE ✅";
          }}
        }}, 1000);
      }});

      pauseBtn.addEventListener("click", function() {{
        if (workoutInterval) {{
          clearInterval(workoutInterval);
          workoutInterval = null;
        }}
      }});

      resetBtn.addEventListener("click", function() {{
        if (workoutInterval) {{
          clearInterval(workoutInterval);
          workoutInterval = null;
        }}
        remaining = totalSeconds;
        hasStarted = false;
        updateDisplay();
      }});

      function getSetTimerEl(setId) {{
        return document.getElementById("rest-" + setId);
      }}

      function stopSetRest(setId) {{
        if (setTimers[setId]) {{
          clearInterval(setTimers[setId]);
          delete setTimers[setId];
        }}
        var el = getSetTimerEl(setId);
        if (el) el.textContent = "00:00";
      }}

      function startSetRest(setId, seconds) {{
        stopSetRest(setId);
        var left = seconds;
        var el = getSetTimerEl(setId);
        if (!el) return;
        el.textContent = fmt(left);

        setTimers[setId] = setInterval(function() {{
          left -= 1;
          el.textContent = fmt(Math.max(left, 0));
          if (left <= 0) {{
            clearInterval(setTimers[setId]);
            delete setTimers[setId];
            el.textContent = "DONE ✅";
          }}
        }}, 1000);
      }}

      function buildSetRow(exIdx, setNum) {{
        var sid = exIdx + "-" + setNum;
        var div = document.createElement("div");
        div.className = "set-item";
        div.setAttribute("data-setid", sid);
        div.innerHTML =
          "<label><input type='checkbox' class='set-done'> Set " + setNum + "</label>" +
          "<label>Reps done: <input type='number' min='0' value='0' class='set-reps'></label>" +
          "<label>Custom rest (sec): <input type='number' min='5' value='60' class='custom-rest-input'></label>" +
          "<span id='rest-" + sid + "' class='set-timer'>00:00</span>" +
          "<button type='button' class='rest-btn' data-seconds='30'>30s</button>" +
          "<button type='button' class='rest-btn' data-seconds='60'>60s</button>" +
          "<button type='button' class='rest-btn' data-seconds='90'>90s</button>" +
          "<button type='button' class='rest-custom-btn'>Custom</button>" +
          "<button type='button' class='rest-stop-btn'>Stop</button>";
        return div;
      }}

      function addExerciseCard(name, sets, reps) {{
        var exIdx = dynamicExerciseIdx++;
        var card = document.createElement("div");
        card.className = "session-card";
        card.setAttribute("data-exercise-name", name);
        card.setAttribute("data-planned-sets", String(sets));

        var html = "<h3>" + name + "</h3>" +
                   "<p><strong>Suggested:</strong> " + sets + " sets x " + reps + "</p>" +
                   "<button type='button' class='delete-ex-btn'>🗑 Delete Exercise</button>" +
                   "<div class='set-list'></div>";
        card.innerHTML = html;

        var list = card.querySelector(".set-list");
        for (var i = 1; i <= sets; i++) {{
          list.appendChild(buildSetRow(exIdx, i));
        }}

        container.appendChild(card);
      }}

      // Add exercise button
      var addBtn = document.getElementById("add-ex-btn");
      addBtn.addEventListener("click", function() {{
        var name = (document.getElementById("new-ex-name").value || "").trim();
        var sets = Number(document.getElementById("new-ex-sets").value || "3");
        var reps = (document.getElementById("new-ex-reps").value || "10-12").trim();
        if (!name) {{
          alert("Please enter exercise name.");
          return;
        }}
        if (!sets || sets < 1) sets = 1;
        addExerciseCard(name, sets, reps);

        document.getElementById("new-ex-name").value = "";
        document.getElementById("new-ex-sets").value = "3";
        document.getElementById("new-ex-reps").value = "10-12";
      }});

      // CLICK event delegation (rest buttons / delete)
      document.addEventListener("click", function(e) {{
        var target = e.target;

        if (target.classList.contains("delete-ex-btn")) {{
          var card = target.closest(".session-card");
          if (card) card.remove();
          return;
        }}

        var setItem = target.closest(".set-item");
        if (!setItem) return;

        var setId = setItem.getAttribute("data-setid");
        var restInput = setItem.querySelector(".custom-rest-input");

        if (target.classList.contains("rest-btn")) {{
          var sec = Number(target.getAttribute("data-seconds") || "60");
          if (restInput) restInput.value = String(sec); // autofill
          startSetRest(setId, sec);
          return;
        }}

        if (target.classList.contains("rest-custom-btn")) {{
          var customSec = Number(restInput && restInput.value ? restInput.value : "60");
          if (!customSec || customSec < 5) customSec = 5;
          if (restInput) restInput.value = String(customSec);
          startSetRest(setId, customSec);
          return;
        }}

        if (target.classList.contains("rest-stop-btn")) {{
          stopSetRest(setId);
          return;
        }}
      }});

      // CHANGE event delegation (checkbox auto-uses box value)
      document.addEventListener("change", function(e) {{
        var target = e.target;
        if (!target.classList.contains("set-done")) return;

        var setItem = target.closest(".set-item");
        if (!setItem) return;

        var setId = setItem.getAttribute("data-setid");
        var restInput = setItem.querySelector(".custom-rest-input");
        var sec = Number(restInput && restInput.value ? restInput.value : "60");
        if (!sec || sec < 5) sec = 5;
        if (restInput) restInput.value = String(sec);

        if (target.checked) {{
          startSetRest(setId, sec);
        }} else {{
          stopSetRest(setId);
        }}
      }});

      // Save workout
      completeBtn.addEventListener("click", function() {{
        if (workoutInterval) {{
          clearInterval(workoutInterval);
          workoutInterval = null;
        }}

        var now = new Date();
        var completedAt = now.toLocaleString();

        var actualSeconds = hasStarted ? (totalSeconds - remaining) : 0;
        var mins = Math.floor(actualSeconds / 60);
        var secs = actualSeconds % 60;
        var actualDuration = String(mins).padStart(2, "0") + ":" + String(secs).padStart(2, "0");

        var cards = document.querySelectorAll(".session-card");
        var exerciseLogs = [];

        cards.forEach(function(card) {{
          var name = card.getAttribute("data-exercise-name") || "Exercise";
          var plannedSets = Number(card.getAttribute("data-planned-sets") || "0");

          var checks = card.querySelectorAll(".set-done");
          var reps = card.querySelectorAll(".set-reps");

          var completedSets = 0;
          var repsBySet = [];

          checks.forEach(function(cb, idx) {{
            if (cb.checked) completedSets += 1;
            repsBySet.push(reps[idx] ? (reps[idx].value || "0") : "0");
          }});

          exerciseLogs.push({{
            name: name,
            planned_sets: plannedSets,
            completed_sets: completedSets,
            reps_by_set: repsBySet
          }});
        }});

        var item = {{
          completed_at: completedAt,
          completed_at_iso: now.toISOString(),
          started_at_utc: startedAt,
          target_minutes: {max(1, target_minutes)},
          actual_duration: actualDuration,
          exercise_logs: exerciseLogs
        }};

        var history = [];
        try {{
          history = JSON.parse(localStorage.getItem("workout_history") || "[]");
        }} catch (e) {{
          history = [];
        }}
        history.push(item);
        localStorage.setItem("workout_history", JSON.stringify(history));

        alert("Workout saved with full details.");
      }});
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
    minutes: int = Form(...),
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
