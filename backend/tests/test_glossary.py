import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_glossary_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List terms
        resp = await client.get("/api/v1/glossary")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

        # Add term
        payload = {
            "term": "Antigravity AI",
            "action": "preserve"
        }
        add_resp = await client.post("/api/v1/glossary", json=payload)
        assert add_resp.status_code == 200
        new_item = add_resp.json()
        assert new_item["term"] == "Antigravity AI"

        # Delete term
        if new_item.get("id"):
            del_resp = await client.delete(f"/api/v1/glossary/{new_item['id']}")
            assert del_resp.status_code == 200
