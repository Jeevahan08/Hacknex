import re
from typing import List, Dict, Tuple, Any

class EntityProtectionEngine:
    """
    Detects and preserves named entities, numbers, dates, times, and technical terms.
    Prevents translation APIs from corrupting proper nouns or digits.
    """

    KNOWN_LOCATIONS = {"Chennai", "Delhi", "Mumbai", "Bengaluru", "Bangalore", "Kolkata", "Hyderabad", "Perundurai", "Coimbatore", "Madurai", "Kochi"}
    KNOWN_ORGANIZATIONS = {"ISRO", "DRDO", "IIT", "NIT", "AIIMS", "Indian Railways", "RailBlock AI", "IndicLive", "Sarvam", "Google", "DeepMind"}
    KNOWN_NAMES = {"Arun", "Priya", "Rahul", "Ananya", "Karthik", "Sneha", "Vikram", "Deepa", "Suresh"}

    # Regex patterns for time, numbers, currencies
    TIME_PATTERN = re.compile(r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?|\d{1,2}\s*(?:AM|PM|am|pm))\b")
    DATE_PATTERN = re.compile(r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*|\d{1,2}/\d{1,2}/\d{2,4})\b", re.IGNORECASE)
    NUMBER_PATTERN = re.compile(r"\b\d+(?:,\d+)*(?:\.\d+)?\b")

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        entities = []

        # Times
        for match in self.TIME_PATTERN.finditer(text):
            entities.append({"text": match.group(0), "type": "TIME", "preserve": True})

        # Dates
        for match in self.DATE_PATTERN.finditer(text):
            entities.append({"text": match.group(0), "type": "DATE", "preserve": True})

        # Organizations
        for org in self.KNOWN_ORGANIZATIONS:
            if re.search(rf"\b{re.escape(org)}\b", text, re.IGNORECASE):
                entities.append({"text": org, "type": "ORGANIZATION", "preserve": True})

        # Locations
        for loc in self.KNOWN_LOCATIONS:
            if re.search(rf"\b{re.escape(loc)}\b", text, re.IGNORECASE):
                entities.append({"text": loc, "type": "LOCATION", "preserve": True})

        # Names
        for name in self.KNOWN_NAMES:
            if re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE):
                entities.append({"text": name, "type": "PERSON", "preserve": True})

        return entities

    def protect_and_mask(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replaces sensitive literal entities (times, dates, acronyms, technical brands)
        with placeholders like __ENT_0__ to protect them through translation models.
        Names and locations are allowed to translate naturally into the target script
        unless explicitly registered as literal preserve terms.
        """
        entities = self.extract_entities(text)
        placeholders = {}
        masked_text = text

        # Only mask literal tokens that must never be translated (TIME, DATE, NUMBER, ORGANIZATION)
        maskable_types = {"TIME", "DATE", "NUMBER", "ORGANIZATION"}
        idx = 0
        for ent in entities:
            if ent["type"] in maskable_types:
                placeholder = f"__ENT_{idx}__"
                placeholders[placeholder] = ent["text"]
                masked_text = re.sub(rf"\b{re.escape(ent['text'])}\b", placeholder, masked_text, count=1, flags=re.IGNORECASE)
                idx += 1

        return masked_text, placeholders

    def unmask(self, translated_text: str, placeholders: Dict[str, str]) -> str:
        res = translated_text
        for placeholder, original in placeholders.items():
            # Exact replacement
            res = res.replace(placeholder, original)
            # Case-insensitive replacement
            res = re.sub(re.escape(placeholder), original, res, flags=re.IGNORECASE)
            # Tolerant pattern for models that add spaces inside placeholder (e.g. __ ENT_0 __)
            m = re.match(r"__ENT_(\d+)__", placeholder)
            if m:
                i = m.group(1)
                spaced_pat = rf"__\s*ENT\s*_{i}\s*__"
                res = re.sub(spaced_pat, original, res, flags=re.IGNORECASE)
        return res

entity_protection_engine = EntityProtectionEngine()
