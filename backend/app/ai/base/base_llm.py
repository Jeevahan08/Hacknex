from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class EntityInfo(BaseModel):
    text: str
    type: str  # LOCATION, PERSON, ORGANIZATION, NUMBER, DATE, TECHNICAL_TERM
    preserve: bool = True

class ContextAnalysis(BaseModel):
    entities: List[EntityInfo] = []
    numbers: List[str] = []
    code_mixed_terms: List[str] = []
    ambiguity: bool = False
    context_hint: Optional[str] = None

class QualityCheckResult(BaseModel):
    valid: bool = True
    needs_correction: bool = False
    issues: List[str] = []
    corrected_text: Optional[str] = None

class BaseLLMProvider(ABC):
    @abstractmethod
    async def analyze_context(
        self,
        text: str,
        recent_history: Optional[List[str]] = None
    ) -> ContextAnalysis:
        pass

    @abstractmethod
    async def quality_check(
        self,
        source_text: str,
        target_language: str,
        translated_text: str
    ) -> QualityCheckResult:
        pass
