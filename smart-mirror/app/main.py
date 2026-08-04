"""Smart Mirror web app.

Serves a fullscreen dashboard (time, date, weather) to the browser.

How to run:
    python smart-mirror/app/main.py
Then open http://localhost:8000 in your browser.

Fill in the TODOs yourself. Pointers are given, not answers.
"""
import threading
from modules.gestures import run as run_gestures
from modules.month import get_calendar
from modules.events import get_events
from modules.weather import get_weather, get_forecast
from modules.clock import get_time
from modules.gestures import read_gesture, pop_event
from modules.news import get_news
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
    forecast = get_forecast()
    events = get_events()
    cal = get_calendar()
    return render_template("index.html", clock=clock, weather=weather, forecast=forecast, events=events, cal=cal)

@app.route("/api/gesture")
def api_gesture():
    """
    Two separate fields, because they behave differently:
      gesture -> the CURRENT pose ("FIST", "OK", "NONE"). Safe to read repeatedly;
                 it stays the same until the hand changes.
      event   -> a one-shot swipe, or "" if nothing happened. POPPED here, so it
                 is returned to exactly one poll and then gone. Don't add another
                 caller to this endpoint or they'll steal each other's events.
    """
    return jsonify({"gesture": read_gesture(), "event": pop_event()})

@app.route("/api/weather")
def api_weather():
    """Return current weather + 4-day forecast as JSON."""
    return jsonify({"current": get_weather(), "forecast": get_forecast()})

@app.route("/api/news")
def api_news():
    return jsonify({"articles": get_news()})

if __name__ == "__main__":
    gesture_thread = threading.Thread(
        target=run_gestures,
        daemon=True
    )
    gesture_thread.start()
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)
