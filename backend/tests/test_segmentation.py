from app.ai.intelligence.stability import CaptionStabilityEngine
from app.ai.intelligence.code_mix import code_mix_handler
from app.ai.intelligence.entity_protection import entity_protection_engine
from app.ai.intelligence.language_detector import language_detector

def test_code_mix_detection():
    # Mixed Tamil-English utterance
    result = code_mix_handler.analyze("நான் tomorrow Chennai போறேன்")
    assert result["is_code_mixed"] is True
    assert "tomorrow" in result["embedded_terms"]
    assert result["has_tamil"] is True

def test_entity_protection_extraction():
    entities = entity_protection_engine.extract_entities("Arun will meet Priya in Chennai at 10:30 AM.")
    types = [e["type"] for e in entities]
    texts = [e["text"] for e in entities]
    assert "LOCATION" in types
    assert "TIME" in types
    assert "Chennai" in texts
    assert "10:30 AM" in texts

def test_stability_engine_calculation():
    engine = CaptionStabilityEngine()
    engine.on_partial("Good")
    engine.on_partial("Good morning")
    engine.on_committed("Good morning everyone.")
    assert engine.stability_score >= 0.95
    assert engine.late_rewrites == 0

def test_language_detection():
    lang, conf = language_detector.detect("அனைவருக்கும் காலை வணக்கம்")
    assert lang == "ta-IN"

    lang_hi, conf_hi = language_detector.detect("सभी को सुप्रभात")
    assert lang_hi == "hi-IN"

    lang_ml, conf_ml = language_detector.detect("എല്ലാവർക്കും സുപ്രഭാതം")
    assert lang_ml == "ml-IN"
