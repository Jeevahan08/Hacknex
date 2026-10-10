import time
from fastapi import APIRouter
from app.config import settings
from app.ai.providers.sarvam.client import sarvam_client
from app.ai.registry import get_models_status

router = APIRouter()

@router.get("/health")
async def health_check():
    configured = sarvam_client.is_configured()
    return {
        "status": "healthy",
        "demo_mode": settings.is_demo,
        "backend": "connected",
        "database": "connected",
        "provider": "sarvam" if configured else "demo_mock_provider",
        "provider_connected": configured or settings.is_demo,
        "timestamp": time.time()
    }

@router.get("/models")
async def models_status():
    return get_models_status()

@router.get("/config")
async def get_config():
    return {
        "demo_mode": settings.is_demo,
        "default_source_language": settings.DEFAULT_SOURCE_LANGUAGE,
        "default_target_languages": settings.target_languages_list,
        "min_translation_tokens": settings.MIN_TRANSLATION_TOKENS,
        "max_partial_wait_ms": settings.MAX_PARTIAL_WAIT_MS,
        "silence_commit_ms": settings.SILENCE_COMMIT_MS,
        "stability_threshold": settings.STABILITY_THRESHOLD,
        "llm_enabled": settings.LLM_ENABLED,
        "llm_mode": settings.LLM_MODE,
        "enable_tts": settings.ENABLE_TTS,
        "models": {
            "stt": settings.SARVAM_STT_MODEL,
            "translation": settings.SARVAM_TRANSLATION_MODEL,
            "llm": settings.SARVAM_LLM_MODEL,
            "tts": settings.SARVAM_TTS_MODEL
        }
    }
