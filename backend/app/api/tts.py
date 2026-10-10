import base64
import time
from fastapi import APIRouter
from app.schemas.translation import TTSRequest, TTSResponse
from app.ai.providers.sarvam.tts import sarvam_tts_provider
from app.services.tts_cache import tts_cache

router = APIRouter()

@router.post("/tts", response_model=TTSResponse)
async def synthesize_speech(req: TTSRequest):
    start_t = time.time()
    cached = tts_cache.get(req.text, req.language, req.speaker or "ananya")
    is_cached = cached is not None

    audio_bytes = await sarvam_tts_provider.synthesize(
        text=req.text,
        language=req.language,
        speaker=req.speaker,
        pace=req.pace,
        pitch=req.pitch
    )

    duration_ms = int((time.time() - start_t) * 1000)
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else ""

    return TTSResponse(
        audio_base64=audio_base64,
        format="audio/wav",
        language=req.language,
        cached=is_cached,
        duration_ms=duration_ms
    )
