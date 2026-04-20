from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Free Workout Decider")

RULES = {
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

def decide(goal: str, equipment: str, minutes: int) -> str:
    goal = goal if goal in RULES else "strength"
    equipment = equipment if equipment in RULES[goal] else "none"
    workout = RULES[goal][equipment]
    minutes = max(1, minutes)
    if minutes < 20:
        return f"Quick {minutes}-Minute Version: {workout}"
    if minutes <= 45:
        return f"Standard {minutes}-Minute Session: {workout}"
    return f"Extended {minutes}-Minute Session: {workout} + mobility cooldown"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html><body style="font-family:Arial;max-width:700px;margin:40px auto;">
      <h1>Free Workout Decider</h1>
      <form method="post" action="/decide">
        <p>Goal:
          <select name="goal">
            <option value="strength">Build Strength</option>
            <option value="fat_loss">Fat Loss</option>
            <option value="endurance">Endurance</option>
          </select>
        </p>
        <p>Equipment:
          <select name="equipment">
            <option value="none">None</option>
            <option value="basic">Basic</option>
            <option value="full">Full Gym</option>
          </select>
        </p>
        <p>Minutes: <input type="number" name="minutes" value="30" min="1"></p>
        <button type="submit">Get Workout</button>
      </form>
    </body></html>
    """

@app.post("/decide", response_class=HTMLResponse)
async def decide_post(goal: str = Form(...), equipment: str = Form(...), minutes: int = Form(...)):
    recommendation = decide(goal, equipment, minutes)
    return f"""
    <html><body style="font-family:Arial;max-width:700px;margin:40px auto;">
      <h1>Your Recommendation</h1>
      <p>{recommendation}</p>
      <p><a href="/">← Back</a></p>
    </body></html>
    """
