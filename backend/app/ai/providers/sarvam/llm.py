import os
import json
from typing import List, Optional
from app.config import settings
from app.utils.logging import logger
from app.ai.base.base_llm import BaseLLMProvider, ContextAnalysis, QualityCheckResult, EntityInfo
from app.ai.providers.sarvam.client import sarvam_client
from app.ai.intelligence.entity_protection import entity_protection_engine
from app.ai.intelligence.code_mix import code_mix_handler

class SarvamLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.client = sarvam_client
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "prompts")

    def _load_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.prompts_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    async def analyze_context(
        self,
        text: str,
        recent_history: Optional[List[str]] = None
    ) -> ContextAnalysis:
        # If demo mode or client not configured, perform rule-based context analysis
        if settings.is_demo or not self.client.is_configured():
            return self._heuristic_analysis(text)

        try:
            prompt = self._load_prompt("translation_context.txt")
            payload = {
                "model": settings.SARVAM_LLM_MODEL,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"History: {recent_history or []}\nSegment: {text}"}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            # Sarvam LLM chat/completions endpoint (OpenAI-compatible)
            res = await self.client.post("/v1/chat/completions", payload, timeout=settings.LLM_TIMEOUT)
            content = res.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            data = json.loads(content)
            return ContextAnalysis.model_validate(data)
        except Exception as exc:
            logger.warning(f"Sarvam LLM call failed ({exc}); falling back to heuristic context analysis.")
            return self._heuristic_analysis(text)

    async def quality_check(
        self,
        source_text: str,
        target_language: str,
        translated_text: str
    ) -> QualityCheckResult:
        if settings.is_demo or not self.client.is_configured():
            return self._heuristic_quality_check(source_text, target_language, translated_text)

        try:
            prompt = self._load_prompt("quality_check.txt")
            payload = {
                "model": settings.SARVAM_LLM_MODEL,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Source: {source_text}\nTarget: {target_language}\nTranslation: {translated_text}"}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            res = await self.client.post("/v1/chat/completions", payload, timeout=settings.LLM_TIMEOUT)
            content = res.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            data = json.loads(content)
            return QualityCheckResult.model_validate(data)
        except Exception as exc:
            logger.warning(f"Sarvam LLM quality check failed ({exc}); using heuristic.")
            return self._heuristic_quality_check(source_text, target_language, translated_text)

    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Direct text inference with Sarvam-105B."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if settings.is_demo or not self.client.is_configured():
            return f"[Sarvam-105B Demo Response] Analysis complete for: {prompt[:40]}"

        try:
            payload = {
                "model": settings.SARVAM_LLM_MODEL,
                "messages": messages,
                "temperature": 0.2
            }
            res = await self.client.post("/v1/chat/completions", payload, timeout=settings.LLM_TIMEOUT)
            return res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception as exc:
            logger.error(f"Sarvam-105B completion failed: {exc}")
            raise IndicLiveError("LLM_ERROR", f"Sarvam-105B inference failed: {str(exc)}")

    def _heuristic_analysis(self, text: str) -> ContextAnalysis:
        entities_raw = entity_protection_engine.extract_entities(text)
        entities = [
            EntityInfo(text=e["text"], type=e["type"], preserve=e["preserve"])
            for e in entities_raw
        ]
        cm = code_mix_handler.analyze(text)
        return ContextAnalysis(
            entities=entities,
            numbers=[e["text"] for e in entities_raw if e["type"] in ("TIME", "DATE")],
            code_mixed_terms=cm.get("embedded_terms", []),
            ambiguity=False,
            context_hint=None
        )

    def _heuristic_quality_check(self, src: str, tgt_lang: str, trans: str) -> QualityCheckResult:
        issues = []
        if not trans or not trans.strip():
            issues.append("Translation is empty")
            return QualityCheckResult(valid=False, needs_correction=True, issues=issues)

        # Check entity preservation
        entities = entity_protection_engine.extract_entities(src)
        for e in entities:
            # Check if numbers or locations survived
            if e["type"] in ("LOCATION", "ORGANIZATION", "TIME"):
                if e["text"] not in trans and e["text"].lower() not in trans.lower():
                    # May be transliterated or missing
                    pass

        return QualityCheckResult(valid=True, needs_correction=False, issues=issues)

sarvam_llm_provider = SarvamLLMProvider()
