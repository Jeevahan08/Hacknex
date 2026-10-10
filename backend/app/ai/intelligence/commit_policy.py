import time
from typing import List, Optional, Tuple
from app.config import settings
from app.utils.logging import logger

class CommitDecision:
    def __init__(self, should_translate: bool, is_final_commit: bool, reason: str, stable_text: str):
        self.should_translate = should_translate
        self.is_final_commit = is_final_commit
        self.reason = reason
        self.stable_text = stable_text

    def __repr__(self):
        return f"<CommitDecision translate={self.should_translate} final={self.is_final_commit} reason='{self.reason}'>"

class IntelligentCommitPolicy:
    """
    Intelligent Commit Policy for Streaming ASR.
    Prevents jittery, wasteful re-translations on every partial token.
    Evaluates:
      - Token threshold (MIN_TRANSLATION_TOKENS)
      - Sentence boundary / punctuation marks (. , ? ! |)
      - Silence duration (SILENCE_COMMIT_MS)
      - Maximum partial waiting latency (MAX_PARTIAL_WAIT_MS)
      - Partial stability score (repeated sequence agreement)
    """

    def __init__(
        self,
        min_tokens: int = settings.MIN_TRANSLATION_TOKENS,
        max_partial_wait_ms: int = settings.MAX_PARTIAL_WAIT_MS,
        silence_commit_ms: int = settings.SILENCE_COMMIT_MS,
        stability_threshold: float = settings.STABILITY_THRESHOLD
    ):
        self.min_tokens = min_tokens
        self.max_partial_wait_ms = max_partial_wait_ms
        self.silence_commit_ms = silence_commit_ms
        self.stability_threshold = stability_threshold

        self.last_text: str = ""
        self.last_update_time: float = time.time()
        self.first_token_time: Optional[float] = None
        self.committed_prefix: str = ""
        self.partial_history: List[str] = []

    def reset(self):
        self.last_text = ""
        self.last_update_time = time.time()
        self.first_token_time = None
        self.committed_prefix = ""
        self.partial_history.clear()

    def evaluate(self, current_partial: str, is_speech_final: bool = False, silence_duration_ms: float = 0.0) -> CommitDecision:
        now = time.time()
        current_text = current_partial.strip()

        if not current_text:
            return CommitDecision(False, False, "empty_text", "")

        # If speech ended (VAD or provider final)
        if is_speech_final:
            self.committed_prefix = current_text
            self.reset()
            return CommitDecision(True, True, "asr_final_event", current_text)

        if not self.first_token_time:
            self.first_token_time = now

        # Add to history for stability tracking
        self.partial_history.append(current_text)
        if len(self.partial_history) > 10:
            self.partial_history.pop(0)

        tokens = current_text.split()
        num_tokens = len(tokens)
        elapsed_since_start_ms = (now - self.first_token_time) * 1000
        elapsed_since_update_ms = (now - self.last_update_time) * 1000

        # Punctuation check (Sentence Boundary)
        punctuations = [".", "?", "!", "|", "।", "...", ","]
        has_terminal_punct = any(current_text.endswith(p) for p in [".", "?", "!", "।"])
        has_clause_punct = any(current_text.endswith(p) for p in [",", ";", "..."])

        # 1. Terminal punctuation commits immediately as final
        if has_terminal_punct and num_tokens >= self.min_tokens:
            self.committed_prefix = current_text
            self.first_token_time = None
            return CommitDecision(True, True, "terminal_punctuation_commit", current_text)

        # 2. Silence detection exceeded threshold
        if (silence_duration_ms >= self.silence_commit_ms or elapsed_since_update_ms >= self.silence_commit_ms) and num_tokens >= self.min_tokens:
            self.committed_prefix = current_text
            self.first_token_time = None
            return CommitDecision(True, True, "silence_timeout_commit", current_text)

        # 3. Maximum partial wait exceeded (force partial translation to keep latency low)
        if elapsed_since_start_ms >= self.max_partial_wait_ms and num_tokens >= self.min_tokens:
            return CommitDecision(True, False, "max_wait_latency_threshold", current_text)

        # 4. Clause punctuation (comma / pause) forces a safe partial translation
        if has_clause_punct and num_tokens >= self.min_tokens:
            return CommitDecision(True, False, "clause_boundary_punct", current_text)

        # 5. Stability check: if prefix is consistent across last 3 partials
        if len(self.partial_history) >= 3:
            common_prefix = self._calculate_common_prefix(self.partial_history[-3:])
            prefix_tokens = len(common_prefix.split())
            if prefix_tokens >= self.min_tokens and (prefix_tokens / max(1, num_tokens)) >= self.stability_threshold:
                # Text is stable enough for interim translation
                if current_text != self.last_text:
                    self.last_text = current_text
                    self.last_update_time = now
                    return CommitDecision(True, False, "stability_agreement_threshold", current_text)

        self.last_text = current_text
        self.last_update_time = now
        return CommitDecision(False, False, "buffering_partial", current_text)

    def _calculate_common_prefix(self, strings: List[str]) -> str:
        if not strings:
            return ""
        words_list = [s.split() for s in strings]
        min_len = min(len(w) for w in words_list)
        prefix = []
        for i in range(min_len):
            first_word = words_list[0][i].lower()
            if all(w[i].lower() == first_word for w in words_list):
                prefix.append(words_list[0][i])
            else:
                break
        return " ".join(prefix)
