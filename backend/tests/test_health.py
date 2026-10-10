import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "backend" in data

@pytest.mark.asyncio
async def test_languages_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/languages")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["languages"]) >= 4
        codes = [l["code"] for l in data["languages"]]
        assert "en-IN" in codes
        assert "ta-IN" in codes
        assert "hi-IN" in codes
        assert "ml-IN" in codes

@pytest.mark.asyncio
async def test_models_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "stt" in data
        assert "translation" in data
        assert data["stt"]["model"] == "saaras:v4"
