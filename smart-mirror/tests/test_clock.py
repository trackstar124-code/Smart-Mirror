import datetime
from modules.clock import get_time

class FakeDatetime(datetime.datetime):
    @classmethod
    def now(cls):
        # Freeze time at a specific moment for predictable testing
        return cls(2023, 10, 31, 14, 30, 0)

def test_get_time(monkeypatch):
    monkeypatch.setattr("modules.clock.datetime", FakeDatetime)
    
    result = get_time()
    
    assert result == {
        "date": "Tuesday, October 31",
        "time": "14:30:00"
    }
