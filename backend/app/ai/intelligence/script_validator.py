import re
from typing import Tuple, Dict

# Unicode ranges for Indic scripts
SCRIPT_REGEX_MAP: Dict[str, Tuple[re.Pattern, str]] = {
    "ta-IN": (re.compile(r'[\u0B80-\u0BFF]'), "Tamil"),
    "hi-IN": (re.compile(r'[\u0900-\u097F]'), "Devanagari"),
    "mr-IN": (re.compile(r'[\u0900-\u097F]'), "Devanagari"),
    "ml-IN": (re.compile(r'[\u0D00-\u0D7F]'), "Malayalam"),
    "te-IN": (re.compile(r'[\u0C00-\u0C7F]'), "Telugu"),
    "kn-IN": (re.compile(r'[\u0C80-\u0CFF]'), "Kannada"),
    "en-IN": (re.compile(r'[a-zA-Z]'), "Latin"),
}

def validate_target_script(target_language: str, text: str) -> Tuple[bool, str]:
    """
    Validates whether the translated text contains characters in the expected script.
    Guarantees that a Tamil target has Tamil characters, Hindi/Marathi has Devanagari,
    Malayalam has Malayalam script, etc.
    Prevents Romanized transliterations or untranslated source English from falsely
    passing as target language output.
    """
    if not text or not text.strip():
        return False, "EMPTY_TEXT"

    clean = text.strip()
    rule = SCRIPT_REGEX_MAP.get(target_language)
    if not rule:
        # Fallback for unconfigured language codes: accept if non-empty
        return True, "UNKNOWN_SCRIPT_ACCEPTED"

    regex, script_name = rule
    if regex.search(clean):
        return True, f"VALID_{script_name.upper()}_SCRIPT"

    return False, f"INVALID_TARGET_SCRIPT: Expected {script_name} characters, got non-{script_name} text."
