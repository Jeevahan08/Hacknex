from typing import Dict, Any
from app.config import settings
from app.ai.providers.sarvam.client import sarvam_client

MODEL_REGISTRY = {
    "stt": {
        "provider": "sarvam",
        "model": settings.SARVAM_STT_MODEL,
        "purpose": "realtime_speech_recognition",
        "supported_languages": ["en-IN", "ta-IN", "hi-IN", "ml-IN", "mr-IN", "te-IN", "kn-IN", "bn-IN", "gu-IN", "pa-IN", "od-IN"],
        "streaming": True,
        "latency_class": "ultra_low"
    },
    "translation": {
        "provider": "sarvam",
        "model": settings.SARVAM_TRANSLATION_MODEL,
        "purpose": "primary_translation",
        "supported_languages": ["en-IN", "ta-IN", "hi-IN", "ml-IN", "mr-IN", "te-IN", "kn-IN", "bn-IN", "gu-IN", "pa-IN", "od-IN"],
        "streaming": False,
        "parallel_execution": True,
        "latency_class": "low"
    },
    "llm": {
        "provider": "sarvam",
        "model": settings.SARVAM_LLM_MODEL,
        "purpose": "optional_context_postprocessing",
        "enabled": settings.LLM_ENABLED,
        "latency_class": "medium"
    },
    "conversational_llm": {
        "provider": "sarvam",
        "model": settings.SARVAM_CONVERSATIONAL_MODEL,
        "purpose": "optional_conversational_processing",
        "latency_class": "medium"
    },
    "tts": {
        "provider": "sarvam",
        "model": settings.SARVAM_TTS_MODEL,
        "purpose": "translated_speech",
        "enabled": settings.ENABLE_TTS,
        "latency_class": "low"
    }
}

def get_models_status() -> Dict[str, Any]:
    configured = sarvam_client.is_configured()
    status_label = "ready" if (configured or settings.is_demo) else "unconfigured"
    
    return {
        "stt": {
            "provider": "sarvam",
            "model": settings.SARVAM_STT_MODEL,
            "status": status_label,
            "demo_fallback": settings.is_demo
        },
        "translation": {
            "provider": "sarvam",
            "model": settings.SARVAM_TRANSLATION_MODEL,
            "status": status_label,
            "demo_fallback": settings.is_demo
        },
        "llm": {
            "provider": "sarvam",
            "model": settings.SARVAM_LLM_MODEL,
            "status": status_label if settings.LLM_ENABLED else "disabled",
            "mode": settings.LLM_MODE
        },
        "tts": {
            "provider": "sarvam",
            "model": settings.SARVAM_TTS_MODEL,
            "status": status_label if settings.ENABLE_TTS else "disabled",
            "voices": ["ananya", "aravind", "priya"]
        }
    }
