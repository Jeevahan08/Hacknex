from typing import Optional, List
from app.config import settings
from app.ai.providers.sarvam.llm import sarvam_llm_provider
from app.ai.base.base_llm import ContextAnalysis, QualityCheckResult

class LLMRoutingEngine:
    async def process_pre_translation(
        self,
        mode: str,
        text: str,
        history: Optional[List[str]] = None
    ) -> Optional[ContextAnalysis]:
        if mode == "fast" or not settings.LLM_ENABLED:
            return None

        if mode == "balanced":
            # Only trigger if text contains mixed scripts or potential ambiguities
            analysis = await sarvam_llm_provider.analyze_context(text, history)
            if analysis.code_mixed_terms or analysis.ambiguity:
                return analysis
            return None

        if mode == "quality":
            return await sarvam_llm_provider.analyze_context(text, history)

        return None

    async def process_post_translation(
        self,
        mode: str,
        source_text: str,
        target_language: str,
        translated_text: str
    ) -> Optional[QualityCheckResult]:
        if mode != "quality" or not settings.LLM_ENABLED:
            return None

        return await sarvam_llm_provider.quality_check(source_text, target_language, translated_text)

llm_router = LLMRoutingEngine()
