from datetime import datetime

def get_time():
    now = datetime.now()
    date = now.strftime("%A, %B %d")
    time = now.strftime("%H:%M:%S")
    return {"date": date, "time": time}

