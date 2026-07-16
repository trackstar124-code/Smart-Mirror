"""Events module: reads upcoming events from events.json for the dashboard.

Same "widget" idea as clock.py / weather.py — plain Python that returns data.
The difference: this returns a LIST of events (not a single dict), so the
template will loop over it.

Fill in the TODOs yourself. Pointers are given, not answers.
"""
import json
from pathlib import Path

# Path to the events file, built relative to THIS file so it works no matter
# which folder you run Python from. (Path(__file__).parent = this file's folder.)
EVENTS_FILE = Path(__file__).parent / "events.json"

def get_events():
    """Get the events file and return it as a python dic"""
    with open(EVENTS_FILE, "r") as f:
        events = json.load(f)
        return events

if __name__ == "__main__":
    print(get_events())
