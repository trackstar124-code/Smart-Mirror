from unittest.mock import Mock
from modules.weather import get_weather, return_weather

def test_return_weather():
    fake_api_data = {
        "main": {"temp": 72.5},
        "name": "Boston",
        "weather": [{"icon": "01d"}]
    }
    result = return_weather(fake_api_data)
    assert result == {"temp": 72.5, "city": "Boston", "icon": "01d"}

def test_get_weather(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "fake_key")
    
    def mock_get(url, params=None, timeout=None):
        mock_resp = Mock()
        if "ip-api.com" in url:
            mock_resp.json.return_value = {"lat": 42.0, "lon": -71.0}
        else:
            mock_resp.json.return_value = {
                "main": {"temp": 75.0},
                "name": "Mock City",
                "weather": [{"icon": "02d"}]
            }
        return mock_resp

    monkeypatch.setattr("modules.weather.requests.get", mock_get)
    
    result = get_weather()
    assert result["temp"] == 75.0
    assert result["city"] == "Mock City"
