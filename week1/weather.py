import requests
import os
"""Week 1 deliverable: fetch and print current weather for your city.

Goal: run `python weather.py` and see the current temperature and conditions
printed to the terminal. This is a throwaway learning script — keep it simple.

Fill in the TODOs yourself. Pointers are given, not answers.
"""

# TODO: import the library you'll use to make the web request.
#       (Look up: "python requests library get")

from dotenv import load_dotenv
load_dotenv()

def get_api_key():
    """Gets API key from the .env file"""
    api_key = os.environ.get("WEATHER_API_KEY")
    return api_key


def fetch_weather(lat: float, lon: float, api_key, units="metric"):
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
    """Pull the temperature and conditions out of the response and print them.

    The API returns a nested dictionary. Your job is to figure out which keys
    hold the temperature and the text description, then print them nicely.

    Look up:
      - how to inspect a dict you don't know the shape of (print it, or use
        the API docs' example response)
      - dictionary indexing vs. .get()

    Args:
        data (dict): the parsed response from fetch_weather().
    """
    # TODO: extract temp + conditions from `data` and print them.
    raise NotImplementedError


def main():
    """Tie it together: get key -> fetch -> print."""
    # TODO: set your city, call the functions above in order.
    raise NotImplementedError


if __name__ == "__main__":
    api_key = get_api_key()
    print(api_key)                             
    data = fetch_weather(42.3601, -71.0589, api_key)  # Boston coords need to change later to be dynamic
    print(data)


