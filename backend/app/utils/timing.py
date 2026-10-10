import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class LatencyTracker(BaseModel):
    session_id: str
    segment_id: str
    audio_received_at: float = Field(default_factory=time.time)
    stt_partial_at: Optional[float] = None
    stt_commit_at: Optional[float] = None
    translation_start_at: Optional[float] = None
    translation_first_token_at: Optional[float] = None
    translation_final_at: Optional[float] = None
    tts_start_at: Optional[float] = None
    tts_first_audio_at: Optional[float] = None

    def mark_stt_partial(self):
        if not self.stt_partial_at:
            self.stt_partial_at = time.time()

    def mark_stt_commit(self):
        self.stt_commit_at = time.time()

    def mark_translation_start(self):
        self.translation_start_at = time.time()

    def mark_translation_first_token(self):
        if not self.translation_first_token_at:
            self.translation_first_token_at = time.time()

    def mark_translation_final(self):
        self.translation_final_at = time.time()

    def mark_tts_start(self):
        self.tts_start_at = time.time()

    def mark_tts_first_audio(self):
        self.tts_first_audio_at = time.time()

    @property
    def stt_latency_ms(self) -> int:
        if self.stt_commit_at:
            return int((self.stt_commit_at - self.audio_received_at) * 1000)
        if self.stt_partial_at:
            return int((self.stt_partial_at - self.audio_received_at) * 1000)
        return 0

    @property
    def first_word_latency_ms(self) -> int:
        ts = self.translation_first_token_at or self.translation_final_at
        if ts:
            return int((ts - self.audio_received_at) * 1000)
        return 0

    @property
    def final_latency_ms(self) -> int:
        if self.translation_final_at:
            return int((self.translation_final_at - self.audio_received_at) * 1000)
        return 0

    @property
    def tts_latency_ms(self) -> int:
        if self.tts_first_audio_at and self.tts_start_at:
            return int((self.tts_first_audio_at - self.tts_start_at) * 1000)
        return 0

    def to_metrics_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "segment_id": self.segment_id,
            "stt_latency_ms": self.stt_latency_ms,
            "first_word_latency_ms": self.first_word_latency_ms,
            "final_latency_ms": self.final_latency_ms,
            "tts_latency_ms": self.tts_latency_ms,
            "timestamp": time.time()
        }
