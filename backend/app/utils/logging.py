import logging
import re
import sys

# Masking pattern for API keys
API_KEY_PATTERN = re.compile(r"(Bearer\s+|api[-_]?key[\"':\s=]+)([a-zA-Z0-9_\-]{8,})", re.IGNORECASE)

class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        orig = super().format(record)
        # Redact any key-like sequence
        return API_KEY_PATTERN.sub(r"\1***REDACTED***", orig)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(SafeFormatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger("indiclive")
