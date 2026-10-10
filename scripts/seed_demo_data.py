import asyncio
import json
import os
import sys

# Ensure backend app in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.database import init_db, AsyncSessionLocal
from app.database.repositories import GlossaryRepository, SessionRepository

async def seed():
    print("[*] Initializing IndicLive database...")
    await init_db()

    glossary_path = os.path.join(os.path.dirname(__file__), "..", "data", "glossary", "sample_glossary.json")
    if os.path.exists(glossary_path):
        with open(glossary_path, "r", encoding="utf-8") as f:
            terms = json.load(f)
        
        async with AsyncSessionLocal() as session:
            repo = GlossaryRepository(session)
            for item in terms:
                await repo.add_term(
                    term=item["term"],
                    action=item.get("action", "preserve"),
                    replacement=item.get("replacement"),
                    target_lang=item.get("target_language")
                )
            print(f"[+] Seeded {len(terms)} glossary terms into SQLite.")

    async with AsyncSessionLocal() as session:
        sess_repo = SessionRepository(session)
        await sess_repo.create_session(
            session_id="sess_demo_seed_001",
            source_lang="en-IN",
            target_langs=["ta-IN", "hi-IN", "ml-IN"],
            mode="fast"
        )
        print("[+] Created initial demonstration session: sess_demo_seed_001")

if __name__ == "__main__":
    asyncio.run(seed())
