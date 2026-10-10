from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.ai.providers.sarvam.llm import sarvam_llm_provider

router = APIRouter()

class LLMAnalyzeRequest(BaseModel):
    text: str
    history: Optional[List[str]] = None

class LLMQualityRequest(BaseModel):
    source_text: str
    target_language: str
    translated_text: str

class LLMCompleteRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None

@router.get("/llm/info")
async def get_llm_info():
    """Information about active Sarvam-105B LLM model."""
    return {
        "model": settings.SARVAM_LLM_MODEL,
        "conversational_model": settings.SARVAM_CONVERSATIONAL_MODEL,
        "provider": "sarvam",
        "enabled": settings.LLM_ENABLED,
        "mode": settings.LLM_MODE,
        "purposes": [
            "Context disambiguation",
            "Code-mix script resolution (Hinglish/Tanglish)",
            "Entity protection",
            "Translation quality scoring"
        ]
    }

@router.post("/llm/analyze")
async def analyze_context_segment(payload: LLMAnalyzeRequest):
    """
    Analyze speech context and extract entities using Sarvam-105B LLM.
    """
    try:
        analysis = await sarvam_llm_provider.analyze_context(payload.text, payload.history)
        return {
            "model": settings.SARVAM_LLM_MODEL,
            "entities": [e.model_dump() for e in analysis.entities],
            "numbers": analysis.numbers,
            "code_mixed_terms": analysis.code_mixed_terms,
            "ambiguity": analysis.ambiguity,
            "context_hint": analysis.context_hint
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/llm/quality")
async def check_translation_quality(payload: LLMQualityRequest):
    """
    Evaluate translation quality and fluency using Sarvam-105B LLM.
    """
    try:
        result = await sarvam_llm_provider.quality_check(
            source_text=payload.source_text,
            target_language=payload.target_language,
            translated_text=payload.translated_text
        )
        return {
            "model": settings.SARVAM_LLM_MODEL,
            "fluency_score": result.fluency_score,
            "meaning_preserved": result.meaning_preserved,
            "notes": result.notes
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/llm/complete")
async def complete_text(payload: LLMCompleteRequest):
    """
    Direct prompt inference against Sarvam-105B Foundation Model.
    """
    try:
        response_text = await sarvam_llm_provider.complete(
            prompt=payload.prompt,
            system_prompt=payload.system_prompt
        )
        return {
            "model": settings.SARVAM_LLM_MODEL,
            "content": response_text
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
