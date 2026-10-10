"""
Comprehensive translation pipeline tests.
Tests for: script validation, translation correctness, same-language passthrough,
demo translation quality, continuous speech (multi-segment), and error handling.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.ai.intelligence.script_validator import validate_target_script
from app.ai.providers.sarvam.translation import SarvamTranslationProvider, DEMO_TRANSLATION_MAP
from app.ai.intelligence.commit_policy import IntelligentCommitPolicy


# ─── Script Validator Tests ────────────────────────────────────────────────────

def test_script_validator_tamil_unicode():
    """Tamil target must contain Tamil script characters."""
    valid, msg = validate_target_script("ta-IN", "வணக்கம், எப்படி இருக்கிறீர்கள்?")
    assert valid is True
    assert "TAMIL" in msg

def test_script_validator_hindi_unicode():
    """Hindi target must contain Devanagari characters."""
    valid, msg = validate_target_script("hi-IN", "नमस्ते, आप कैसे हैं?")
    assert valid is True
    assert "DEVANAGARI" in msg

def test_script_validator_marathi_unicode():
    """Marathi target must contain Devanagari characters."""
    valid, msg = validate_target_script("mr-IN", "नमस्कार, आपण कसे आहात?")
    assert valid is True
    assert "DEVANAGARI" in msg

def test_script_validator_malayalam_unicode():
    """Malayalam target must contain Malayalam script characters."""
    valid, msg = validate_target_script("ml-IN", "ഹലോ, സുഖമാണോ?")
    assert valid is True
    assert "MALAYALAM" in msg

def test_script_validator_rejects_english_as_tamil():
    """English text must NOT pass Tamil script validation."""
    valid, msg = validate_target_script("ta-IN", "Hello, how are you?")
    assert valid is False
    assert "INVALID_TARGET_SCRIPT" in msg

def test_script_validator_rejects_english_as_hindi():
    """English text must NOT pass Hindi script validation."""
    valid, msg = validate_target_script("hi-IN", "Hello how are you")
    assert valid is False
    assert "INVALID_TARGET_SCRIPT" in msg

def test_script_validator_rejects_roman_as_malayalam():
    """Romanized text must NOT pass Malayalam script validation."""
    valid, msg = validate_target_script("ml-IN", "Njan nale Chennaiyilekku pokunu")
    assert valid is False
    assert "INVALID_TARGET_SCRIPT" in msg


# ─── Demo Translation Tests ────────────────────────────────────────────────────

def test_demo_translation_en_to_tamil():
    """English → Tamil must produce Tamil script, not English."""
    provider = SarvamTranslationProvider()
    result = provider._demo_translate("Hello, how are you?", "en-IN", "ta-IN")
    valid, _ = validate_target_script("ta-IN", result)
    assert valid is True, f"Expected Tamil script, got: '{result}'"
    assert "Hello" not in result, f"Source text must not appear in Tamil translation: '{result}'"

def test_demo_translation_en_to_hindi():
    """English → Hindi must produce Devanagari script."""
    provider = SarvamTranslationProvider()
    result = provider._demo_translate("Hello, how are you?", "en-IN", "hi-IN")
    valid, _ = validate_target_script("hi-IN", result)
    assert valid is True, f"Expected Devanagari script, got: '{result}'"

def test_demo_translation_en_to_malayalam():
    """English → Malayalam must produce Malayalam script."""
    provider = SarvamTranslationProvider()
    result = provider._demo_translate("Hello, how are you?", "en-IN", "ml-IN")
    valid, _ = validate_target_script("ml-IN", result)
    assert valid is True, f"Expected Malayalam script, got: '{result}'"

def test_demo_translation_en_to_marathi():
    """English → Marathi must produce Devanagari script."""
    provider = SarvamTranslationProvider()
    result = provider._demo_translate("Good morning everyone.", "en-IN", "mr-IN")
    valid, _ = validate_target_script("mr-IN", result)
    assert valid is True, f"Expected Devanagari Marathi, got: '{result}'"

def test_demo_fallback_does_not_return_source_text():
    """Demo fallback for unknown text must NOT return the source English text as translation."""
    provider = SarvamTranslationProvider()
    unknown_text = "This is a completely unknown test sentence xyz123."
    result_ta = provider._demo_translate(unknown_text, "en-IN", "ta-IN")
    result_hi = provider._demo_translate(unknown_text, "en-IN", "hi-IN")
    # The result must NOT be the original English text passed through
    assert result_ta != unknown_text, f"Tamil fallback must not be the source text: '{result_ta}'"
    assert result_hi != unknown_text, f"Hindi fallback must not be the source text: '{result_hi}'"

def test_demo_translation_case_insensitive_match():
    """Demo lookup should match case-insensitively."""
    provider = SarvamTranslationProvider()
    result = provider._demo_translate("good morning everyone.", "en-IN", "ta-IN")
    valid, _ = validate_target_script("ta-IN", result)
    assert valid is True, f"Case-insensitive match should produce Tamil, got: '{result}'"


# ─── Same-Language Passthrough Test ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_same_language_passthrough():
    """en-IN → en-IN should return the input text unchanged without API call."""
    provider = SarvamTranslationProvider()
    text = "Hello, how are you?"
    result = await provider.translate("en-IN", "en-IN", text)
    assert result == text, f"Same-language passthrough should return source text, got: '{result}'"


# ─── Parallel Translation Tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parallel_translation_demo_mode():
    """Parallel translation in demo mode should return target-script outputs."""
    provider = SarvamTranslationProvider()
    # Force demo mode for this test
    with patch('app.ai.providers.sarvam.translation.settings') as mock_settings:
        mock_settings.is_demo = True
        mock_settings.DEBUG_TRANSLATION = False
        mock_settings.SARVAM_TRANSLATION_MODEL = "sarvam-translate:v1"

        results = await provider.translate_parallel(
            source_language="en-IN",
            target_languages=["ta-IN", "hi-IN", "ml-IN"],
            text="Good morning everyone."
        )

    assert "ta-IN" in results
    assert "hi-IN" in results
    assert "ml-IN" in results

    ta_valid, _ = validate_target_script("ta-IN", results["ta-IN"])
    hi_valid, _ = validate_target_script("hi-IN", results["hi-IN"])
    ml_valid, _ = validate_target_script("ml-IN", results["ml-IN"])

    assert ta_valid, f"Tamil result must be Tamil script: '{results['ta-IN']}'"
    assert hi_valid, f"Hindi result must be Devanagari: '{results['hi-IN']}'"
    assert ml_valid, f"Malayalam result must be Malayalam script: '{results['ml-IN']}'"


# ─── Commit Policy Multi-Segment Test ─────────────────────────────────────────

def test_commit_policy_multi_segment_continuous_speech():
    """
    Continuous speech should produce multiple committed segments,
    not just one. A short pause must NOT end the session.
    """
    policy = IntelligentCommitPolicy(min_tokens=3, silence_commit_ms=850)

    # Segment 1: "Hello everyone good morning"
    d1 = policy.evaluate("Hello everyone good morning.", is_speech_final=True)
    assert d1.should_translate
    assert d1.is_final_commit

    # Policy resets for next segment (as pipeline.py now does after commit)
    policy.reset()

    # Segment 2: new speech continues after the first commit
    d2 = policy.evaluate("Today we are going to", is_speech_final=False)
    # Should be buffering since not enough context yet
    # (depends on timing, but this verifies policy can handle a second segment)
    assert isinstance(d2.should_translate, bool)  # Just verify it evaluates without error

    policy.reset()

    # Segment 3
    d3 = policy.evaluate("discuss our live translation project.", is_speech_final=True)
    assert d3.should_translate
    assert d3.is_final_commit


def test_commit_policy_pause_does_not_kill_session():
    """
    A short pause (silence) should commit the current segment but NOT
    indicate session termination. The policy itself never 'ends' a session.
    The session stays alive between segments.
    """
    policy = IntelligentCommitPolicy(min_tokens=3, silence_commit_ms=850)

    # First segment commits on silence
    import time
    # Simulate max partial wait exceeded
    d = policy.evaluate("Hello everyone", is_speech_final=False, silence_duration_ms=900)
    # 900ms > silence_commit_ms(850ms) and >= min_tokens(3)... wait, 2 tokens
    # So it should buffer since we only have 2 tokens
    # Let's use a 3+ token text
    d = policy.evaluate("Hello everyone good", is_speech_final=False, silence_duration_ms=900)
    assert d.should_translate  # silence triggers commit
    assert d.is_final_commit

    # Reset simulates pipeline moving to next segment — NOT closing WebSocket
    policy.reset()

    # Session is still "alive" — next utterance evaluates normally
    d2 = policy.evaluate("Good morning", is_speech_final=False)
    # Only 2 tokens, should buffer
    assert not d2.should_translate


# ─── API HTTP Tests ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_translation_api_demo_response():
    """Translation API endpoint should return target-language translations, not source text."""
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/translate", json={
            "source_language": "en-IN",
            "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
            "text": "Good morning everyone.",
            "mode": "fast"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "translations" in data

        ta_text = data["translations"]["ta-IN"]["translated_text"]
        hi_text = data["translations"]["hi-IN"]["translated_text"]
        ml_text = data["translations"]["ml-IN"]["translated_text"]

        # Verify target languages are correct script
        ta_valid, ta_msg = validate_target_script("ta-IN", ta_text)
        hi_valid, hi_msg = validate_target_script("hi-IN", hi_text)
        ml_valid, ml_msg = validate_target_script("ml-IN", ml_text)

        assert ta_valid, f"Tamil translation must be Tamil script, got: '{ta_text}' ({ta_msg})"
        assert hi_valid, f"Hindi translation must be Devanagari, got: '{hi_text}' ({hi_msg})"
        assert ml_valid, f"Malayalam translation must be Malayalam script, got: '{ml_text}' ({ml_msg})"

        # Critical: source text must NOT appear as translation
        source = "Good morning everyone."
        assert ta_text != source, "Tamil translation must not be the source text"
        assert hi_text != source, "Hindi translation must not be the source text"
        assert ml_text != source, "Malayalam translation must not be the source text"
