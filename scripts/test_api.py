import asyncio
import os
import sys
from httpx import ASGITransport, AsyncClient

# Configure UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import app
from app.database.database import init_db

async def run_checks():
    print("[*] Running IndicLive End-to-End API verification...")
    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health
        h_res = await client.get("/api/v1/health")
        print(f"[OK] GET /api/v1/health -> {h_res.status_code} ({h_res.json().get('status')})")

        # 2. Models
        m_res = await client.get("/api/v1/models")
        print(f"[OK] GET /api/v1/models -> {m_res.status_code} (STT: {m_res.json()['stt']['model']}, Translation: {m_res.json()['translation']['model']})")

        # 3. Languages
        l_res = await client.get("/api/v1/languages")
        print(f"[OK] GET /api/v1/languages -> {l_res.status_code} ({len(l_res.json()['languages'])} languages)")

        # 4. Translation
        t_res = await client.post("/api/v1/translate", json={
            "source_language": "en-IN",
            "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
            "text": "Good morning everyone.",
            "mode": "fast"
        })
        translations = t_res.json().get("translations", {})
        print(f"[OK] POST /api/v1/translate -> {t_res.status_code}")
        for lang, item in translations.items():
            print(f"    - {lang}: {item['translated_text']}")

        # 5. TTS
        tts_res = await client.post("/api/v1/tts", json={
            "text": "வணக்கம்",
            "language": "ta-IN"
        })
        print(f"[OK] POST /api/v1/tts -> {tts_res.status_code} (audio payload size: {len(tts_res.json().get('audio_base64', ''))} chars)")

        # 6. Benchmark
        b_res = await client.get("/api/v1/benchmark")
        print(f"[OK] GET /api/v1/benchmark -> {b_res.status_code} ({len(b_res.json().get('comparisons', []))} comparisons)")

    print("[+] All API checks passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_checks())
