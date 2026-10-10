import pytest
from app.ai.intelligence.commit_policy import IntelligentCommitPolicy

def test_commit_policy_token_buffering():
    policy = IntelligentCommitPolicy(min_tokens=3)
    
    # 1 token should buffer
    decision = policy.evaluate("I")
    assert not decision.should_translate
    assert decision.reason == "buffering_partial"

    # 2 tokens should still buffer
    decision = policy.evaluate("I am")
    assert not decision.should_translate

    # Speech final event should commit immediately
    decision = policy.evaluate("I am going to Chennai.", is_speech_final=True)
    assert decision.should_translate
    assert decision.is_final_commit
    assert decision.reason == "asr_final_event"

def test_commit_policy_terminal_punctuation():
    policy = IntelligentCommitPolicy(min_tokens=3)
    decision = policy.evaluate("I will be travelling to Chennai tomorrow.")
    assert decision.should_translate
    assert decision.is_final_commit
    assert decision.reason == "terminal_punctuation_commit"
