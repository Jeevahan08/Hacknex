import asyncio
import json
import time
import struct
import math
from typing import AsyncGenerator, Dict, Optional
import httpx
from app.config import settings
from app.utils.logging import logger
from app.ai.base.base_stt import BaseSTTProvider, STTEvent
from app.ai.providers.sarvam.client import sarvam_client

def pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 16000) -> bytes:
    """Wraps linear 16-bit 16kHz PCM audio bytes in a standard 44-byte WAV header."""
    byte_rate = sample_rate * 2
    block_align = 2
    chunk_size = 36 + len(pcm_bytes)
    hdr = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', chunk_size, b'WAVE',
        b'fmt ', 16, 1, 1, sample_rate, byte_rate, block_align, 16,
        b'data', len(pcm_bytes)
    )
    return bytes(hdr + pcm_bytes)

class SarvamSTTProvider(BaseSTTProvider):
    """
    Sarvam Saaras v4 Streaming Speech Recognition Provider.
    Buffers incoming linear PCM audio chunks and performs streaming transcription
    via Sarvam Saaras v4 STT API.

    CRITICAL FIX: Buffer is cleared after each snapshot to prevent re-transcribing
    old audio on every subsequent call.
    """

    def __init__(self):
        self.client = sarvam_client
        self._active_sessions: Dict[str, Dict] = {}

    async def start_stream(
        self,
        session_id: str,
        source_language: str = "en-IN",
        sample_rate: int = 16000
    ) -> None:
        queue: asyncio.Queue = asyncio.Queue()
        self._active_sessions[session_id] = {
            "source_language": source_language,
            "sample_rate": sample_rate,
            "queue": queue,
            "audio_buffer": bytearray(),
            "total_bytes_received": 0,
            "last_speech_time": time.time(),
            "last_transcribe_time": 0.0,
            "is_speaking": False,
            "closed": False,
            "is_real": self.client.is_configured(),
            "audio_chunks_received": 0,
            "transcriptions_done": 0,
            "last_partial_text": ""
        }
        logger.info(
            f"[WS] session started: session_id={session_id} "
            f"source_language={source_language} real_api={self.client.is_configured()}"
        )

    async def send_audio_chunk(self, session_id: str, audio_bytes: bytes) -> None:
        session = self._active_sessions.get(session_id)
        if not session or session["closed"]:
            return

        session["audio_buffer"].extend(audio_bytes)
        session["audio_chunks_received"] = session.get("audio_chunks_received", 0) + 1
        session["total_bytes_received"] = session.get("total_bytes_received", 0) + len(audio_bytes)
        now = time.time()

        # Voice Activity Detection: compute RMS energy from 16-bit PCM audio samples
        sample_count = len(audio_bytes) // 2
        if sample_count > 0:
            try:
                shorts = struct.unpack(f"<{sample_count}h", audio_bytes[:sample_count * 2])
                sum_sq = sum(s * s for s in shorts)
                rms = math.sqrt(sum_sq / sample_count)
                # RMS threshold for voiced speech
                if rms > 280:
                    session["last_speech_time"] = now
                    session["is_speaking"] = True
            except Exception:
                pass

        buffer_len = len(session["audio_buffer"])
        time_since_speech = now - session["last_speech_time"]
        time_since_transcribe = now - session.get("last_transcribe_time", 0.0)

        # 1. Endpoint / silence detection for sentence boundary:
        # User spoke at least ~1.0s of audio and has paused for >= 850ms
        has_min_audio = buffer_len >= 32000
        silence_pause = (time_since_speech >= 0.85) and session.get("is_speaking", False) and has_min_audio

        if silence_pause:
            session["is_speaking"] = False
            session["last_transcribe_time"] = now
            snapshot = bytes(session["audio_buffer"])
            # Clear buffer for the next sentence utterance while keeping the session open
            session["audio_buffer"].clear()

            if settings.DEBUG_TRANSLATION:
                logger.info(
                    f"[STT] silence pause detected ({time_since_speech:.2f}s) — committing sentence: "
                    f"session={session_id} size={len(snapshot)} bytes"
                )

            if session.get("is_real"):
                asyncio.create_task(
                    self._transcribe_pcm_chunk(
                        session_id, snapshot, session["source_language"], is_final=True
                    )
                )
            return

        # 2. Interim partial transcription:
        # Transcribe accumulated audio so far without clearing buffer, keeping context intact
        # Minimum ~1.0s of audio and at least 1.0s since last partial request
        if buffer_len >= 32000 and time_since_transcribe >= 1.0:
            session["last_transcribe_time"] = now
            snapshot = bytes(session["audio_buffer"])

            if session.get("is_real"):
                asyncio.create_task(
                    self._transcribe_pcm_chunk(
                        session_id, snapshot, session["source_language"], is_final=False
                    )
                )

        # 3. Maximum segment safety flush (e.g. 15 seconds without a pause)
        if buffer_len >= 480000:
            session["is_speaking"] = False
            session["last_transcribe_time"] = now
            snapshot = bytes(session["audio_buffer"])
            session["audio_buffer"].clear()
            if session.get("is_real"):
                asyncio.create_task(
                    self._transcribe_pcm_chunk(
                        session_id, snapshot, session["source_language"], is_final=True
                    )
                )

    async def flush_and_finalize(self, session_id: str) -> None:
        session = self._active_sessions.get(session_id)
        if not session or not session.get("audio_buffer"):
            return
        snapshot = bytes(session["audio_buffer"])
        session["audio_buffer"].clear()
        logger.info(f"[STT] flush_and_finalize: session={session_id} size={len(snapshot)} bytes")
        if len(snapshot) >= 4000 and session.get("is_real"):
            await self._transcribe_pcm_chunk(
                session_id, snapshot, session["source_language"], is_final=True
            )

    async def _transcribe_pcm_chunk(
        self,
        session_id: str,
        pcm_bytes: bytes,
        source_language: str,
        is_final: bool = False
    ):
        if len(pcm_bytes) < 4000:
            logger.debug(f"[STT] chunk too small ({len(pcm_bytes)} bytes), skipping")
            return

        try:
            # Map auto/unknown source language to official Sarvam Saaras 'unknown'
            stt_lang = "unknown" if source_language.lower() in ("auto", "unknown", "auto detect", "auto-detect") else source_language

            wav_bytes = pcm_to_wav(pcm_bytes)
            headers = {"api-subscription-key": self.client.api_key}
            files = {"file": ("audio.wav", wav_bytes, "audio/wav")}
            data = {
                "model": settings.SARVAM_STT_MODEL,
                "language_code": stt_lang
            }
            logger.info(
                f"[STT] POST speech-to-text: model={settings.SARVAM_STT_MODEL} "
                f"language={stt_lang} wav_size={len(wav_bytes)} bytes is_final={is_final}"
            )
            async with httpx.AsyncClient(timeout=settings.STT_READ_TIMEOUT) as client:
                res = await client.post(
                    "https://api.sarvam.ai/speech-to-text",
                    headers=headers,
                    files=files,
                    data=data
                )
                if res.status_code == 200:
                    body = res.json()
                    transcript = body.get("transcript", "").strip()
                    detected_lang = body.get("language_code", source_language)
                    logger.info(
                        f"[STT] transcript received: '{transcript}' "
                        f"language={detected_lang} is_final={is_final}"
                    )
                    if transcript:
                        evt = STTEvent(
                            event="final" if is_final else "partial",
                            text=transcript,
                            language=detected_lang,
                            confidence=0.95,
                            timestamp=time.time()
                        )
                        session = self._active_sessions.get(session_id)
                        if session and not session["closed"]:
                            session["transcriptions_done"] = session.get("transcriptions_done", 0) + 1
                            session["last_partial_text"] = transcript
                            await session["queue"].put(evt)
                else:
                    logger.error(
                        f"[STT] Sarvam STT error: status={res.status_code} "
                        f"body={res.text[:300]}"
                    )
        except Exception as exc:
            logger.warning(f"[STT] Sarvam speech-to-text chunk transcription error: {exc}")

    async def transcribe_file(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language_code: str = "en-IN"
    ) -> Dict:
        """Transcribe an audio file using Sarvam Saaras v4 STT."""
        if settings.is_demo or not self.client.is_configured():
            return {
                "transcript": "Hello, this is a demonstration transcription from IndicLive Saaras v4.",
                "language_code": language_code,
                "model": settings.SARVAM_STT_MODEL,
                "confidence": 0.98
            }

        headers = {"api-subscription-key": self.client.api_key}
        files = {"file": (filename, audio_bytes, "audio/wav")}
        data = {
            "model": settings.SARVAM_STT_MODEL,
            "language_code": language_code
        }
        async with httpx.AsyncClient(timeout=settings.STT_READ_TIMEOUT) as client:
            res = await client.post(
                "https://api.sarvam.ai/speech-to-text",
                headers=headers,
                files=files,
                data=data
            )
            if res.status_code == 200:
                result = res.json()
                result["model"] = settings.SARVAM_STT_MODEL
                return result
            else:
                logger.error(f"Sarvam Saaras v4 STT failed status={res.status_code}: {res.text}")
                from app.ai.errors import IndicLiveError
                raise IndicLiveError(
                    "STT_ERROR",
                    f"Saaras v4 transcription failed ({res.status_code}): {res.text}"
                )

    async def emit_direct_transcript(
        self,
        session_id: str,
        text: str,
        is_final: bool = False,
        language: str = "en-IN"
    ):
        """Direct transcript input from client speech recognition or WebSocket stream."""
        session = self._active_sessions.get(session_id)
        if not session or session["closed"]:
            return

        logger.info(
            f"[STT] direct transcript: '{text[:80]}' is_final={is_final} language={language}"
        )
        evt = STTEvent(
            event="final" if is_final else "partial",
            text=text.strip(),
            language=language or session["source_language"],
            confidence=0.96 if is_final else 0.88,
            timestamp=time.time()
        )
        await session["queue"].put(evt)

    async def emit_demo_transcript(
        self,
        session_id: str,
        sentence: str,
        delay_between_words: float = 0.25
    ):
        """Emits realistic progressive interim partials followed by a final commit."""
        session = self._active_sessions.get(session_id)
        if not session:
            return

        queue = session["queue"]
        words = sentence.split()
        accumulated = []

        for i, word in enumerate(words):
            accumulated.append(word)
            partial_text = " ".join(accumulated)
            is_last = (i == len(words) - 1)
            event_type = "final" if is_last else "partial"

            evt = STTEvent(
                event=event_type,
                text=partial_text,
                language=session["source_language"],
                confidence=0.88 if not is_last else 0.96,
                timestamp=time.time()
            )
            await queue.put(evt)
            if not is_last:
                await asyncio.sleep(delay_between_words)

    async def receive_events(self, session_id: str) -> AsyncGenerator[STTEvent, None]:
        session = self._active_sessions.get(session_id)
        if not session:
            return

        queue: asyncio.Queue = session["queue"]
        while not session["closed"]:
            try:
                evt = await asyncio.wait_for(queue.get(), timeout=0.5)
                yield evt
            except asyncio.TimeoutError:
                continue

    async def close_stream(self, session_id: str) -> None:
        session = self._active_sessions.pop(session_id, None)
        if session:
            session["closed"] = True
            logger.info(
                f"[WS] session closed: session_id={session_id} "
                f"chunks={session.get('audio_chunks_received', 0)} "
                f"transcriptions={session.get('transcriptions_done', 0)}"
            )

sarvam_stt_provider = SarvamSTTProvider()
