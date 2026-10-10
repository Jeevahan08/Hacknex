class IndicLiveError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = False):
        self.code = code
        self.message = message
        self.retryable = retryable
        super().__init__(f"[{code}] {message}")

class InvalidAPIKey(IndicLiveError):
    def __init__(self, message: str = "Invalid or missing Sarvam API key."):
        super().__init__("INVALID_API_KEY", message, retryable=False)

class RateLimitError(IndicLiveError):
    def __init__(self, message: str = "Provider rate limit exceeded. Please retry shortly."):
        super().__init__("RATE_LIMIT_EXCEEDED", message, retryable=True)

class ProviderTimeout(IndicLiveError):
    def __init__(self, message: str = "Provider API request timed out."):
        super().__init__("PROVIDER_TIMEOUT", message, retryable=True)

class ProviderUnavailable(IndicLiveError):
    def __init__(self, message: str = "Translation or STT provider is currently unavailable."):
        super().__init__("PROVIDER_UNAVAILABLE", message, retryable=True)

class UnsupportedLanguage(IndicLiveError):
    def __init__(self, lang: str):
        super().__init__("UNSUPPORTED_LANGUAGE", f"Language '{lang}' is not supported by the provider.", retryable=False)
