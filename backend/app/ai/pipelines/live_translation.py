import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.logging import logger
from app.utils.timing import LatencyTracker
from app.ai.base.base_stt import STTEvent
from app.ai.providers.sarvam.stt import sarvam_stt_provider
from app.ai.providers.sarvam.translation import sarvam_translation_provider
from app.ai.providers.sarvam.tts import sarvam_tts_provider
from app.ai.intelligence.commit_policy import IntelligentCommitPolicy
from app.ai.intelligence.stability import CaptionStabilityEngine
from app.ai.intelligence.llm_router import llm_router
from app.ai.intelligence.entity_protection import entity_protection_engine
from app.ai.intelligence.code_mix import code_mix_handler
from app.ai.intelligence.glossary import glossary_engine

class LiveTranslationPipelineSession:
    def __init__(
        self,
        session_id: str,
        source_language: str = "en-IN",
        target_languages: Optional[List[str]] = None,
        enable_tts: bool = False,
        mode: str = "fast",
        ws_send_callback = None
    ):
        self.session_id = session_id
        self.source_language = source_language
        self.target_languages = target_languages or ["ta-IN", "hi-IN", "ml-IN"]
        self.enable_tts = enable_tts
        self.mode = mode
        self.ws_send = ws_send_callback

        self.commit_policy = IntelligentCommitPolicy()
        self.stability_engine = CaptionStabilityEngine()
        self.current_segment_id = f"seg_{uuid.uuid4().hex[:8]}"
        self.latency_tracker = LatencyTracker(session_id=session_id, segment_id=self.current_segment_id)
        self.is_active = True
        self.last_audio_time = time.time()
        self.recent_history: List[str] = []

    async def emit_pipeline_stage(self, stage: str, details: Optional[str] = None):
        if self.ws_send:
            await self.ws_send({
                "type": "pipeline.stage",
                "stage": stage,
                "details": details
            })

    async def on_audio_chunk(self, audio_bytes: bytes):
        self.last_audio_time = time.time()
        self.latency_tracker.audio_received_at = self.last_audio_time
        await self.emit_pipeline_stage("listening")
        await sarvam_stt_provider.send_audio_chunk(self.session_id, audio_bytes)

    async def handle_stt_event(self, evt: STTEvent):
        if not self.is_active:
            return

        text = evt.text.strip()
        if not text:
            return

        await self.emit_pipeline_stage("transcribing")
        is_speech_final = (evt.event == "final")

        if settings.DEBUG_TRANSLATION:
            logger.info(
                f"[STT] event received: event={evt.event} text='{text}' "
                f"language={evt.language} confidence={evt.confidence:.2f}"
            )

        # Intelligent Commit Policy Evaluation
        decision = self.commit_policy.evaluate(text, is_speech_final=is_speech_final)

        if decision.is_final_commit:
            self.latency_tracker.mark_stt_commit()
            self.stability_engine.on_committed(text)
            self.recent_history.append(text)
            if len(self.recent_history) > settings.MAX_CONTEXT_SEGMENTS:
                self.recent_history.pop(0)

            logger.info(
                f"[STT] segment committed: '{text}' reason={decision.reason} "
                f"segment_id={self.current_segment_id}"
            )

            # Broadcast committed transcript
            if self.ws_send:
                await self.ws_send({
                    "type": "transcript.committed",
                    "text": text,
                    "language": evt.language,
                    "segment_id": self.current_segment_id,
                    "confidence": evt.confidence,
                    "timestamp": evt.timestamp
                })

            # Reset commit policy for the next segment so it evaluates fresh
            self.commit_policy.reset()

        else:
            self.latency_tracker.mark_stt_partial()
            self.stability_engine.on_partial(text)

            # Broadcast partial transcript
            if self.ws_send:
                await self.ws_send({
                    "type": "transcript.partial",
                    "text": text,
                    "language": evt.language,
                    "confidence": evt.confidence,
                    "timestamp": evt.timestamp
                })

        # Check if text is safe / ready to translate according to commit policy
        if decision.should_translate:
            logger.info(
                f"[STT] segment commit: reason={decision.reason} "
                f"source={self.source_language} targets={self.target_languages}"
            )
            await self.emit_pipeline_stage("commit", details=decision.reason)
            await self._run_parallel_translations(text, is_final=decision.is_final_commit)

    async def _run_parallel_translations(self, text: str, is_final: bool):
        await self.emit_pipeline_stage("translating")
        self.latency_tracker.mark_translation_start()

        if settings.DEBUG_TRANSLATION:
            logger.info(
                f"[TRANSLATE] starting parallel translation:"
                f" source={self.source_language} targets={self.target_languages}"
                f" is_final={is_final}"
                f" source_text='{text}'"
            )

        # Step 1: Pre-translation entity protection / Sarvam-105B context check
        processed_text = text
        placeholders = {}
        if self.mode in ("balanced", "quality"):
            if is_final:
                try:
                    llm_analysis = await llm_router.process_pre_translation(self.mode, text, self.recent_history)
                    if llm_analysis and self.ws_send:
                        await self.ws_send({
                            "type": "llm.context",
                            "model": settings.SARVAM_LLM_MODEL,
                            "code_mixed_terms": llm_analysis.code_mixed_terms,
                            "ambiguity": llm_analysis.ambiguity,
                            "entities_count": len(llm_analysis.entities)
                        })
                except Exception as e:
                    logger.warning(f"Sarvam-105B context routing notice: {e}")

            processed_text, placeholders = entity_protection_engine.protect_and_mask(text)

        # Step 2: Parallel Translation using asyncio.gather across all target languages!
        start_t = time.time()
        translations_dict = await sarvam_translation_provider.translate_parallel(
            source_language=self.source_language,
            target_languages=self.target_languages,
            text=processed_text
        )
        self.latency_tracker.mark_translation_first_token()
        if is_final:
            self.latency_tracker.mark_translation_final()

        # Step 3: Post-processing and unmasking
        final_translations = {}
        for tgt_lang, translated_text in translations_dict.items():
            unmasked = entity_protection_engine.unmask(translated_text, placeholders)
            # Apply glossary post with source context
            unmasked = glossary_engine.apply_post(unmasked, tgt_lang, source_text=text)
            final_translations[tgt_lang] = unmasked
            if settings.DEBUG_TRANSLATION:
                logger.info(
                    f"[TRANSLATE] result: {self.source_language} → {tgt_lang}"
                    f" translated='{unmasked}' is_final={is_final}"
                )

        # Step 3b: Sarvam-105B Quality verification in quality mode
        if self.mode == "quality" and is_final and settings.LLM_ENABLED:
            try:
                primary_target = self.target_languages[0]
                primary_trans = final_translations.get(primary_target, "")
                if primary_trans and not primary_trans.startswith("[TRANSLATION ERROR"):
                    q_res = await llm_router.process_post_translation(
                        self.mode, text, primary_target, primary_trans
                    )
                    if q_res and self.ws_send:
                        await self.ws_send({
                            "type": "llm.quality",
                            "model": settings.SARVAM_LLM_MODEL,
                            "target_language": primary_target,
                            "score": q_res.fluency_score,
                            "meaning_preserved": q_res.meaning_preserved
                        })
            except Exception as e:
                logger.warning(f"Sarvam-105B quality check notice: {e}")

        first_word_ms = self.latency_tracker.first_word_latency_ms
        final_ms = self.latency_tracker.final_latency_ms
        stability = self.stability_engine.stability_score
        rewrites = self.stability_engine.late_rewrites

        # Step 4: Dispatch translations to Frontend Live Translation Lanes
        # CRITICAL: translated_text is the TARGET language output.
        # source text (text) must NEVER be sent as the translation value.
        any_failed = False
        for tgt_lang, translated_text in final_translations.items():
            is_error = translated_text.startswith("[TRANSLATION ERROR") or translated_text.startswith("[Translation unavailable")
            if is_error:
                any_failed = True
            trans_status = "failed" if is_error else ("final" if is_final else "partial")
            msg_type = ("translation.failed" if is_error else "translation.final") if is_final else "translation.partial"

            if self.ws_send:
                await self.ws_send({
                    "type": msg_type,
                    "segment_id": self.current_segment_id,
                    "source_language": self.source_language,
                    "source_text": text,
                    "target_language": tgt_lang,
                    "text": translated_text,
                    "status": trans_status,
                    "error": translated_text if is_error else None,
                    "first_word_latency_ms": first_word_ms,
                    "final_latency_ms": final_ms,
                    "stability_score": stability,
                    "rewrites": rewrites
                })

        # Step 5: Optional TTS if configured and final
        if is_final:
            if any_failed:
                await self.emit_pipeline_stage("translation_failed", details="Translation failed for one or more targets")
            else:
                await self.emit_pipeline_stage("final")

            if self.enable_tts and not any_failed:
                primary_target = self.target_languages[0]
                primary_text = final_translations.get(primary_target, "")
                if primary_text and not primary_text.startswith("[TRANSLATION"):
                    await self.emit_pipeline_stage("generating_speech")
                    self.latency_tracker.mark_tts_start()
                    try:
                        audio_bytes = await sarvam_tts_provider.synthesize(primary_text, primary_target)
                        self.latency_tracker.mark_tts_first_audio()
                        if audio_bytes and self.ws_send:
                            import base64
                            await self.ws_send({
                                "type": "tts.audio",
                                "segment_id": self.current_segment_id,
                                "target_language": primary_target,
                                "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
                                "format": "audio/wav"
                            })
                    except Exception as tts_err:
                        logger.error(f"[TTS] Voice generation failed: {tts_err}")
                        await self.emit_pipeline_stage("voice_failed", details=str(tts_err))
                        if self.ws_send:
                            await self.ws_send({
                                "type": "tts.failed",
                                "segment_id": self.current_segment_id,
                                "target_language": primary_target,
                                "error": str(tts_err)
                            })

            # Create a new segment ID for the upcoming sentence
            self.current_segment_id = f"seg_{uuid.uuid4().hex[:8]}"
            self.latency_tracker = LatencyTracker(session_id=self.session_id, segment_id=self.current_segment_id)

    async def close(self):
        self.is_active = False
        await sarvam_stt_provider.close_stream(self.session_id)
