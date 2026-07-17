"""Month calendar widget: builds the current month as a grid for the dashboard.

Returns the month laid out as rows of weeks, so the template can draw a normal
wall-calendar grid.

Fill in the TODOs yourself. Pointers are given, not answers.
"""
import calendar
from datetime import datetime

# Make weeks start on Sunday (US-style calendars). Remove this line if you'd
# rather weeks start on Monday (the default).
calendar.setfirstweekday(calendar.SUNDAY)


def get_calendar():
    now = datetime.now()
    weeks = calendar.monthcalendar(now.year, now.month)
    return {
        "month_name": calendar.month_name[now.month],
        "year": now.year,
        "weeks": weeks,
        "today": now.day,
    }

if __name__ == "__main__":
    print(get_calendar())
