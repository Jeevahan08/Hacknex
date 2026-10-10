import asyncio
from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.utils.logging import logger
from app.ai.errors import (
    InvalidAPIKey,
    RateLimitError,
    ProviderTimeout,
    ProviderUnavailable,
    IndicLiveError
)

class SarvamClient:
    BASE_URL = "https://api.sarvam.ai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.SARVAM_API_KEY
        self._headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("YOUR_"))

    async def post(self, endpoint: str, payload: Dict[str, Any], timeout: float = 8.0) -> Dict[str, Any]:
        if not self.is_configured():
            raise InvalidAPIKey("Sarvam API key is not configured or placeholder.")

        url = f"{self.BASE_URL}{endpoint}"
        retries = 3
        delay = 0.5

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(url, headers=self._headers, json=payload)
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code == 401 or resp.status_code == 403:
                        logger.error(f"Sarvam auth failed status={resp.status_code}")
                        raise InvalidAPIKey(f"Authentication failed with Sarvam API ({resp.status_code}). Check your SARVAM_API_KEY.")
                    elif resp.status_code == 429:
                        if attempt < retries - 1:
                            await asyncio.sleep(delay)
                            delay *= 2
                            continue
                        raise RateLimitError("Sarvam API rate limit exceeded.")
                    elif resp.status_code >= 500:
                        if attempt < retries - 1:
                            await asyncio.sleep(delay)
                            delay *= 2
                            continue
                        raise ProviderUnavailable(f"Sarvam service error {resp.status_code}.")
                    else:
                        raise IndicLiveError("API_ERROR", f"Sarvam API responded with status {resp.status_code}: {resp.text}")

            except httpx.TimeoutException:
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                raise ProviderTimeout("Sarvam request timed out.")
            except httpx.RequestError as exc:
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                raise ProviderUnavailable(f"Network error connecting to Sarvam API: {str(exc)}")

        raise ProviderUnavailable("Sarvam API retries exhausted.")

sarvam_client = SarvamClient()
