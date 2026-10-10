from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class TranslateRequest(BaseModel):
    source_language: str = Field(default="en-IN", description="BCP-47 language code")
    target_languages: List[str] = Field(default=["ta-IN", "hi-IN", "ml-IN"], description="List of target language codes")
    text: str = Field(..., description="Text to translate")
    mode: str = Field(default="fast", description="Processing mode: fast, balanced, quality")
    enable_glossary: bool = True
    session_id: Optional[str] = None
    segment_id: Optional[str] = None

class TargetTranslation(BaseModel):
    language: str
    translated_text: str
    status: str = "final"  # partial, committed, final
    latency_ms: int = 0
    confidence: float = 0.95

class TranslateResponse(BaseModel):
    source_language: str
    text: str
    segment_id: str
    translations: Dict[str, TargetTranslation]
    pipeline_mode: str = "fast"
    total_latency_ms: int = 0

class TTSRequest(BaseModel):
    text: str
    language: str = "ta-IN"
    speaker: Optional[str] = "ananya"
    pace: float = 1.0
    pitch: float = 0.0

class TTSResponse(BaseModel):
    audio_base64: str
    format: str = "audio/wav"
    language: str
    cached: bool = False
    duration_ms: int = 0
