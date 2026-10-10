import re
from typing import Dict, Any, List

class CodeMixHandler:
    """
    Handles Indic-English code-mixed utterances (e.g., 'நான் tomorrow Chennai போறேன்' or 'officeக்கு போறேன்').
    Extracts embedded English/loan words and keeps normalized context alongside original transcript.
    """

    TAMIL_RANGE = re.compile(r"[\u0B80-\u0BFF]")
    DEVANAGARI_RANGE = re.compile(r"[\u0900-\u097F]")
    MALAYALAM_RANGE = re.compile(r"[\u0D00-\u0D7F]")
    TELUGU_RANGE = re.compile(r"[\u0C00-\u0C7F]")
    KANNADA_RANGE = re.compile(r"[\u0C80-\u0CFF]")
    LATIN_WORD = re.compile(r"\b[A-Za-z]+\b")

    # Common agglutinative suffixes in Tamil attached to English stems
    INDIC_SUFFIXES = [
        "க்கு", "கு", "ல", "வா", "லிருந்து", "ஓட", "ஐ", "யும்"  # Tamil suffixes
    ]

    def analyze(self, text: str) -> Dict[str, Any]:
        has_tamil = bool(self.TAMIL_RANGE.search(text))
        has_devanagari = bool(self.DEVANAGARI_RANGE.search(text))
        has_malayalam = bool(self.MALAYALAM_RANGE.search(text))
        has_latin = bool(self.LATIN_WORD.search(text))

        is_code_mixed = has_latin and (has_tamil or has_devanagari or has_malayalam)
        embedded_terms = []

        if is_code_mixed:
            words = text.split()
            for w in words:
                # Check for Latin stem
                latin_match = self.LATIN_WORD.search(w)
                if latin_match:
                    stem = latin_match.group(0)
                    embedded_terms.append(stem)

        return {
            "is_code_mixed": is_code_mixed,
            "has_tamil": has_tamil,
            "has_hindi": has_devanagari,
            "has_malayalam": has_malayalam,
            "has_english": has_latin,
            "embedded_terms": embedded_terms,
            "normalized_context": text
        }

code_mix_handler = CodeMixHandler()
