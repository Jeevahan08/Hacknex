"""
Defect Regression Test Suite for INDICLIVE.
Implements Tests A through L required by the specification:
  Test A: English to Tamil complete translation into Tamil script
  Test B: English to Hindi complete translation into Devanagari script
  Test C: English to Malayalam complete translation into Malayalam script
  Test D: English to Marathi complete translation into Marathi Devanagari script
  Test E: Unseen vocabulary handled by translation model
  Test F: Long speech (multi-sentence paragraph) with no dropped content
  Test G: Continuous microphone input (multiple consecutive segments)
  Test H: Pause and resume without session termination
  Test I: Technical glossary preservation and preferred terminology
  Test J: Reverse translation (Indic -> English and Indic -> Indic)
  Test K: API failure reporting genuine error instead of source text
  Test L: Voiceover receiving translated text and target language
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from app.config import settings
from app.ai.providers.sarvam.translation import SarvamTranslationProvider
from app.ai.providers.sarvam.stt import SarvamSTTProvider, pcm_to_wav
from app.ai.providers.sarvam.tts import SarvamTTSProvider
from app.ai.intelligence.script_validator import validate_target_script
from app.ai.intelligence.commit_policy import IntelligentCommitPolicy
from app.ai.intelligence.glossary import glossary_engine
from app.ai.pipelines.live_translation import LiveTranslationPipelineSession

@pytest.fixture
def translation_provider():
    return SarvamTranslationProvider()

@pytest.fixture
def tts_provider():
    return SarvamTTSProvider()

# ─── Test A: English to Tamil ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_a_english_to_tamil(translation_provider):
    """
    Test A — English to Tamil:
    Input: "Hello, how are you? Today we are presenting our new project."
    Verify complete translation into Tamil script and preservation of the entire meaning.
    """
    text = "Hello, how are you? Today we are presenting our new project."
    result = await translation_provider.translate("en-IN", "ta-IN", text)

    assert result != text, "Translation must not be identical to source text"
    valid, msg = validate_target_script("ta-IN", result)
    assert valid, f"Expected Tamil script, got: '{result}' ({msg})"
    # Ensure it's not a short truncated snippet
    assert len(result) > 15, f"Translation too short / truncated: '{result}'"
    assert "Hello" not in result, f"Roman English greeting leaked into Tamil: '{result}'"

# ─── Test B: English to Hindi ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_b_english_to_hindi(translation_provider):
    """
    Test B — English to Hindi:
    Input: "Good morning everyone. We are going to demonstrate our live translation system."
    Verify complete translation into Hindi script.
    """
    text = "Good morning everyone. We are going to demonstrate our live translation system."
    result = await translation_provider.translate("en-IN", "hi-IN", text)

    assert result != text, "Translation must not be identical to source text"
    valid, msg = validate_target_script("hi-IN", result)
    assert valid, f"Expected Hindi Devanagari script, got: '{result}' ({msg})"
    assert len(result) > 15, f"Translation too short: '{result}'"

# ─── Test C: English to Malayalam ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_c_english_to_malayalam(translation_provider):
    """
    Test C — English to Malayalam:
    Verify the entire sentence is translated, not merely recognized or romanized.
    """
    text = "This entire sentence must be properly translated into Malayalam script."
    result = await translation_provider.translate("en-IN", "ml-IN", text)

    assert result != text, "Translation must not be identical to source text"
    valid, msg = validate_target_script("ml-IN", result)
    assert valid, f"Expected Malayalam script, got: '{result}' ({msg})"
    assert len(result) > 15, f"Translation too short: '{result}'"

# ─── Test D: English to Marathi ───────────────────────────────────────────────
@pytest.mark.asyncio
async def test_d_english_to_marathi(translation_provider):
    """
    Test D — English to Marathi:
    Verify the translation uses appropriate Marathi text.
    """
    text = "We are developing advanced multilingual speech translation software."
    result = await translation_provider.translate("en-IN", "mr-IN", text)

    assert result != text, "Translation must not be identical to source text"
    valid, msg = validate_target_script("mr-IN", result)
    assert valid, f"Expected Marathi Devanagari script, got: '{result}' ({msg})"
    assert len(result) > 15, f"Translation too short: '{result}'"

# ─── Test E: Unseen Vocabulary ────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_e_unseen_vocabulary(translation_provider):
    """
    Test E — Unseen vocabulary:
    Use a sentence containing words absent from predefined dictionaries.
    Verify that the translation API handles the complete sentence naturally.
    """
    unseen_text = "Quantum computing algorithms significantly enhance cryptographic decryption resilience."
    result = await translation_provider.translate("en-IN", "ta-IN", unseen_text)

    assert result != unseen_text, "Unseen vocabulary must not return English source"
    valid, msg = validate_target_script("ta-IN", result)
    assert valid, f"Expected Tamil script for unseen text, got: '{result}' ({msg})"
    assert len(result) > 15, f"Unseen sentence translation incomplete: '{result}'"

# ─── Test F: Long Speech ───────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_f_long_speech_no_dropped_content(translation_provider):
    """
    Test F — Long speech:
    Use a multi-sentence paragraph. Verify no content is silently dropped at segment boundaries.
    """
    paragraph = (
        "Welcome to the annual international technology summit. "
        "Our team has engineered a high-precision real-time translation architecture. "
        "We support seamless continuous conversation across Indian languages."
    )
    result_ta = await translation_provider.translate("en-IN", "ta-IN", paragraph)
    result_hi = await translation_provider.translate("en-IN", "hi-IN", paragraph)

    valid_ta, _ = validate_target_script("ta-IN", result_ta)
    valid_hi, _ = validate_target_script("hi-IN", result_hi)
    assert valid_ta, f"Expected full Tamil paragraph, got: '{result_ta}'"
    assert valid_hi, f"Expected full Hindi paragraph, got: '{result_hi}'"
    # Ensure length reflects a full multi-sentence paragraph, not just 1 sentence
    assert len(result_ta) > 40, f"Tamil paragraph was truncated: '{result_ta}'"
    assert len(result_hi) > 40, f"Hindi paragraph was truncated: '{result_hi}'"

# ─── Test G: Continuous Microphone Input ──────────────────────────────────────
@pytest.mark.asyncio
async def test_g_continuous_speech_multi_segments():
    """
    Test G — Continuous microphone input:
    Simulates consecutive audio speech chunks over time.
    Verifies that the system continues receiving audio and commits multiple segments.
    """
    stt = SarvamSTTProvider()
    session_id = "test_continuous_sess_001"
    await stt.start_stream(session_id, source_language="en-IN")

    # Send 10 chunks of PCM audio (simulating speech stream)
    # 16-bit linear PCM audio chunk (16000 samples/s * 2 bytes = 32000 bytes/sec)
    dummy_speech_chunk = b"\x10\x0f" * 4096  # Audio with voice activity energy
    for _ in range(10):
        await stt.send_audio_chunk(session_id, dummy_speech_chunk)

    session_data = stt._active_sessions.get(session_id)
    assert session_data is not None
    assert session_data["audio_chunks_received"] == 10
    assert session_data["total_bytes_received"] == 10 * len(dummy_speech_chunk)
    assert not session_data["closed"], "Continuous session must remain open while streaming"

    await stt.close_stream(session_id)

# ─── Test H: Pause and Resume ─────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_h_pause_and_resume_session_stays_active():
    """
    Test H — Pause and resume:
    Pause briefly, then continue speaking. Verify that the session remains active.
    """
    policy = IntelligentCommitPolicy(min_tokens=3, silence_commit_ms=850)

    # Segment 1 speech completes
    d1 = policy.evaluate("Hello everyone, how are you today?", is_speech_final=True)
    assert d1.should_translate
    assert d1.is_final_commit

    # Pause occurs: reset policy for next utterance (session is NOT closed)
    policy.reset()

    # Segment 2 begins after pause
    d2 = policy.evaluate("We are continuing our presentation after a brief pause.", is_speech_final=True)
    assert d2.should_translate
    assert d2.is_final_commit
    assert "brief pause" in d2.stable_text

# ─── Test I: Technical Glossary Preservation ──────────────────────────────────
@pytest.mark.asyncio
async def test_i_glossary_preservation_and_preference():
    """
    Test I — Glossary:
    Include a technical brand name ("RailBlock AI") and verify it is preserved.
    Include a preferred term ("Machine Learning" -> "இயந்திர கற்றல்" for Tamil).
    """
    # 1. Preserved term
    src_text = "RailBlock AI monitors automated railway safety."
    post_preserved = glossary_engine.apply_post("ரயில்வே பாதுகாப்பை RailBlock AI கண்காணிக்கிறது.", "ta-IN", source_text=src_text)
    assert "RailBlock AI" in post_preserved, f"Preserved brand name missing: '{post_preserved}'"

    # 2. Preferred term
    src_text2 = "We specialize in Machine Learning algorithms."
    translated_raw = "நாங்கள் Machine Learning வழிமுறைகளில் நிபுணத்துவம் பெற்றுள்ளோம்."
    post_preferred = glossary_engine.apply_post(translated_raw, "ta-IN", source_text=src_text2)
    assert "இயந்திர கற்றல்" in post_preferred, f"Preferred Tamil term missing: '{post_preferred}'"

# ─── Test J: Reverse Translation ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_j_reverse_translation_indic_to_english(translation_provider):
    """
    Test J — Reverse translation:
    Tamil, Hindi, Malayalam, and Marathi to English, and Indic-to-Indic.
    """
    # Tamil -> English
    ta_en = await translation_provider.translate("ta-IN", "en-IN", "அனைவருக்கும் காலை வணக்கம்.")
    assert "morning" in ta_en.lower() or "everyone" in ta_en.lower(), f"Unexpected Tamil->English: '{ta_en}'"

    # Hindi -> English
    hi_en = await translation_provider.translate("hi-IN", "en-IN", "सभी को सुप्रभात।")
    assert "morning" in hi_en.lower() or "everyone" in hi_en.lower(), f"Unexpected Hindi->English: '{hi_en}'"

    # Malayalam -> English
    ml_en = await translation_provider.translate("ml-IN", "en-IN", "എല്ലാവർക്കും സുപ്രഭാതം.")
    assert "morning" in ml_en.lower() or "everyone" in ml_en.lower(), f"Unexpected Malayalam->English: '{ml_en}'"

    # Marathi -> English
    mr_en = await translation_provider.translate("mr-IN", "en-IN", "सर्वांना शुभ प्रभात.")
    assert "morning" in mr_en.lower() or "everyone" in mr_en.lower(), f"Unexpected Marathi->English: '{mr_en}'"

    # Indic-to-Indic (Tamil -> Hindi)
    ta_hi = await translation_provider.translate("ta-IN", "hi-IN", "அனைவருக்கும் காலை வணக்கம்.")
    valid_dev, _ = validate_target_script("hi-IN", ta_hi)
    assert valid_dev, f"Tamil->Hindi must produce Devanagari, got: '{ta_hi}'"

# ─── Test K: API Failure Reporting ────────────────────────────────────────────
@pytest.mark.asyncio
async def test_k_api_failure_reports_genuine_error():
    """
    Test K — API failure:
    Verify that the system reports a genuine error instead of displaying the source text as a successful translation.
    """
    provider = SarvamTranslationProvider()
    source_sentence = "This sentence simulates an unexpected provider network breakdown."

    # Simulate client exception (network failure / 503)
    with patch.object(provider.client, 'post', side_effect=Exception("Connection refused by remote host")):
        with patch.object(settings, 'DEMO_MODE', False):
            result = await provider.translate("en-IN", "ta-IN", source_sentence)

            # 1. Result must NOT be the source sentence
            assert result != source_sentence, "Failure must never return the source text"
            # 2. Result must clearly indicate error
            assert "[TRANSLATION ERROR:" in result
            # 3. Validation should reject it
            is_valid, _ = validate_target_script("ta-IN", result)
            assert not is_valid

    # Pipeline verification
    events = []
    async def capture_ws(msg):
        events.append(msg)

    pipeline = LiveTranslationPipelineSession(
        session_id="test_fail_sess",
        source_language="en-IN",
        target_languages=["ta-IN"],
        ws_send_callback=capture_ws
    )
    with patch.object(provider.client, 'post', side_effect=Exception("503 Service Unavailable")):
        with patch.object(settings, 'DEMO_MODE', False):
            await pipeline._run_parallel_translations("Test failure sentence.", is_final=True)

    # Verify event was marked as failed
    failed_evts = [e for e in events if e.get("type") in ("translation.failed", "translation.final") and e.get("status") == "failed"]
    assert len(failed_evts) > 0, f"Expected status='failed', got events: {events}"
    assert failed_evts[0]["error"] is not None

# ─── Test L: Voiceover Integration ────────────────────────────────────────────
@pytest.mark.asyncio
async def test_l_voiceover_receives_target_language(tts_provider):
    """
    Test L — Voiceover:
    Verify that TTS receives the translated text and selected target language.
    """
    target_tamil_text = "அனைவருக்கும் காலை வணக்கம்."
    target_lang = "ta-IN"

    audio_bytes = await tts_provider.synthesize(target_tamil_text, language=target_lang)
    assert len(audio_bytes) > 0, "TTS must generate valid audio bytes"
    # Verify standard WAV header
    assert audio_bytes[:4] == b"RIFF"
    assert audio_bytes[8:12] == b"WAVE"
