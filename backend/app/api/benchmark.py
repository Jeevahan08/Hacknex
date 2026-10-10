from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.repositories import MetricRepository
from app.schemas.benchmark import BenchmarkRunRequest, BenchmarkRunResponse
from app.services.benchmark_service import benchmark_service

router = APIRouter()

@router.get("/benchmark", response_model=BenchmarkRunResponse)
async def get_benchmark_baseline():
    return await benchmark_service.run_benchmark()

@router.post("/benchmark/run", response_model=BenchmarkRunResponse)
async def run_benchmark(req: BenchmarkRunRequest):
    return await benchmark_service.run_benchmark(
        source_language=req.source_language,
        target_languages=req.target_languages,
        mode=req.mode
    )

@router.get("/metrics/{session_id}")
async def get_session_metrics(session_id: str, db: AsyncSession = Depends(get_db)):
    repo = MetricRepository(db)
    records = await repo.get_session_metrics(session_id)
    return {
        "session_id": session_id,
        "metrics": [
            {
                "segment_id": r.segment_id,
                "stt_latency_ms": r.stt_latency_ms,
                "first_word_latency_ms": r.first_word_latency_ms,
                "final_latency_ms": r.final_latency_ms,
                "stability_score": r.stability_score,
                "rewrites": r.rewrites,
                "timestamp": r.timestamp
            }
            for r in records
        ]
    }
