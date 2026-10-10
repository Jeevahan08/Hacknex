import base64
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.ai.providers.sarvam.stt import sarvam_stt_provider

router = APIRouter()

class TranscribeJsonRequest(BaseModel):
    audio_base64: str
    language_code: Optional[str] = "en-IN"
    filename: Optional[str] = "audio.wav"

class TranscribeResponse(BaseModel):
    transcript: str
    language_code: str
    model: str
    request_id: Optional[str] = None

@router.get("/stt/info")
async def get_stt_info():
    """Information about active speech-to-text model."""
    return {
        "model": settings.SARVAM_STT_MODEL,
        "provider": "sarvam",
        "supported_languages": ["en-IN", "ta-IN", "hi-IN", "ml-IN", "te-IN", "kn-IN"],
        "streaming_supported": True,
        "audio_format": "16kHz 16-bit linear PCM or standard WAV"
    }

@router.post("/stt/transcribe", response_model=TranscribeResponse)
async def transcribe_audio_file(
    file: Optional[UploadFile] = File(None),
    language_code: str = Form("en-IN")
):
    """
    Transcribe uploaded audio file using Sarvam Saaras v4 STT model.
    Accepts WAV, MP3, or AAC audio recordings.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Audio file must be uploaded as multipart/form-data.")

    audio_bytes = await file.read()
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file is empty or too short.")

    try:
        res = await sarvam_stt_provider.transcribe_file(
            audio_bytes=audio_bytes,
            filename=file.filename or "recording.wav",
            language_code=language_code
        )
        return TranscribeResponse(
            transcript=res.get("transcript", "").strip(),
            language_code=res.get("language_code", language_code),
            model=settings.SARVAM_STT_MODEL,
            request_id=res.get("request_id")
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/stt/transcribe-base64", response_model=TranscribeResponse)
async def transcribe_base64_audio(payload: TranscribeJsonRequest):
    """
    Transcribe base64-encoded audio chunk using Sarvam Saaras v4 STT model.
    """
    try:
        audio_bytes = base64.b64decode(payload.audio_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio payload.")

    try:
        res = await sarvam_stt_provider.transcribe_file(
            audio_bytes=audio_bytes,
            filename=payload.filename or "recording.wav",
            language_code=payload.language_code or "en-IN"
        )
        return TranscribeResponse(
            transcript=res.get("transcript", "").strip(),
            language_code=res.get("language_code", payload.language_code or "en-IN"),
            model=settings.SARVAM_STT_MODEL,
            request_id=res.get("request_id")
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
