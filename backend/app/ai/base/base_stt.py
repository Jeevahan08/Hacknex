from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional
from pydantic import BaseModel

class STTEvent(BaseModel):
    event: str  # "partial" or "final"
    text: str
    language: str = "en-IN"
    confidence: float = 0.90
    timestamp: float

class BaseSTTProvider(ABC):
    @abstractmethod
    async def start_stream(
        self,
        session_id: str,
        source_language: str = "en-IN",
        sample_rate: int = 16000
    ) -> None:
        pass

    @abstractmethod
    async def send_audio_chunk(self, session_id: str, audio_bytes: bytes) -> None:
        pass

    @abstractmethod
    async def receive_events(self, session_id: str) -> AsyncGenerator[STTEvent, None]:
        pass

    @abstractmethod
    async def close_stream(self, session_id: str) -> None:
        pass
