import time
import uuid
from fastapi import APIRouter
from app.schemas.translation import TranslateRequest, TranslateResponse, TargetTranslation
from app.ai.providers.sarvam.translation import sarvam_translation_provider
from app.ai.intelligence.entity_protection import entity_protection_engine
from app.ai.intelligence.llm_router import llm_router

router = APIRouter()

from app.ai.intelligence.glossary import glossary_engine

@router.post("/translate", response_model=TranslateResponse)
async def translate_text(req: TranslateRequest):
    start_time = time.time()
    segment_id = req.segment_id or f"seg_{uuid.uuid4().hex[:8]}"

    # Entity protection and pre-masking
    processed_text, placeholders = entity_protection_engine.protect_and_mask(req.text)

    # Parallel translation across requested targets using asyncio.gather
    raw_translations = await sarvam_translation_provider.translate_parallel(
        source_language=req.source_language,
        target_languages=req.target_languages,
        text=processed_text
    )

    total_latency = int((time.time() - start_time) * 1000)
    target_results = {}

    for tgt_lang, translated_text in raw_translations.items():
        unmasked = entity_protection_engine.unmask(translated_text, placeholders)
        unmasked = glossary_engine.apply_post(unmasked, tgt_lang, source_text=req.text)
        is_error = unmasked.startswith("[TRANSLATION ERROR") or unmasked.startswith("[Translation unavailable")
        target_results[tgt_lang] = TargetTranslation(
            language=tgt_lang,
            translated_text=unmasked,
            status="failed" if is_error else "final",
            latency_ms=total_latency,
            confidence=0.0 if is_error else 0.96
        )

    return TranslateResponse(
        source_language=req.source_language,
        text=req.text,
        segment_id=segment_id,
        translations=target_results,
        pipeline_mode=req.mode,
        total_latency_ms=total_latency
    )

@router.post("/llm/quality-check")
async def quality_check(source_text: str, target_language: str, translated_text: str):
    res = await llm_router.process_post_translation(
        mode="quality",
        source_text=source_text,
        target_language=target_language,
        translated_text=translated_text
    )
    if res:
        return res.model_dump()
    return {"valid": True, "needs_correction": False, "issues": []}
