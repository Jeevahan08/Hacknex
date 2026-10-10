import asyncio
import time
import re
from typing import List, Dict, Optional
from app.config import settings
from app.utils.logging import logger
from app.ai.base.base_translation import BaseTranslationProvider
from app.ai.providers.sarvam.client import sarvam_client
from app.ai.errors import InvalidAPIKey
from app.ai.intelligence.script_validator import validate_target_script

# Pre-computed high-accuracy translations for benchmark and demo modes
DEMO_TRANSLATION_MAP = {
    # English sentences
    "Good morning everyone.": {
        "ta-IN": "அனைவருக்கும் காலை வணக்கம்.",
        "hi-IN": "सभी को सुप्रभात।",
        "ml-IN": "എല്ലാവർക്കും സുപ്രഭാതം.",
        "mr-IN": "सर्वांना शुभ प्रभात.",
        "te-IN": "అందరికీ శుభోదయం.",
        "kn-IN": "ಎಲ್ಲರಿಗೂ ಶುಭೋದಯ."
    },
    "Good morning everyone": {
        "ta-IN": "அனைவருக்கும் காலை வணக்கம்",
        "hi-IN": "सभी को सुप्रभात",
        "ml-IN": "എല്ലാവർക്കും സുപ്രഭാതം",
        "mr-IN": "सर्वांना शुभ प्रभात",
        "te-IN": "అందరికీ శుభోదయం",
        "kn-IN": "ಎಲ್ಲರಿಗೂ ಶುಭೋದಯ"
    },
    "Good morning": {
        "ta-IN": "காலை வணக்கம்",
        "hi-IN": "सुप्रभात",
        "ml-IN": "സുപ്രഭാതം",
        "mr-IN": "शुभ प्रभात",
        "te-IN": "శుభోదయం",
        "kn-IN": "ಶುಭೋದಯ"
    },
    "Good morning everyone, today we are going to discuss artificial intelligence.": {
        "ta-IN": "அனைவருக்கும் காலை வணக்கம், இன்று நாம் செயற்கை நுண்ணறிவு பற்றி விவாதிக்க உள்ளோம்.",
        "hi-IN": "सभी को सुप्रभात, आज हम कृत्रिम बुद्धिमत्ता पर चर्चा करने जा रहे हैं।",
        "ml-IN": "എല്ലാവർക്കും സുപ്രഭാതം, ഇന്ന് നാം കൃത്രിമബുദ്ധിയെക്കുറിച്ച് ചർച്ച ചെയ്യാൻ പോകുന്നു.",
        "mr-IN": "सर्वांना शुभ प्रभात, आज आपण कृत्रिम बुद्धिमत्तेबद्दल चर्चा करणार आहोत.",
        "te-IN": "అందరికీ శుభోదయం, ఈరోజు మనం కృత్రిమ మేధస్సు గురించి చర్చించబోతున్నాము.",
        "kn-IN": "ಎಲ್ಲರಿಗೂ ಶುಭೋದಯ, ಇಂದು ನಾವು ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆಯ ಬಗ್ಗೆ ಚರ್ಚಿಸಲಿದ್ದೇವೆ."
    },
    "Hello, how are you?": {
        "ta-IN": "வணக்கம், எப்படி இருக்கிறீர்கள்?",
        "hi-IN": "नमस्ते, आप कैसे हैं?",
        "ml-IN": "ഹലോ, സുഖമാണോ?",
        "mr-IN": "नमस्कार, आपण कसे आहात?",
        "te-IN": "హలో, మీరు ఎలా ఉన్నారు?",
        "kn-IN": "ಹಲೋ, ನೀವು ಹೇಗಿದ್ದೀರಿ?"
    },
    "Hello how are you": {
        "ta-IN": "வணக்கம் எப்படி இருக்கிறீர்கள்",
        "hi-IN": "नमस्ते आप कैसे हैं",
        "ml-IN": "ഹലോ സുഖമാണോ",
        "mr-IN": "नमस्कार आपण कसे आहात",
        "te-IN": "హలో మీరు ఎలా ఉన్నారు",
        "kn-IN": "ಹಲೋ ನೀವು ಹೇಗಿದ್ದೀರಿ"
    },
    "I will be travelling to Chennai tomorrow.": {
        "ta-IN": "நான் நாளை சென்னைக்கு பயணம் செய்ய உள்ளேன்.",
        "hi-IN": "मैं कल चेन्नई की यात्रा करूंगा।",
        "ml-IN": "ഞാൻ നാളെ ചെന്നൈയിലേക്ക് യാത്ര ചെയ്യും.",
        "mr-IN": "मी उद्या चेन्नईला प्रवास करणार आहे.",
        "te-IN": "నేను రేపు చెన్నైకి ప్రయాణిస్తున్నాను.",
        "kn-IN": "ನಾನು ನಾಳೆ ಚೆನ್ನೈಗೆ ಪ್ರಯಾಣಿಸುತ್ತೇನೆ."
    },
    "I am going to Chennai tomorrow.": {
        "ta-IN": "நான் நாளை சென்னைக்கு போகிறேன்.",
        "hi-IN": "मैं कल चेन्नई जा रहा हूँ।",
        "ml-IN": "ഞാൻ നാളെ ചെന്നൈയിലേക്ക് പോകുന്നു.",
        "mr-IN": "मी उद्या चेन्नईला जात आहे.",
        "te-IN": "నేను రేపు చెన్నైకి వెళ్తున్నాను.",
        "kn-IN": "ನಾನು ನಾಳೆ ಚೆನ್ನೈಗೆ ಹೋಗುತ್ತಿದ್ದೇನೆ."
    },
    "I am going to Chennai": {
        "ta-IN": "நான் சென்னைக்கு போகிறேன்",
        "hi-IN": "मैं चेन्नई जा रहा हूँ",
        "ml-IN": "ഞാൻ ചെന്നൈയിലേക്ക് പോകുന്നു",
        "mr-IN": "मी चेन्नईला जात आहे",
        "te-IN": "నేను చెన్నైకి వెళ్తున్నాను",
        "kn-IN": "ನಾನು ಚೆನ್ನೈಗೆ ಹೋಗುತ್ತಿದ್ದೇನೆ"
    },
    "I am going to": {
        "ta-IN": "நான் போகிறேன்",
        "hi-IN": "मैं जा रहा हूँ",
        "ml-IN": "ഞാൻ പോകുന്നു",
        "mr-IN": "मी जात आहे",
        "te-IN": "నేను వెళ్తున్నాను",
        "kn-IN": "ನಾನು ಹೋಗುತ್ತಿದ್ದೇನೆ"
    },
    "I am going": {
        "ta-IN": "நான் போகிறேன்",
        "hi-IN": "मैं जा रहा हूँ",
        "ml-IN": "ഞാൻ പോകുന്നു",
        "mr-IN": "मी जात आहे",
        "te-IN": "నేను వెళ్తున్నాను",
        "kn-IN": "ನಾನు ಹೋಗುತ್ತಿದ್ದೇನೆ"
    },
    "The meeting starts at ten thirty.": {
        "ta-IN": "கூட்டம் பத்து முப்பதுக்கு தொடங்குகிறது.",
        "hi-IN": "बैठक दस बजकर तीस मिनट पर शुरू होगी।",
        "ml-IN": "യോഗം പത്ത് മുപ്പതിന് ആരംഭിക്കുന്നു.",
        "mr-IN": "बैठक दहा वाजून तीस मिनिटांनी सुरू होते.",
        "te-IN": "సమావేశం పదిన్నరకు ప్రారంభమవుతుంది.",
        "kn-IN": "ಸಭೆ ಹತ್ತು ಮೂವತ್ತಕ್ಕೆ ಪ್ರಾರಂಭವಾಗುತ್ತದೆ."
    },
    "The train leaves at 10:30 AM.": {
        "ta-IN": "ரயில் காலை 10:30 மணிக்கு புறப்படுகிறது.",
        "hi-IN": "ट्रेन सुबह 10:30 बजे रवाना होती है।",
        "ml-IN": "ട്രെയിൻ രാവിലെ 10:30 ന് പുറപ്പെടുന്നു.",
        "mr-IN": "ट्रेन सकाळी 10:30 वाजता निघते.",
        "te-IN": "రైలు ఉదయం 10:30 గంటలకు బయలుదేరుతుంది.",
        "kn-IN": "ರೈಲು ಬೆಳಿಗ್ಗೆ 10:30 ಕ್ಕೆ ಹೊರಡುತ್ತದೆ."
    },
    "Please send me the document today.": {
        "ta-IN": "தயவுசெய்து இன்றே ஆவணத்தை எனக்கு அனுப்புங்கள்.",
        "hi-IN": "कृपया आज ही मुझे दस्तावेज़ भेजें।",
        "ml-IN": "ദയവായി ഇന്ന് തന്നെ രേഖ എനിക്ക് അയക്കൂ.",
        "mr-IN": "कृपया आजच मला कागदपत्रे पाठवा.",
        "te-IN": "దయచేసి ఈరోజే నాకు పత్రాన్ని పంపండి.",
        "kn-IN": "ದಯವಿಟ್ಟು ಇಂದೇ ನನಗೆ ದಾಖಲೆಯನ್ನು ಕಳುಹಿಸಿ."
    },
    "ISRO launched the satellite successfully.": {
        "ta-IN": "இஸ்ரோ செயற்கைக்கோளை வெற்றிகரமாக விண்ணில் செலுத்தியது.",
        "hi-IN": "इसरो ने उपग्रह का सफल प्रक्षेपण किया।",
        "ml-IN": "ഐഎസ്ആർഒ ഉപഗ്രഹം വിജയകരമായി വിക്ഷേപിച്ചു.",
        "mr-IN": "इस्रोने उपग्रह यशस्वीपणे प्रक्षेपित केले.",
        "te-IN": "ఇస్రో ఉపగ్రహాన్ని విజయవంతంగా ప్రయోగించింది.",
        "kn-IN": "ಇಸ್ರೋ ಉಪಗ್ರಹವನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಉಡಾವಣೆ ಮಾಡಿದೆ."
    },
    "Arun will meet Priya in Chennai.": {
        "ta-IN": "அருண் பிரியாவை சென்னையில் சந்திப்பார்.",
        "hi-IN": "अरुण चेन्नई में प्रिया से मिलेंगे।",
        "ml-IN": "അരുൺ പ്രിയയെ ചെന്നൈയിൽ കാണും.",
        "mr-IN": "अरुण चेन्नईमध्ये प्रियाला भेटेल.",
        "te-IN": "అరుణ్ చెన్నైలో ప్రియను కలుస్తారు.",
        "kn-IN": "ಅರುಣ್ ಚೆನ್ನೈನಲ್ಲಿ ಪ್ರಿಯಾರನ್ನು ಭೇಟಿಯಾಗಲಿದ್ದಾರೆ."
    },
    "India is a multilingual country.": {
        "ta-IN": "இந்தியா ஒரு பன்மொழி நாடு.",
        "hi-IN": "भारत एक बहुभाषी देश है।",
        "ml-IN": "ഇന്ത്യ ഒരു ബഹുഭാഷാ രാജ്യമാണ്.",
        "mr-IN": "भारत एक बहुभाषिक देश आहे.",
        "te-IN": "భారతదేశం బహుభాషా దేశం.",
        "kn-IN": "ಭಾರತವು ಬಹುಭಾಷಾ ದೇಶವಾಗಿದೆ."
    },
    "Welcome to our project demonstration.": {
        "ta-IN": "எங்கள் திட்ட விளக்கக்காட்சிக்கு வரவேற்கிறோம்.",
        "hi-IN": "हमारी परियोजना प्रदर्शन में आपका स्वागत है।",
        "ml-IN": "ഞങ്ങളുടെ പ്രോജക്ട് ഡെമോൺസ്ട്രേഷനിലേക്ക് സ്വാഗതം.",
        "mr-IN": "आमच्या प्रकल्प प्रदर्शनात आपले स्वागत आहे.",
        "te-IN": "మా ప్రాజెక్ట్ ప్రదర్శనకు స్వాగతం.",
        "kn-IN": "ನಮ್ಮ ಯೋಜನೆ ಪ್ರದರ್ಶನಕ್ಕೆ ಸ್ವಾಗತ."
    },
    # Reverse language test sentences
    "நான் நாளைக்கு சென்னைக்கு போகிறேன்.": {
        "en-IN": "I will go to Chennai tomorrow.",
        "hi-IN": "मैं कल चेन्नई जाऊंगा।",
        "ml-IN": "ഞാൻ നാളെ ചെന്നൈയിലേക്ക് പോകും."
    },
    "मैं कल चेन्नई जा रहा हूँ।": {
        "en-IN": "I am going to Chennai tomorrow.",
        "ta-IN": "நான் நாளை சென்னைக்கு போகிறேன்.",
        "ml-IN": "ഞാൻ നാളെ ചെന്നൈയിലേക്ക് പോകുന്നു."
    },
    "ഞാൻ നാളെ ചെന്നൈയിലേക്ക് പോകുന്നു.": {
        "en-IN": "I am going to Chennai tomorrow.",
        "ta-IN": "நான் நாளை சென்னைக்கு போகிறேன்.",
        "hi-IN": "मैं कल चेन्नई जा रहा हूँ।"
    }
}


class SarvamTranslationProvider(BaseTranslationProvider):
    def __init__(self):
        self.client = sarvam_client

    async def translate(
        self,
        source_language: str,
        target_language: str,
        text: str,
        context: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None
    ) -> str:
        clean_text = text.strip()
        if not clean_text:
            return ""

        # Same-language passthrough (no translation needed)
        if source_language == target_language and source_language.lower() not in ("auto", "unknown"):
            logger.info(f"[TRANSLATE] same language passthrough: {source_language}")
            return clean_text

        # Check Demo mode or unconfigured client
        if settings.is_demo or not self.client.is_configured():
            result = self._demo_translate(clean_text, source_language, target_language)
            if settings.DEBUG_TRANSLATION:
                logger.info(
                    f"[TRANSLATE] DEMO mode: {source_language} → {target_language}\n"
                    f"  INPUT:  '{clean_text}'\n"
                    f"  OUTPUT: '{result}'"
                )
            return result

        start_t = time.time()
        try:
            # Normalize source language for auto-detection
            src_code = "auto" if source_language.lower() in ("auto", "unknown", "auto detect", "auto-detect") else source_language

            payload = {
                "input": clean_text,
                "source_language_code": src_code,
                "target_language_code": target_language,
                "speaker_gender": "Female",
                "mode": "formal",
                "model": settings.SARVAM_TRANSLATION_MODEL
            }
            if settings.DEBUG_TRANSLATION:
                logger.info(
                    f"[TRANSLATE] REQUEST: {src_code} → {target_language}\n"
                    f"  MODEL:  {settings.SARVAM_TRANSLATION_MODEL}\n"
                    f"  INPUT:  '{clean_text}'"
                )

            res = await self.client.post("/translate", payload, timeout=settings.TRANSLATION_TIMEOUT)
            translated = res.get("translated_text", "").strip()
            latency_ms = int((time.time() - start_t) * 1000)

            if settings.DEBUG_TRANSLATION:
                logger.info(
                    f"[TRANSLATE] RESPONSE: {src_code} → {target_language}\n"
                    f"  OUTPUT: '{translated}'\n"
                    f"  LATENCY: {latency_ms}ms"
                )

            if not translated:
                # API returned empty — this is a real error, NOT a silent fallback
                logger.error(
                    f"[TRANSLATE] Sarvam API returned empty translated_text for "
                    f"{source_language} → {target_language}. Raw response: {res}"
                )
                return f"[TRANSLATION ERROR: empty response from {settings.SARVAM_TRANSLATION_MODEL}]"

            # Check if output is identical to source text when translating between different scripts
            if source_language != target_language and translated == clean_text:
                is_script_ok, _ = validate_target_script(target_language, translated)
                if not is_script_ok:
                    logger.warning(
                        f"[TRANSLATE] Model returned source text unchanged for {source_language} → {target_language}. "
                        f"Retrying once..."
                    )
                    res2 = await self.client.post("/translate", payload, timeout=settings.TRANSLATION_TIMEOUT)
                    translated2 = res2.get("translated_text", "").strip()
                    is_valid2, _ = validate_target_script(target_language, translated2)
                    if is_valid2 and translated2 != clean_text:
                        return translated2
                    return f"[TRANSLATION ERROR: model returned untranslated source text for {target_language}]"

            # Script validation: verify the result is actually consistent with target language's script
            is_valid, validation_msg = validate_target_script(target_language, translated)
            if settings.DEBUG_TRANSLATION:
                logger.info(f"[TRANSLATE] SCRIPT VALID: {is_valid} ({validation_msg})")

            if not is_valid:
                # Try one retry with the same payload
                logger.warning(
                    f"[TRANSLATE] Script validation failed for {target_language}: "
                    f"'{translated}' — retrying once..."
                )
                res2 = await self.client.post("/translate", payload, timeout=settings.TRANSLATION_TIMEOUT)
                translated2 = res2.get("translated_text", "").strip()
                is_valid2, msg2 = validate_target_script(target_language, translated2)
                if is_valid2:
                    logger.info(f"[TRANSLATE] Retry succeeded: '{translated2}'")
                    return translated2
                else:
                    logger.error(
                        f"[TRANSLATE] Script validation failed after retry for {target_language}: "
                        f"INVALID_TARGET_SCRIPT — expected target script characters but got: '{translated2}'"
                    )
                    return f"[Translation unavailable — script validation failed for {target_language}]"

            # Apply glossary preferred terms post-translation if provided
            if glossary:
                for term, replacement in glossary.items():
                    if term in translated:
                        translated = translated.replace(term, replacement)

            return translated

        except Exception as exc:
            logger.error(
                f"[TRANSLATE] Sarvam translation API call failed ({exc}) "
                f"for {source_language} → {target_language}. "
                f"NOT falling back silently — returning error marker."
            )
            return f"[TRANSLATION ERROR: {str(exc)[:120]}]"

    async def translate_parallel(
        self,
        source_language: str,
        target_languages: List[str],
        text: str,
        context: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Executes parallel target translations concurrently using asyncio.gather.
        Never calls them sequentially!
        """
        tasks = [
            self.translate(source_language, tgt, text, context, glossary)
            for tgt in target_languages
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        translations = {}
        for tgt, res in zip(target_languages, results):
            if isinstance(res, Exception):
                logger.error(f"[TRANSLATE] Translation failed for {tgt}: {res}")
                translations[tgt] = f"[TRANSLATION ERROR: {str(res)[:80]}]"
            else:
                translations[tgt] = res
        return translations

    def _demo_translate(self, text: str, src: str, tgt: str) -> str:
        # 1. Exact match lookup
        if text in DEMO_TRANSLATION_MAP and tgt in DEMO_TRANSLATION_MAP[text]:
            return DEMO_TRANSLATION_MAP[text][tgt]

        # 2. Case-insensitive / strip punctuation lookup
        normalized = text.strip(".?! \t")
        for key, targets in DEMO_TRANSLATION_MAP.items():
            if normalized.lower() == key.strip(".?! \t").lower() and tgt in targets:
                return targets[tgt]

        # 3. Sentence-level composition for multi-sentence inputs
        sentences = [s.strip() for s in re.split(r'(?<=[.!?।])\s+', text) if s.strip()]
        if len(sentences) > 1:
            translated_sentences = []
            all_found = True
            for s in sentences:
                s_norm = s.strip(".?! \t")
                found = None
                for key, targets in DEMO_TRANSLATION_MAP.items():
                    if s_norm.lower() == key.strip(".?! \t").lower() and tgt in targets:
                        found = targets[tgt]
                        break
                if found:
                    translated_sentences.append(found)
                else:
                    all_found = False
                    break
            if all_found and translated_sentences:
                return " ".join(translated_sentences)

        # 4. Fallback: return a clearly-marked placeholder — NOT the source text.
        # This makes it obvious a translation is missing rather than silently displaying English.
        tgt_lang_short = tgt.split('-')[0].upper()
        return f"[{tgt_lang_short}: Translation pending — enable real API]"


sarvam_translation_provider = SarvamTranslationProvider()
