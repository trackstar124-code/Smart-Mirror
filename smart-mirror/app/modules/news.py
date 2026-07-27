from collections import abc
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_nyt_api_key():
    """Gets API key from the .env file"""
    api_key = os.environ.get("NYT_API_KEY")
    return api_key


def get_news():
    """Fetch top stories from NYT API."""
    api_key = get_nyt_api_key()
    if not api_key:
        print("NYT_API_KEY not found in environment.")
        return []

    url = "https://api.nytimes.com/svc/topstories/v2/home.json"
    params = {"api-key": api_key}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Extract top 10 articles
        articles = data.get("results", [])[:10]
        news_list = []
        for article in articles:
            if article.get("title"):
                news_list.append({
                    "title": article.get("title"),
                    "url": article.get("url")
                })
        return news_list
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

if __name__ == "__main__":
    print(get_news())
