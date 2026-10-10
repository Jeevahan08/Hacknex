import re
from typing import Dict, List, Optional
from app.database.models import GlossaryRecord

class GlossaryEngine:
    """
    Glossary and Terminology Engine.
    Supports technical vocabulary, proper names, brand and organization names,
    acronyms, domain-specific terminology, and preferred translations.

    Priority:
      1. Capture complete source text.
      2. Detect and protect relevant entities.
      3. Send complete sentence to translation API.
      4. Apply glossary constraints without destroying sentence grammar.
      5. Validate returned translation.
    """
    def __init__(self):
        # In-memory fast cache with rich glossary configuration
        self.terms: Dict[str, Dict[str, Optional[str]]] = {
            "ISRO": {"action": "preserve", "replacement": "ISRO", "target": None, "source_language": "en-IN", "case_sensitive": True},
            "RailBlock AI": {"action": "preserve", "replacement": "RailBlock AI", "target": None, "source_language": "en-IN", "case_sensitive": False},
            "IndicLive": {"action": "preserve", "replacement": "IndicLive", "target": None, "source_language": "en-IN", "case_sensitive": False},
            "Machine Learning": {"action": "preferred", "replacement": "இயந்திர கற்றல்", "target": "ta-IN", "source_language": "en-IN", "case_sensitive": False}
        }

    def load_from_records(self, records: List[GlossaryRecord]):
        self.terms.clear()
        for r in records:
            self.terms[r.term] = {
                "action": r.action,
                "replacement": r.replacement,
                "target": r.target_language,
                "source_language": getattr(r, "source_language", "en-IN"),
                "case_sensitive": getattr(r, "case_sensitive", False)
            }

    def apply_pre(self, text: str, target_lang: str) -> str:
        """
        Pre-translation hook. We do NOT replace words with foreign scripts
        before translation as that ruins sentence grammar across multiple parallel targets.
        """
        return text

    def apply_post(self, translated_text: str, target_lang: str, source_text: Optional[str] = None) -> str:
        """
        Applies glossary constraints to target translation without breaking grammar.
        Restores preserved acronyms/brands and applies preferred domain terms.
        """
        if not translated_text:
            return translated_text

        processed = translated_text
        src = source_text or ""

        for term, data in self.terms.items():
            action = data.get("action", "preserve")
            target = data.get("target")
            replacement = data.get("replacement")
            case_sens = data.get("case_sensitive", False)
            flags = 0 if case_sens else re.IGNORECASE

            # Check if term appeared in source (if source provided)
            term_in_source = bool(re.search(rf"\b{re.escape(term)}\b", src, flags)) if src else True

            if action == "preserve" and term_in_source:
                # If target is None or matches, ensure the preserved term isn't corrupted
                if target is None or target == target_lang:
                    preserve_token = replacement or term
                    # If model modified the acronym/brand casing or dropped it, restore it
                    # e.g., if "railblock ai" appeared in lowercase, restore exact "RailBlock AI"
                    if re.search(rf"\b{re.escape(term)}\b", processed, re.IGNORECASE):
                        processed = re.sub(rf"\b{re.escape(term)}\b", preserve_token, processed, flags=re.IGNORECASE)

            elif action == "preferred" and replacement and term_in_source:
                if target is None or target == target_lang:
                    # Apply preferred target translation if the term or English loan word remains in the target text
                    if re.search(rf"\b{re.escape(term)}\b", processed, flags):
                        processed = re.sub(rf"\b{re.escape(term)}\b", replacement, processed, flags=flags)

        return processed

glossary_engine = GlossaryEngine()
