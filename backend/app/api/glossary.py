from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.repositories import GlossaryRepository
from app.schemas.glossary import GlossaryCreate, GlossaryItem, GlossaryResponse

router = APIRouter()

@router.get("/glossary", response_model=GlossaryResponse)
async def list_glossary(db: AsyncSession = Depends(get_db)):
    repo = GlossaryRepository(db)
    records = await repo.list_terms()
    items = [
        GlossaryItem(
            id=r.id,
            term=r.term,
            action=r.action,
            replacement=r.replacement,
            target_language=r.target_language
        )
        for r in records
    ]
    # If DB is empty, provide default demonstration terms
    if not items:
        defaults = [
            GlossaryItem(id=1, term="Chennai", action="preserve"),
            GlossaryItem(id=2, term="ISRO", action="preserve"),
            GlossaryItem(id=3, term="RailBlock AI", action="preserve"),
            GlossaryItem(id=4, term="Machine Learning", action="preferred", replacement="இயந்திர கற்றல்", target_language="ta-IN"),
            GlossaryItem(id=5, term="Indian Railways", action="preserve")
        ]
        return GlossaryResponse(items=defaults, total=len(defaults))

    return GlossaryResponse(items=items, total=len(items))

@router.post("/glossary", response_model=GlossaryItem)
async def add_glossary_term(data: GlossaryCreate, db: AsyncSession = Depends(get_db)):
    repo = GlossaryRepository(db)
    record = await repo.add_term(
        term=data.term,
        action=data.action,
        replacement=data.replacement,
        target_lang=data.target_language
    )
    return GlossaryItem(
        id=record.id,
        term=record.term,
        action=record.action,
        replacement=record.replacement,
        target_language=record.target_language
    )

@router.delete("/glossary/{term_id}")
async def delete_glossary_term(term_id: int, db: AsyncSession = Depends(get_db)):
    repo = GlossaryRepository(db)
    deleted = await repo.delete_term(term_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Glossary term not found")
    return {"status": "deleted", "id": term_id}
