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
    api_key = os.environ.get("WEATHER_API_KEY")
    return api_key



def fetch_weather(city, api_key):
    """Call the weather API and return the raw response data.

    You'll make an HTTP GET request to your chosen API's "current weather"
    endpoint, passing the city and (if required) the API key.

    Look up:
      - your API's docs for the current-weather endpoint URL and its parameters
      - "requests.get params argument" (how to pass query parameters cleanly)
      - "response.json()" (turning the reply into a Python dict)

    Args:
        city (str): the city name to look up.
        api_key (str): your API key (may be unused for keyless APIs).

    Returns:
        dict: the parsed JSON response from the API.
    """
    # TODO: build the request, send it, and return response.json()
    raise NotImplementedError


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
    print(get_api_key())
