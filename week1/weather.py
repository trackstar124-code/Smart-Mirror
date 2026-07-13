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


def print_weather(data):
    """prints the weather data for Boston"""
    temp = data["main"]["temp"]
    city = data["name"]

    print(f"{city}: {temp}°F")


def main():
    """Runs all the function above in order to give an output"""
    api_key = get_api_key()                           
    data = fetch_weather(42.3601, -71.0589, api_key)  # Boston coords need to change later to be dynamic
    print_weather(data)

if __name__ == "__main__":
    main()
