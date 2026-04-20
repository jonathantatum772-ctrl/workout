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
    "chest": [
        {"id": "pushups", "name": "Push-ups", "default_sets": 4, "default_reps": "10-15", "mins": 8},
        {"id": "diamond_pushups", "name": "Diamond Push-ups", "default_sets": 3, "default_reps": "8-12", "mins": 7},
        {"id": "db_bench", "name": "Dumbbell Bench Press", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
    ],
    "triceps": [
        {"id": "bench_dips", "name": "Bench Dips", "default_sets": 4, "default_reps": "10-15", "mins": 8},
        {"id": "close_pushups", "name": "Close-Grip Push-ups", "default_sets": 4, "default_reps": "8-12", "mins": 8},
        {"id": "db_oh_ext", "name": "DB Overhead Tricep Extension", "default_sets": 3, "default_reps": "10-15", "mins": 8, "needs": ["dumbbells"]},
    ],
    "biceps": [
        {"id": "db_curl", "name": "Dumbbell Curl", "default_sets": 4, "default_reps": "10-15", "mins": 9, "needs": ["dumbbells"]},
        {"id": "hammer_curl", "name": "Hammer Curl", "default_sets": 4, "default_reps": "10-12", "mins": 9, "needs": ["dumbbells"]},
        {"id": "barbell_curl", "name": "Barbell Curl", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["barbell"]},
    ],
    "back": [
        {"id": "pullups", "name": "Pull-ups", "default_sets": 4, "default_reps": "AMRAP", "mins": 10, "needs": ["pullup_bar"]},
        {"id": "db_row", "name": "Dumbbell Row", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells"]},
        {"id": "barbell_row", "name": "Barbell Row", "default_sets": 4, "default_reps": "6-10", "mins": 10, "needs": ["barbell"]},
    ],
    "legs": [
        {"id": "bw_squat", "name": "Bodyweight Squat", "default_sets": 4, "default_reps": "15-20", "mins": 8},
        {"id": "reverse_lunge", "name": "Reverse Lunge", "default_sets": 3, "default_reps": "10 each leg", "mins": 8},
        {"id": "goblet_squat", "name": "Goblet Squat", "default_sets": 4, "default_reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"]},
    ],
    "core": [
        {"id": "plank", "name": "Plank", "default_sets": 4, "default_reps": "30-60 sec", "mins": 8},
        {"id": "side_plank", "name": "Side Plank", "default_sets": 3, "default_reps": "30-45 sec each", "mins": 7},
        {"id": "deadbug", "name": "Dead Bug", "default_sets": 3, "default_reps": "10 each", "mins": 6},
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
    part = body_part if body_part in EXERCISES else "full_body"
    options = [e for e in EXERCISES[part] if has_equipment(e, equipment)]
    if not options:
        options = [e for e in EXERCISES[part] if "needs" not in e]
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
          <label class="title-row">
            <input type="checkbox" name="selected_exercises" value="{ex['id']}" class="pick-box" data-mins="{ex['mins']}">
            <strong>{ex['name']}</strong>
          </label>
          <p>Suggested: {ex['default_sets']} sets x {ex['default_reps']}</p>
          <p class="muted">Estimated time: ~{ex['mins']} min</p>
        </div>
        """

    options_block = ""
    if options:
        payload = json.dumps(options).replace('"', "&quot;")
        options_block = f"""
        <form method="post" action="/start" class="card glass" style="margin-top:1rem;">
          <h2>Select Exercises</h2>
          <p><strong>Target time:</strong> {minutes} min</p>
          <p id="pick-status"><strong>Selected time:</strong> 0 min</p>
          <div class="grid">{cards}</div>
          <input type="hidden" name="target_minutes" value="{minutes}">
          <input type="hidden" name="exercise_payload" value="{payload}">
          <button type="submit" class="btn-primary" style="margin-top:1rem;">Start Workout</button>
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
    :root {{
      --bg1: #0f172a;
      --bg2: #111827;
      --card: rgba(255,255,255,0.08);
      --border: rgba(255,255,255,0.15);
      --text: #e5e7eb;
      --muted: #cbd5e1;
      --accent: #60a5fa;
      --accent2: #22d3ee;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      color: var(--text);
      background: radial-gradient(circle at top right, #1e3a8a 0%, var(--bg1) 45%, var(--bg2) 100%);
      min-height: 100vh;
    }}
    .wrap {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem 2rem; }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1rem;
      backdrop-filter: blur(8px);
    }}
    .glass {{ box-shadow: 0 12px 32px rgba(0,0,0,.25); }}
    .muted {{ color: var(--muted); }}
    .equip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: .45rem;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: .75rem;
      background: rgba(255,255,255,.03);
    }}
    .grid {{
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }}
    .exercise-card {{
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: .75rem;
      background: rgba(255,255,255,.03);
    }}
    .title-row {{ display: flex; gap: .5rem; align-items: center; }}
    input, select, button {{
      border-radius: 10px;
      border: 1px solid var(--border);
      padding: .55rem .65rem;
      color: var(--text);
      background: rgba(255,255,255,.06);
    }}
    button {{ cursor: pointer; }}
    .btn-primary {{
      border: none;
      background: linear-gradient(90deg, var(--accent), var(--accent2));
      color: #0b1020;
      font-weight: 700;
    }}
    .history-item {{
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: .7rem;
      margin-bottom: .6rem;
      background: rgba(255,255,255,.03);
    }}
    .history-ex {{ margin: .4rem 0 .2rem 1rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Free Workout Decider</h1>
    <p class="muted">Pick exact muscle groups, equipment, and time.</p>

    <form method="post" action="/decide" class="card glass">
      <p>
        <label><strong>Muscle Group</strong></label><br/>
        <select name="body_part" required>
          <option value="full_body" {selected_attr("full_body", body_part)}>Full Body</option>
          <option value="chest" {selected_attr("chest", body_part)}>Chest</option>
          <option value="triceps" {selected_attr("triceps", body_part)}>Triceps</option>
          <option value="biceps" {selected_attr("biceps", body_part)}>Biceps</option>
          <option value="back" {selected_attr("back", body_part)}>Back</option>
          <option value="legs" {selected_attr("legs", body_part)}>Legs</option>
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

      <button type="submit" class="btn-primary">Show Matching Exercises</button>
    </form>

    {options_block}

    <div class="card glass" style="margin-top:1rem;">
      <h2>Past Workouts</h2>
      <div id="history-list"></div>
      <button type="button" id="clear-history-btn">Clear History</button>
    </div>
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
          historyList.innerHTML = "<p class='muted'>No saved workouts yet.</p>";
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
        return "<html><body style='font-family:Arial;padding:2rem;'><h2>No exercises selected.</h2><p><a href='/'>Go back.</a></p></body></html>"

    by_id = {e["id"]: e for e in payload}
    selected = [by_id[eid] for eid in selected_ids if eid in by_id]
    if not selected:
        return "<html><body style='font-family:Arial;padding:2rem;'><h2>Selected exercises not found.</h2><p><a href='/'>Back</a></p></body></html>"

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
        <div class="session-card" data-exercise-name="{ex['name']}" data-planned-sets="{sets}" data-next-set="{sets + 1}" data-ex-index="{ex_idx}">
          <h3>{ex["name"]}</h3>
          <p><strong>Suggested:</strong> <span class="set-count">{sets}</span> sets x {reps_default}</p>
          <button type="button" class="delete-ex-btn">🗑 Delete Exercise</button>
          <button type="button" class="add-set-btn">➕ Add Set</button>
          <button type="button" class="remove-set-btn">➖ Delete Last Set</button>
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
    :root {{
      --bg1: #0f172a;
      --bg2: #111827;
      --card: rgba(255,255,255,0.08);
      --border: rgba(255,255,255,0.15);
      --text: #e5e7eb;
      --accent: #60a5fa;
      --accent2: #22d3ee;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      color: var(--text);
      background: radial-gradient(circle at top right, #1e3a8a 0%, var(--bg1) 45%, var(--bg2) 100%);
      min-height: 100vh;
    }}
    .wrap {{ max-width: 980px; margin: 2rem auto; padding: 0 1rem 2rem; }}
    .session-card, .add-box {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem;
      margin-bottom: 1rem;
      backdrop-filter: blur(8px);
    }}
    .set-list {{ display:grid; gap:.6rem; margin-top:.6rem; }}
    .set-item {{
      display:flex; align-items:center; gap:.6rem; flex-wrap:wrap;
      border:1px solid var(--border); border-radius:10px; padding:.55rem;
      background: rgba(255,255,255,.03);
    }}
    .set-timer {{ font-family: monospace; font-weight: 700; min-width: 60px; }}
    .workout-timer {{ font-family: monospace; font-weight: 700; font-size: 1.2rem; margin-left: .5rem; }}
    button, input {{
      border-radius: 10px; border: 1px solid var(--border);
      color: var(--text); background: rgba(255,255,255,.06);
      padding: .45rem .6rem;
    }}
    .btn-primary {{
      border: none; color: #0b1020; font-weight: 700;
      background: linear-gradient(90deg, var(--accent), var(--accent2));
    }}
    a {{ color: #93c5fd; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Workout Session</h1>
    <p><strong>Target time:</strong> {target_minutes} min</p>

    <div style="margin:.8rem 0 1rem 0;">
      <button type="button" id="start-workout-btn" class="btn-primary">▶ Start Workout</button>
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
      <button type="button" id="add-ex-btn" class="btn-primary">Add Exercise</button>
    </div>

    <p>You can add/delete exercises and sets while working out.</p>

    <div id="session-container">
      {rows}
    </div>

    <p><a href="/">← Back to planner</a></p>
  </div>

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

      function timerEl(setId) {{
        return document.getElementById("rest-" + setId);
      }}

      function stopSetRest(setId) {{
        if (setTimers[setId]) {{
          clearInterval(setTimers[setId]);
          delete setTimers[setId];
        }}
        var el = timerEl(setId);
        if (el) el.textContent = "00:00";
      }}

      function startSetRest(setId, seconds) {{
        stopSetRest(setId);
        var left = seconds;
        var el = timerEl(setId);
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

      function createSetRow(setId, setNumber) {{
        var div = document.createElement("div");
        div.className = "set-item";
        div.setAttribute("data-setid", setId);
        div.innerHTML =
          "<label><input type='checkbox' class='set-done'> Set " + setNumber + "</label>" +
          "<label>Reps done: <input type='number' min='0' value='0' class='set-reps'></label>" +
          "<label>Custom rest (sec): <input type='number' min='5' value='60' class='custom-rest-input'></label>" +
          "<span id='rest-" + setId + "' class='set-timer'>00:00</span>" +
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
        card.setAttribute("data-next-set", String(sets + 1));
        card.setAttribute("data-ex-index", String(exIdx));

        card.innerHTML =
          "<h3>" + name + "</h3>" +
          "<p><strong>Suggested:</strong> <span class='set-count'>" + sets + "</span> sets x " + reps + "</p>" +
          "<button type='button' class='delete-ex-btn'>🗑 Delete Exercise</button> " +
          "<button type='button' class='add-set-btn'>➕ Add Set</button> " +
          "<button type='button' class='remove-set-btn'>➖ Delete Last Set</button>" +
          "<div class='set-list'></div>";

        var list = card.querySelector(".set-list");
        for (var i = 1; i <= sets; i++) {{
          var sid = exIdx + "-" + i;
          list.appendChild(createSetRow(sid, i));
        }}
        container.appendChild(card);
      }}

      function updateCardSetMeta(card) {{
        var count = card.querySelectorAll(".set-item").length;
        card.setAttribute("data-planned-sets", String(count));
        var setCountEl = card.querySelector(".set-count");
        if (setCountEl) setCountEl.textContent = String(count);
      }}

      document.getElementById("add-ex-btn").addEventListener("click", function() {{
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

      document.addEventListener("click", function(e) {{
        var t = e.target;

        if (t.classList.contains("delete-ex-btn")) {{
          var card = t.closest(".session-card");
          if (card) card.remove();
          return;
        }}

        if (t.classList.contains("add-set-btn")) {{
          var cardAdd = t.closest(".session-card");
          if (!cardAdd) return;
          var exIndex = cardAdd.getAttribute("data-ex-index");
          var nextSet = Number(cardAdd.getAttribute("data-next-set") || "1");
          var sidAdd = exIndex + "-" + nextSet;
          var setList = cardAdd.querySelector(".set-list");
          setList.appendChild(createSetRow(sidAdd, nextSet));
          cardAdd.setAttribute("data-next-set", String(nextSet + 1));
          updateCardSetMeta(cardAdd);
          return;
        }}

        if (t.classList.contains("remove-set-btn")) {{
          var cardRemove = t.closest(".session-card");
          if (!cardRemove) return;
          var setList2 = cardRemove.querySelector(".set-list");
          var items = setList2.querySelectorAll(".set-item");
          if (!items.length) return;
          var last = items[items.length - 1];
          var setId = last.getAttribute("data-setid");
          stopSetRest(setId);
          last.remove();
          updateCardSetMeta(cardRemove);
          return;
        }}

        var setItem = t.closest(".set-item");
        if (!setItem) return;

        var setId = setItem.getAttribute("data-setid");
        var restInput = setItem.querySelector(".custom-rest-input");

        if (t.classList.contains("rest-btn")) {{
          var sec = Number(t.getAttribute("data-seconds") || "60");
          if (restInput) restInput.value = String(sec);
          startSetRest(setId, sec);
          return;
        }}

        if (t.classList.contains("rest-custom-btn")) {{
          var customSec = Number(restInput && restInput.value ? restInput.value : "60");
          if (!customSec || customSec < 5) customSec = 5;
          if (restInput) restInput.value = String(customSec);
          startSetRest(setId, customSec);
          return;
        }}

        if (t.classList.contains("rest-stop-btn")) {{
          stopSetRest(setId);
          return;
        }}
      }});

      document.addEventListener("change", function(e) {{
        var t = e.target;
        if (!t.classList.contains("set-done")) return;

        var setItem = t.closest(".set-item");
        if (!setItem) return;
        var setId = setItem.getAttribute("data-setid");
        var restInput = setItem.querySelector(".custom-rest-input");

        if (t.checked) {{
          var sec = Number(restInput && restInput.value ? restInput.value : "60");
          if (!sec || sec < 5) sec = 5;
          if (restInput) restInput.value = String(sec);
          startSetRest(setId, sec);
        }} else {{
          stopSetRest(setId);
        }}
      }});

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

          checks.forEach(function(cb, i) {{
            if (cb.checked) completedSets += 1;
            repsBySet.push(reps[i] ? (reps[i].value || "0") : "0");
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
          started_at_utc: "{started_at}",
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

        alert("Workout saved.");
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
