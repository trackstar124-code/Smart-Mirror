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
    """Return a list of up to 4 future daily forecasts with high and low temps."""
    api_key = get_api_key()
    location = get_location()

    if location is None:
        lat, lon = 42.3601, -71.0589
    else:
        lat, lon = location["lat"], location["lon"]

    data = fetch_forecast(lat, lon, api_key)
    entries = data.get("list", [])

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # First pass: group every 3-hour slot by day to find true daily high/low
    day_data = {}   # day_str -> {"temps": [...], "icon": str}
    for entry in entries:
        dt_txt = entry.get("dt_txt", "")
        day_str = dt_txt[:10]
        hour    = dt_txt[11:13]

        if day_str == today_str:
            continue  # skip today

        temp = entry["main"]["temp"]
        icon = entry["weather"][0]["icon"]

        if day_str not in day_data:
            day_data[day_str] = {"temps": [], "icon": icon}

        day_data[day_str]["temps"].append(temp)

        # Use the noon icon as the representative icon for the day
        if hour == "12":
            day_data[day_str]["icon"] = icon

    # Second pass: build the sorted forecast list
    forecast = []
    for day_str in sorted(day_data.keys())[:4]:
        temps  = day_data[day_str]["temps"]
        dt_obj = datetime.strptime(day_str, "%Y-%m-%d")
        forecast.append({
            "day":      dt_obj.strftime("%a"),      # "Mon", "Tue", …
            "temp_high": round(max(temps)),
            "temp_low":  round(min(temps)),
            "icon":      day_data[day_str]["icon"],
        })

    return forecast

if __name__ == "__main__":
    print(get_weather())
    print(get_forecast())
