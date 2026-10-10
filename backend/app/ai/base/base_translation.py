from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class BaseTranslationProvider(ABC):
    @abstractmethod
    async def translate(
        self,
        source_language: str,
        target_language: str,
        text: str,
        context: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None
    ) -> str:
        pass

    @abstractmethod
    async def translate_parallel(
        self,
        source_language: str,
        target_languages: List[str],
        text: str,
        context: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        pass
