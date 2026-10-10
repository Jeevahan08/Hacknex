import json
import base64
import asyncio
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.logging import logger
from app.ai.pipelines.live_translation import LiveTranslationPipelineSession
from app.ai.providers.sarvam.stt import sarvam_stt_provider

router = APIRouter()

active_pipelines: Dict[str, LiveTranslationPipelineSession] = {}

async def _handle_live_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket client connected for session={session_id}")

    pipeline_session: LiveTranslationPipelineSession = None
    stt_listener_task = None

    async def ws_send_json(data: dict):
        try:
            await websocket.send_json(data)
        except Exception:
            pass

    try:
        # Send initial confirmation
        await ws_send_json({
            "type": "session.started",
            "session_id": session_id
        })

        async for message in websocket.iter_text():
            try:
                msg = json.loads(message)
                msg_type = msg.get("type", "")

                if msg_type == "session.start":
                    source_lang = msg.get("source_language", "en-IN")
                    target_langs = msg.get("target_languages", ["ta-IN", "hi-IN", "ml-IN"])
                    enable_tts = msg.get("enable_tts", False)
                    mode = msg.get("mode", "fast")

                    if pipeline_session:
                        await pipeline_session.close()

                    pipeline_session = LiveTranslationPipelineSession(
                        session_id=session_id,
                        source_language=source_lang,
                        target_languages=target_langs,
                        enable_tts=enable_tts,
                        mode=mode,
                        ws_send_callback=ws_send_json
                    )
                    active_pipelines[session_id] = pipeline_session

                    # Initialize STT stream
                    await sarvam_stt_provider.start_stream(
                        session_id=session_id,
                        source_language=source_lang
                    )

                    # Spawn STT event consumer loop
                    async def consume_stt():
                        async for evt in sarvam_stt_provider.receive_events(session_id):
                            if pipeline_session:
                                await pipeline_session.handle_stt_event(evt)

                    if stt_listener_task:
                        stt_listener_task.cancel()
                    stt_listener_task = asyncio.create_task(consume_stt())

                    await ws_send_json({
                        "type": "pipeline.stage",
                        "stage": "mic",
                        "details": f"Pipeline ready: {source_lang} -> {', '.join(target_langs)}"
                    })

                elif msg_type == "audio.chunk":
                    data_b64 = msg.get("data", "")
                    if data_b64 and pipeline_session:
                        try:
                            audio_bytes = base64.b64decode(data_b64)
                            await pipeline_session.on_audio_chunk(audio_bytes)
                        except Exception as exc:
                            logger.error(f"Error decoding audio chunk: {exc}")

                elif msg_type == "demo.trigger":
                    # Instant test trigger for demo mode
                    sentence = msg.get("sentence", "Good morning everyone, today we are going to discuss artificial intelligence.")
                    delay_ms = msg.get("delay_ms", 300)
                    if pipeline_session:
                        asyncio.create_task(
                            sarvam_stt_provider.emit_demo_transcript(
                                session_id,
                                sentence,
                                delay_between_words=delay_ms / 1000.0
                            )
                        )

                elif msg_type == "transcript.stream":
                    text = msg.get("text", "")
                    is_final = msg.get("is_final", False)
                    lang = msg.get("language", "en-IN")
                    if text and pipeline_session:
                        await sarvam_stt_provider.emit_direct_transcript(
                            session_id, text, is_final=is_final, language=lang
                        )

                elif msg_type == "session.stop":
                    await sarvam_stt_provider.flush_and_finalize(session_id)
                    if pipeline_session:
                        await pipeline_session.close()
                    await ws_send_json({"type": "session.stopped", "session_id": session_id})

            except json.JSONDecodeError:
                await ws_send_json({"type": "error", "code": "INVALID_JSON", "message": "Failed to parse JSON"})
            except Exception as exc:
                logger.error(f"Error in websocket loop: {exc}")
                await ws_send_json({"type": "error", "code": "SERVER_ERROR", "message": str(exc)})

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for session={session_id}")
    finally:
        if stt_listener_task:
            stt_listener_task.cancel()
        if pipeline_session:
            await pipeline_session.close()
        active_pipelines.pop(session_id, None)

@router.websocket("/ws/v1/live/{session_id}")
async def websocket_live_v1(websocket: WebSocket, session_id: str):
    await _handle_live_ws(websocket, session_id)

@router.websocket("/ws/translation/{session_id}")
async def websocket_translation(websocket: WebSocket, session_id: str):
    await _handle_live_ws(websocket, session_id)
