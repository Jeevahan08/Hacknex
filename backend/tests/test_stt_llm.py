import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_stt_info():
    response = client.get("/api/v1/stt/info")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "saaras:v4"
    assert data["provider"] == "sarvam"
    assert "en-IN" in data["supported_languages"]

def test_llm_info():
    response = client.get("/api/v1/llm/info")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "sarvam-105b"
    assert data["provider"] == "sarvam"

def test_llm_complete_api():
    response = client.post("/api/v1/llm/complete", json={
        "prompt": "Hello world"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "sarvam-105b"
    assert len(data["content"]) > 0

def test_llm_analyze_api():
    response = client.post("/api/v1/llm/analyze", json={
        "text": "Tomorrow at 5 PM in Bengaluru."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "sarvam-105b"
    assert "entities" in data
