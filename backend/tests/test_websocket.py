import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_connection_and_session():
    client = TestClient(app)
    with client.websocket_connect("/ws/v1/live/test_session_123") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "session.started"
        assert data["session_id"] == "test_session_123"

        # Start session
        websocket.send_json({
            "type": "session.start",
            "source_language": "en-IN",
            "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
            "enable_tts": False,
            "mode": "fast"
        })
        
        stage_event = websocket.receive_json()
        assert stage_event["type"] == "pipeline.stage"
        assert stage_event["stage"] == "mic"
