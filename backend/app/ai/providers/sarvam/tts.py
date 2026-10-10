import base64
import math
import struct
from typing import Optional
from app.config import settings
from app.utils.logging import logger
from app.ai.base.base_tts import BaseTTSProvider
from app.ai.providers.sarvam.client import sarvam_client
from app.services.tts_cache import tts_cache

class SarvamTTSProvider(BaseTTSProvider):
    def __init__(self):
        self.client = sarvam_client

    async def synthesize(
        self,
        text: str,
        language: str = "ta-IN",
        speaker: Optional[str] = "priya",
        pace: float = 1.0,
        pitch: float = 0.0
    ) -> bytes:
        clean_text = text.strip()
        if not clean_text:
            return b""

        # Compatible speakers for bulbul:v3 include priya, roopa, kavya, aditya, rahul
        speaker_name = speaker if speaker and speaker != "ananya" else "priya"

        # Check cache
        cached = tts_cache.get(clean_text, language, speaker_name)
        if cached:
            return cached

        # Check if in Demo mode or client unconfigured
        if settings.is_demo or not self.client.is_configured():
            audio_bytes = self._generate_synthetic_tone(duration_sec=0.8)
            tts_cache.set(clean_text, language, speaker_name, audio_bytes)
            return audio_bytes

        try:
            payload = {
                "inputs": [clean_text],
                "target_language_code": language,
                "speaker": speaker_name,
                "pace": max(0.5, min(2.0, pace)),
                "model": settings.SARVAM_TTS_MODEL
            }
            res = await self.client.post("/text-to-speech", payload, timeout=settings.TTS_TIMEOUT)
            audios = res.get("audios", [])
            if audios:
                audio_bytes = base64.b64decode(audios[0])
                tts_cache.set(clean_text, language, speaker_name, audio_bytes)
                return audio_bytes
        except Exception as exc:
            logger.warning(f"Sarvam TTS failed ({exc}); falling back to synthetic audio tone.")

        fallback = self._generate_synthetic_tone(duration_sec=0.8)
        tts_cache.set(clean_text, language, speaker_name, fallback)
        return fallback

    def _generate_synthetic_tone(self, duration_sec: float = 0.8, sample_rate: int = 16000) -> bytes:
        """Generates a valid 16kHz PCM WAV audio chime for browser playback."""
        num_samples = int(sample_rate * duration_sec)
        raw_samples = bytearray()
        freq = 440.0  # A4 note
        for i in range(num_samples):
            # Soft envelope decay
            envelope = math.exp(-3.0 * (i / num_samples))
            val = int(32767 * 0.4 * envelope * math.sin(2 * math.pi * freq * (i / sample_rate)))
            raw_samples.extend(struct.pack("<h", val))

        byte_rate = sample_rate * 2
        block_align = 2
        subchunk2_size = len(raw_samples)
        chunk_size = 36 + subchunk2_size

        wav_header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", chunk_size, b"WAVE",
            b"fmt ", 16, 1, 1, sample_rate, byte_rate, block_align, 16,
            b"data", subchunk2_size
        )
        return bytes(wav_header + raw_samples)

sarvam_tts_provider = SarvamTTSProvider()
