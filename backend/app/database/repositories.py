import json
import time
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import (
    SessionRecord,
    SegmentRecord,
    TranslationRecord,
    MetricRecord,
    GlossaryRecord,
    BenchmarkRecord
)

class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, session_id: str, source_lang: str, target_langs: List[str], mode: str) -> SessionRecord:
        record = SessionRecord(
            id=session_id,
            source_language=source_lang,
            target_languages=",".join(target_langs),
            mode=mode,
            created_at=time.time(),
            status="active"
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_session(self, session_id: str) -> Optional[SessionRecord]:
        result = await self.db.execute(select(SessionRecord).where(SessionRecord.id == session_id))
        return result.scalar_one_or_none()

    async def end_session(self, session_id: str) -> Optional[SessionRecord]:
        session = await self.get_session(session_id)
        if session:
            session.ended_at = time.time()
            session.status = "ended"
            await self.db.commit()
            await self.db.refresh(session)
        return session

    async def list_recent_sessions(self, limit: int = 10) -> List[SessionRecord]:
        result = await self.db.execute(
            select(SessionRecord).order_by(SessionRecord.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

class GlossaryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_terms(self) -> List[GlossaryRecord]:
        result = await self.db.execute(select(GlossaryRecord).order_by(GlossaryRecord.term))
        return list(result.scalars().all())

    async def add_term(self, term: str, action: str = "preserve", replacement: Optional[str] = None, target_lang: Optional[str] = None) -> GlossaryRecord:
        # Check if already exists
        existing = await self.db.execute(select(GlossaryRecord).where(GlossaryRecord.term == term))
        item = existing.scalar_one_or_none()
        if item:
            item.action = action
            item.replacement = replacement
            item.target_language = target_lang
        else:
            item = GlossaryRecord(
                term=term,
                action=action,
                replacement=replacement,
                target_language=target_lang,
                created_at=time.time()
            )
            self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_term(self, term_id: int) -> bool:
        result = await self.db.execute(delete(GlossaryRecord).where(GlossaryRecord.id == term_id))
        await self.db.commit()
        return result.rowcount > 0

class MetricRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_metric(self, session_id: str, segment_id: str, stt_ms: int, first_word_ms: int, final_ms: int, stability: float, rewrites: int):
        record = MetricRecord(
            session_id=session_id,
            segment_id=segment_id,
            stt_latency_ms=stt_ms,
            first_word_latency_ms=first_word_ms,
            final_latency_ms=final_ms,
            stability_score=stability,
            rewrites=rewrites,
            timestamp=time.time()
        )
        self.db.add(record)
        await self.db.commit()

    async def get_session_metrics(self, session_id: str) -> List[MetricRecord]:
        result = await self.db.execute(
            select(MetricRecord).where(MetricRecord.session_id == session_id).order_by(MetricRecord.timestamp.asc())
        )
        return list(result.scalars().all())

class BenchmarkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_benchmark(self, run_id: str, results: Dict[str, Any]):
        record = BenchmarkRecord(
            id=run_id,
            timestamp=time.time(),
            results_json=json.dumps(results)
        )
        self.db.add(record)
        await self.db.commit()

    async def get_latest_benchmarks(self, limit: int = 5) -> List[BenchmarkRecord]:
        result = await self.db.execute(
            select(BenchmarkRecord).order_by(BenchmarkRecord.timestamp.desc()).limit(limit)
        )
        return list(result.scalars().all())
