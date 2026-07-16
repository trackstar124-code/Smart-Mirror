import requests
import os

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

if __name__ == "__main__":
    print(get_weather())
