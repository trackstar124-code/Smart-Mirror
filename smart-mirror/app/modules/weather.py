import requests
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

def get_api_key():
    """Gets API key from the .env file"""
    api_key = os.environ.get("WEATHER_API_KEY")
    return api_key


def fetch_weather(lat: float, lon: float, api_key, units="imperial"):
    """Fetch the weather data using the get_api_key function"""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units
    }
    response = requests.get(url, params=params)
    response.raise_for_status()   # causes the api call not to work if the api call failed
    return response.json()


def get_location():
    "Get location for where ever the decive is"
    url = "http://ip-api.com/json/"
    params = {
        "fields": "city,country,lat,lon,timezone"
        }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching location: {e}")
        return None


def print_weather(data):
    """prints the weather data for Boston"""
    temp = data["main"]["temp"]
    city = data["name"]
    print(f"{city}: {temp}°F")

def return_weather(data):
    """Extract the temp + city from an API response and return them as a dict."""
    temp = data["main"]["temp"]
    city = data["name"]
    icon = data["weather"][0]["icon"]
    return {"temp": temp, "city": city, "icon": icon}


def get_weather():
    """Do the full weather pipeline and return a dict for the dashboard."""
    api_key = get_api_key()
    location = get_location()

    if location is None:
        print("Could not determine location, defaulting to Boston.")
        lat, lon = 42.3601, -71.0589
    else:
        lat, lon = location["lat"], location["lon"]
                            
    data = fetch_weather(lat, lon, api_key)
    return return_weather(data)






def fetch_forecast(lat: float, lon: float, api_key, units="imperial"):
    """Fetch 5-day / 3-hour forecast from OpenWeatherMap."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_forecast():
    """Return a list of up to 4 future daily forecasts (noon-ish reading per day)."""
    api_key = get_api_key()
    location = get_location()

    if location is None:
        lat, lon = 42.3601, -71.0589
    else:
        lat, lon = location["lat"], location["lon"]

    data = fetch_forecast(lat, lon, api_key)
    entries = data.get("list", [])

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seen_days = set()
    forecast = []

    for entry in entries:
        dt_txt = entry.get("dt_txt", "")         # e.g. "2024-07-29 12:00:00"
        day_str = dt_txt[:10]                    # "2024-07-29"
        hour    = dt_txt[11:13]                  # "12"

        # Skip today; only grab ~noon (12:00) readings so we get one per day
        if day_str == today_str:
            continue
        if hour != "12":
            continue
        if day_str in seen_days:
            continue

        seen_days.add(day_str)
        dt_obj = datetime.strptime(day_str, "%Y-%m-%d")
        forecast.append({
            "day":  dt_obj.strftime("%a"),       # "Mon", "Tue", …
            "temp": round(entry["main"]["temp"]),
            "icon": entry["weather"][0]["icon"],
        })

        if len(forecast) == 4:
            break

    return forecast


if __name__ == "__main__":
    print(get_weather())
    print(get_forecast())
