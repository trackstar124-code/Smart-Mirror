import calendar
from datetime import datetime
# Make weeks start on Sunday (US-style calendars). Remove this line if you'd
# rather weeks start on Monday (the default).
calendar.setfirstweekday(calendar.SUNDAY)


def get_calendar():
    """gets calendar and returns the month date and year for the Calender command"""
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
