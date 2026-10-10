from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        pass
