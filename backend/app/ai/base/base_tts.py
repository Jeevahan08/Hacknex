from abc import ABC, abstractmethod
from typing import Optional

class BaseTTSProvider(ABC):
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        language: str = "ta-IN",
        speaker: Optional[str] = "ananya",
        pace: float = 1.0,
        pitch: float = 0.0
    ) -> bytes:
        pass
