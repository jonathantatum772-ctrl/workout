from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

# -------------------------
# Exercise data
# -------------------------
EXERCISES = {
    "full_body": [
        {"name": "Push-ups", "sets": 3, "reps": "10-15", "mins": 6, "video_id": "IODxDxX7oi4", "image": "https://img.youtube.com/vi/IODxDxX7oi4/hqdefault.jpg"},
        {"name": "Bodyweight Squat", "sets": 3, "reps": "15-20", "mins": 6, "video_id": "aclHkVaku9U", "image": "https://img.youtube.com/vi/aclHkVaku9U/hqdefault.jpg"},
        {"name": "Dumbbell Row", "sets": 4, "reps": "8-12", "mins": 10, "needs": ["dumbbells"], "video_id": "pYcpY20QaE8", "image": "https://img.youtube.com/vi/pYcpY20QaE8/hqdefault.jpg"},
        {"name": "Goblet Squat", "sets": 4, "reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"], "video_id": "MeIiIdhvXT4", "image": "https://img.youtube.com/vi/MeIiIdhvXT4/hqdefault.jpg"},
    ],
    "upper_body": [
        {"name": "Push-ups", "sets": 4, "reps": "10-15", "mins": 8, "video_id": "IODxDxX7oi4", "image": "https://img.youtube.com/vi/IODxDxX7oi4/hqdefault.jpg"},
        {"name": "Dumbbell Bench Press", "sets": 4, "reps": "8-12", "mins": 10, "needs": ["dumbbells"], "video_id": "VmB1G1K7v94", "image": "https://img.youtube.com/vi/VmB1G1K7v94/hqdefault.jpg"},
        {"name": "One-Arm Dumbbell Row", "sets": 4, "reps": "8-12 each", "mins": 12, "needs": ["dumbbells"], "video_id": "pYcpY20QaE8", "image": "https://img.youtube.com/vi/pYcpY20QaE8/hqdefault.jpg"},
    ],
    "lower_body": [
        {"name": "Bodyweight Squat", "sets": 4, "reps": "15-20", "mins": 8, "video_id": "aclHkVaku9U", "image": "https://img.youtube.com/vi/aclHkVaku9U/hqdefault.jpg"},
        {"name": "Reverse Lunge", "sets": 3, "reps": "10 each", "mins": 8, "video_id": "wrwwXE_x-pQ", "image": "https://img.youtube.com/vi/wrwwXE_x-pQ/hqdefault.jpg"},
        {"name": "Goblet Squat", "sets": 4, "reps": "8-12", "mins": 10, "needs": ["dumbbells|kettlebell"], "video_id": "MeIiIdhvXT4", "image": "https://img.youtube.com/vi/MeIiIdhvXT4/hqdefault.jpg"},
    ],
    "core": [
        {"name": "Plank", "sets": 4, "reps": "30-60 sec", "mins": 8, "video_id": "ASdvN_XEl_c", "image": "https://img.youtube.com/vi/ASdvN_XEl_c/hqdefault.jpg"},
        {"name": "Dead Bug", "sets": 3, "reps": "10 each", "mins": 6, "video_id": "4XLEnwUr8S4", "image": "https://img.youtube.com/vi/4XLEnwUr8S4/hqdefault.jpg"},
        {"name": "Russian Twist", "sets": 3, "reps": "20 total", "mins": 6, "video_id": "wkD8rjkodUI", "image": "https://img.youtube.com/vi/wkD8rjkodUI/hqdefault.jpg"},
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


def media_block(ex, media_mode):
    if media_mode == "video":
        return f"""
        <iframe width="100%" height="220"
          src="https://www.youtube.com/embed/{ex["video_id"]}"
          title="{ex["name"]} demo"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          loading="lazy"></iframe>
        """
    if media_mode == "image":
        return f'<img src="{ex["image"]}" alt="{ex["name"]} example" style="width:100%;border-radius:8px;" loading="lazy" />'
    return "<p style='color:#6b7280;'>Demo hidden (set media mode to Video or Image).</p>"


def build_exercise_html(options, media_mode):
    blocks = []
    for ex in options:
        set_boxes = []
        for s in range(1, ex["sets"] + 1):
            set_boxes.append(f'<label><input type="checkbox" class="set-box"> Set {s}</label>')
        blocks.append(
            f"""
            <div class="exercise-card">
              <div class="row">
                <label><input type="checkbox" class="exercise-pick" data-mins="{ex['mins']}"> <strong>{ex['name']}</strong></label>
                <span class="chip">~{ex['mins']} min</span>
              </div>
              <p>Sets: {ex['sets']} | Reps/Time: {ex['reps']}</p>
              {media_block(ex, media_mode)}
              <div style="margin-top:.5rem;">{' '.join(set_boxes)}</div>
            </div>
            """
        )
    return "\n".join(blocks)


def render_page(options=None, body_part="full_body", minutes=30, equipment=None, media_mode="video"):
    equipment = equipment or []
    options_html = ""
    if options:
        options_html = f"""
        <div class="card" style="margin-top:1rem;">
          <h2>Pick Exercises Until You Hit Your Time</h2>
          <p><strong>Target:</strong> {minutes} min</p>
          <p id="time-status"><strong>Selected time:</strong> 0 min</p>

          <div style="margin:.75rem 0;">
            <button type="button" id="start-workout-btn">▶ Start Workout Timer</button>
            <button type="button" id="stop-workout-btn">⏹ Stop</button>
            <span id="workout-timer" class="timer">00:00</span>
          </div>

          <div class="grid">
            {build_exercise_html(options, media_mode)}
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
    .timer {{ font-family: monospace; font-weight: bold; margin-left: .5rem; font-size:1.1rem; }}
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

    <p>
      <label><strong>Show Demos As</strong></label><br/>
      <select name="media_mode" required>
        <option value="video" {selected_attr("video", media_mode)}>Video</option>
        <option value="image" {selected_attr("image", media_mode)}>Image</option>
        <option value="none" {selected_attr("none", media_mode)}>None</option>
      </select>
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

      picks.forEach(function(p) {{ p.addEventListener('change', updateTime); }});
      updateTime();

      // Workout timer
      var timerEl = document.getElementById('workout-timer');
      var startBtn = document.getElementById('start-workout-btn');
      var stopBtn = document.getElementById('stop-workout-btn');
      var intervalId = null;
      var remaining = target * 60;

      function fmt(sec) {{
        var m = String(Math.floor(sec / 60)).padStart(2, '0');
        var s = String(sec % 60).padStart(2, '0');
        return m + ":" + s;
      }}

      if (timerEl) timerEl.textContent = fmt(remaining);

      if (startBtn) {{
        startBtn.addEventListener('click', function() {{
          if (intervalId) return;
          intervalId = setInterval(function() {{
            remaining -= 1;
            if (timerEl) timerEl.textContent = fmt(Math.max(remaining, 0));
            if (remaining <= 0) {{
              clearInterval(intervalId);
              intervalId = null;
              if (timerEl) timerEl.textContent = "DONE ✅";
            }}
          }}, 1000);
        }});
      }}

      if (stopBtn) {{
        stopBtn.addEventListener('click', function() {{
          if (intervalId) {{
            clearInterval(intervalId);
            intervalId = null;
          }}
        }});
      }}
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
    minutes: int = Form(...),
    media_mode: str = Form(...)
):
    options = get_options(body_part, equipment)
    return render_page(
        options=options,
        body_part=body_part,
        minutes=max(1, minutes),
        equipment=equipment,
        media_mode=media_mode if media_mode in {"video", "image", "none"} else "video"
    )
