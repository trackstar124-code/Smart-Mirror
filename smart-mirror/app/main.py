"""Smart Mirror web app (Week 2).

Serves a fullscreen dashboard (time, date, weather) to the browser.

How to run:
    python smart-mirror/app/main.py
Then open http://localhost:8000 in your browser.

Fill in the TODOs yourself. Pointers are given, not answers.
"""
from modules.month import get_calendar
from modules.events import get_events
from modules.weather import get_weather
from modules.clock import get_time
from flask import Flask, render_template, jsonify



# Create the Flask application.
#   __name__            -> tells Flask where this app lives (standard boilerplate)
#   template_folder     -> where your HTML files live (relative to THIS file)
#   static_folder       -> where CSS / JS / images live
app = Flask(
    __name__,
    template_folder="ui/templates",
    static_folder="ui/static",
)


@app.route("/")
def index():
    """Serve the main dashboard page (the index.html template)."""
    clock = get_time()
    weather = get_weather()
    events = get_events()
    cal = get_calendar()
    return render_template("index.html", clock=clock, weather=weather, events=events, cal=cal)

@app.route("/api/gesture")
def api_gesture():
    return jsonify({"gesture": "OPEN_PALM"})




if __name__ == "__main__":
    # debug=True auto-reloads the server whenever you save a change,
    # and shows helpful error pages in the browser while you're learning.
    app.run(host="0.0.0.0", port=8000, debug=True)
