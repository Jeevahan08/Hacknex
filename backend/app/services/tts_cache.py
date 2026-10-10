import hashlib
from typing import Dict, Optional

class TTSCache:
    def __init__(self, max_items: int = 200):
        self._cache: Dict[str, bytes] = {}
        self.max_items = max_items

    def _make_key(self, text: str, language: str, speaker: str) -> str:
        raw = f"{language}:{speaker}:{text.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, text: str, language: str, speaker: str) -> Optional[bytes]:
        key = self._make_key(text, language, speaker)
        return self._cache.get(key)

    def set(self, text: str, language: str, speaker: str, audio_bytes: bytes):
        if len(self._cache) >= self.max_items:
            # Pop first item (FIFO)
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        key = self._make_key(text, language, speaker)
        self._cache[key] = audio_bytes

tts_cache = TTSCache()
