from unittest.mock import mock_open
from modules.events import get_events

def test_get_events(monkeypatch):
    dummy_data = [{"date": "10/31", "title": "Halloween"}]
    
    # Mock json.load to return dummy data instead of reading from file
    def mock_json_load(f):
        return dummy_data
        
    monkeypatch.setattr("modules.events.json.load", mock_json_load)
    
    # Mock builtins.open so it doesn't crash trying to open a non-existent file
    monkeypatch.setattr("builtins.open", mock_open())
    
    result = get_events()
    assert result == dummy_data
