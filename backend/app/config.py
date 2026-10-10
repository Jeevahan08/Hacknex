import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # API Keys & Providers
    SARVAM_API_KEY: str = Field(default="", description="Sarvam AI API key")
    
    # Model Registry Identifiers
    SARVAM_STT_MODEL: str = "saaras:v4"
    SARVAM_TRANSLATION_MODEL: str = "sarvam-translate:v1"
    SARVAM_LLM_MODEL: str = "sarvam-105b"
    SARVAM_CONVERSATIONAL_MODEL: str = "sarvam-105b-conversations"
    SARVAM_TTS_MODEL: str = "bulbul:v3"

    # Runtime Modes
    DEMO_MODE: bool = True
    LLM_ENABLED: bool = False
    LLM_MODE: str = "balanced"  # fast, balanced, quality
    ENABLE_TTS: bool = False
    ENABLE_AUTO_LANGUAGE_DETECTION: bool = True

    # Language Defaults
    DEFAULT_SOURCE_LANGUAGE: str = "en-IN"
    DEFAULT_TARGET_LANGUAGES: str = "ta-IN,hi-IN,ml-IN,mr-IN"

    # Commit Policy & Streaming Intelligence
    MIN_TRANSLATION_TOKENS: int = 3
    MAX_PARTIAL_WAIT_MS: int = 1200
    SILENCE_COMMIT_MS: int = 850
    STABILITY_THRESHOLD: float = 0.80

    # Debug & Telemetry
    DEBUG_TRANSLATION: bool = True

    # Context & Intelligence
    MAX_CONTEXT_SEGMENTS: int = 5
    MAX_LLM_CALLS_PER_SEGMENT: int = 1

    # Timeouts (in seconds)
    STT_CONNECT_TIMEOUT: float = 8.0
    STT_READ_TIMEOUT: float = 5.0
    TRANSLATION_TIMEOUT: float = 5.0
    LLM_TIMEOUT: float = 4.0
    TTS_TIMEOUT: float = 8.0

    # Storage & Networking
    DATABASE_URL: str = "sqlite+aiosqlite:///./indiclive.db"
    FRONTEND_URL: str = "http://localhost:5173"
    LOG_LEVEL: str = "INFO"

    @computed_field
    @property
    def target_languages_list(self) -> List[str]:
        return [lang.strip() for lang in self.DEFAULT_TARGET_LANGUAGES.split(",") if lang.strip()]

    @computed_field
    @property
    def is_demo(self) -> bool:
        # If no real API key is set, automatically enable DEMO_MODE safely
        if not self.SARVAM_API_KEY or self.SARVAM_API_KEY.strip() == "" or "YOUR_" in self.SARVAM_API_KEY:
            return True
        return self.DEMO_MODE

settings = Settings()
