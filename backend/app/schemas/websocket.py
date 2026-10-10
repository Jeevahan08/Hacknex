from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

# Client to Server Messages
class WSSessionStart(BaseModel):
    type: str = "session.start"
    source_language: str = "en-IN"
    target_languages: List[str] = ["ta-IN", "hi-IN", "ml-IN"]
    enable_tts: bool = False
    mode: str = "fast"  # fast, balanced, quality
    sample_rate: int = 16000

class WSAudioChunk(BaseModel):
    type: str = "audio.chunk"
    data: str  # Base64-encoded audio chunk
    timestamp: Optional[float] = None

class WSSessionStop(BaseModel):
    type: str = "session.stop"

class WSDemoTrigger(BaseModel):
    type: str = "demo.trigger"
    sentence: Optional[str] = None
    delay_ms: int = 400

# Server to Client Messages
class WSEvent(BaseModel):
    type: str
    session_id: Optional[str] = None
    timestamp: Optional[float] = None
    data: Optional[Dict[str, Any]] = None

class WSTranscriptPartial(BaseModel):
    type: str = "transcript.partial"
    text: str
    language: str = "en-IN"
    confidence: float = 0.90
    timestamp: float

class WSTranscriptCommitted(BaseModel):
    type: str = "transcript.committed"
    text: str
    language: str = "en-IN"
    segment_id: str
    confidence: float = 0.95
    timestamp: float

class WSTranslationPartial(BaseModel):
    type: str = "translation.partial"
    segment_id: str
    target_language: str
    text: str
    status: str = "partial"
    latency_ms: int = 0

class WSTranslationFinal(BaseModel):
    type: str = "translation.final"
    segment_id: str
    target_language: str
    text: str
    status: str = "final"
    first_word_latency_ms: int = 0
    final_latency_ms: int = 0
    stability_score: float = 0.95
    rewrites: int = 0

class WSPipelineStage(BaseModel):
    type: str = "pipeline.stage"
    stage: str  # "mic", "listening", "transcribing", "commit", "translating", "final"
    details: Optional[str] = None

class WSError(BaseModel):
    type: str = "error"
    code: str
    message: str
    retryable: bool = False
