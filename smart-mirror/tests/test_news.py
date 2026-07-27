from unittest.mock import Mock
from modules.news import get_news

def test_get_news_success(monkeypatch):
    monkeypatch.setenv("NYT_API_KEY", "fake_key")
    
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {"title": "Headline 1", "url": "http://link1"},
            {"title": "Headline 2", "url": "http://link2"},
        ]
    }
    mock_response.raise_for_status.return_value = None
    
    monkeypatch.setattr("modules.news.requests.get", lambda url, params, timeout: mock_response)
    
    result = get_news()
    assert len(result) == 2
    assert result[0]["title"] == "Headline 1"
    assert result[0]["url"] == "http://link1"

def test_get_news_no_key(monkeypatch):
    # Test that we return empty list if API key is missing
    monkeypatch.delenv("NYT_API_KEY", raising=False)
    assert get_news() == []

def test_get_news_missing_title(monkeypatch):
    monkeypatch.setenv("NYT_API_KEY", "fake_key")
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {"title": "Valid Headline", "url": "http://valid"},
            {"url": "http://no-title"},  # missing title
        ]
    }
    mock_response.raise_for_status.return_value = None
    monkeypatch.setattr("modules.news.requests.get", lambda url, params, timeout: mock_response)
    result = get_news()
    assert len(result) == 1
    assert result[0]["title"] == "Valid Headline"

def test_get_news_limit_ten(monkeypatch):
    monkeypatch.setenv("NYT_API_KEY", "fake_key")
    # generate 15 dummy articles
    articles = [{"title": f"Headline {i}", "url": f"http://link{i}"} for i in range(15)]
    mock_response = Mock()
    mock_response.json.return_value = {"results": articles}
    mock_response.raise_for_status.return_value = None
    monkeypatch.setattr("modules.news.requests.get", lambda url, params, timeout: mock_response)
    result = get_news()
    assert len(result) == 10
    assert result[0]["title"] == "Headline 0"
    assert result[-1]["title"] == "Headline 9"

def test_get_news_network_error(monkeypatch):
    monkeypatch.setenv("NYT_API_KEY", "fake_key")
    
    import requests
    def mock_get(*args, **kwargs):
        raise requests.RequestException("Network error")
        
    monkeypatch.setattr("modules.news.requests.get", mock_get)
    
    assert get_news() == []
