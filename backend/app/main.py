from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.utils.logging import logger
from app.database.database import init_db
from app.ai.errors import IndicLiveError

# Routers
from app.api.health import router as health_router
from app.api.languages import router as languages_router
from app.api.translation import router as translation_router
from app.api.tts import router as tts_router
from app.api.glossary import router as glossary_router
from app.api.benchmark import router as benchmark_router
from app.api.sessions import router as sessions_router
from app.api.stt import router as stt_router
from app.api.llm import router as llm_router
from app.api.websocket import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing IndicLive backend database...")
    await init_db()
    logger.info(f"IndicLive initialized in {'DEMO' if settings.is_demo else 'PRODUCTION'} mode.")
    yield
    logger.info("IndicLive backend shutting down.")

app = FastAPI(
    title="IndicLive — Real-Time Indic Language Translation Intelligence Platform",
    description="Real-time speech translation intelligence platform for Indian languages powered by Sarvam AI.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(IndicLiveError)
async def indiclive_error_handler(request: Request, exc: IndicLiveError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable
            }
        }
    )

# Include v1 routes
app.include_router(health_router, prefix="/api/v1", tags=["Health & Models"])
app.include_router(languages_router, prefix="/api/v1", tags=["Languages"])
app.include_router(translation_router, prefix="/api/v1", tags=["Translation"])
app.include_router(tts_router, prefix="/api/v1", tags=["TTS"])
app.include_router(glossary_router, prefix="/api/v1", tags=["Glossary"])
app.include_router(benchmark_router, prefix="/api/v1", tags=["Benchmark"])
app.include_router(sessions_router, prefix="/api/v1", tags=["Sessions"])
app.include_router(stt_router, prefix="/api/v1", tags=["Speech Recognition (Saaras v4)"])
app.include_router(llm_router, prefix="/api/v1", tags=["Intelligence LLM (Sarvam-105B)"])

# Also include top-level /api aliases for direct route compatibility
app.include_router(health_router, prefix="/api", tags=["API Aliases"])
app.include_router(languages_router, prefix="/api", tags=["API Aliases"])
app.include_router(translation_router, prefix="/api", tags=["API Aliases"])
app.include_router(tts_router, prefix="/api", tags=["API Aliases"])
app.include_router(glossary_router, prefix="/api", tags=["API Aliases"])
app.include_router(benchmark_router, prefix="/api", tags=["API Aliases"])
app.include_router(sessions_router, prefix="/api", tags=["API Aliases"])
app.include_router(stt_router, prefix="/api", tags=["API Aliases"])
app.include_router(llm_router, prefix="/api", tags=["API Aliases"])

# WebSocket routes
app.include_router(ws_router, tags=["WebSocket Live Streaming"])

@app.get("/")
async def root():
    return {
        "project": "IndicLive",
        "tagline": "Speak Naturally. Understand Instantly.",
        "status": "online",
        "docs": "/docs",
        "demo_mode": settings.is_demo
    }
