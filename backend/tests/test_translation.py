import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_parallel_translation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "source_language": "en-IN",
            "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
            "text": "Good morning everyone.",
            "mode": "fast"
        }
        resp = await client.post("/api/v1/translate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "translations" in data
        assert "ta-IN" in data["translations"]
        assert "hi-IN" in data["translations"]
        assert "ml-IN" in data["translations"]
        assert len(data["translations"]["ta-IN"]["translated_text"]) > 0

@pytest.mark.asyncio
async def test_entity_protection_in_translation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "source_language": "en-IN",
            "target_languages": ["ta-IN", "hi-IN"],
            "text": "The train leaves at 10:30 AM.",
            "mode": "balanced"
        }
        resp = await client.post("/api/v1/translate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # Verify 10:30 is preserved
        ta_text = data["translations"]["ta-IN"]["translated_text"]
        assert "10:30" in ta_text
