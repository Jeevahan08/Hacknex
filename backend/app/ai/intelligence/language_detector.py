import re
from typing import Dict, Tuple

class IndicLanguageDetector:
    """
    Fast script-based and statistical language detector for Indian languages and English.
    """

    SCRIPTS = {
        "ta-IN": (re.compile(r"[\u0B80-\u0BFF]"), "Tamil"),
        "hi-IN": (re.compile(r"[\u0900-\u097F]"), "Hindi"),
        "ml-IN": (re.compile(r"[\u0D00-\u0D7F]"), "Malayalam"),
        "te-IN": (re.compile(r"[\u0C00-\u0C7F]"), "Telugu"),
        "kn-IN": (re.compile(r"[\u0C80-\u0CFF]"), "Kannada"),
        "en-IN": (re.compile(r"[A-Za-z]"), "English")
    }

    def detect(self, text: str, default: str = "en-IN") -> Tuple[str, float]:
        if not text or not text.strip():
            return default, 1.0

        counts: Dict[str, int] = {}
        total_matched = 0

        for code, (pattern, name) in self.SCRIPTS.items():
            matches = len(pattern.findall(text))
            if matches > 0:
                counts[code] = matches
                total_matched += matches

        if not counts:
            return default, 0.5

        # Return language with highest char match
        best_code = max(counts, key=counts.get)
        confidence = round(counts[best_code] / max(1, total_matched), 2)
        return best_code, confidence

language_detector = IndicLanguageDetector()
