from typing import List, Dict, Any

class CaptionStabilityEngine:
    def __init__(self):
        self.partial_updates: int = 0
        self.committed_segments: int = 0
        self.late_rewrites: int = 0
        self.final_rewrites: int = 0
        self.last_committed_text: str = ""

    def reset(self):
        self.partial_updates = 0
        self.committed_segments = 0
        self.late_rewrites = 0
        self.final_rewrites = 0
        self.last_committed_text = ""

    def on_partial(self, text: str):
        self.partial_updates += 1

    def on_committed(self, text: str):
        self.committed_segments += 1
        # Check if previous committed segment was substantially rewritten
        if self.last_committed_text and self._is_late_rewrite(self.last_committed_text, text):
            self.late_rewrites += 1
        self.last_committed_text = text

    def on_final(self, text: str):
        if self.last_committed_text and self._is_late_rewrite(self.last_committed_text, text):
            self.final_rewrites += 1
        self.last_committed_text = text

    def _is_late_rewrite(self, prev: str, curr: str) -> bool:
        prev_words = prev.strip().split()
        curr_words = curr.strip().split()
        if not prev_words or not curr_words:
            return False
        # If words in prefix of curr differ from prev
        check_len = min(len(prev_words), len(curr_words))
        diff_count = sum(1 for i in range(check_len) if prev_words[i].lower() != curr_words[i].lower())
        return diff_count > 1  # More than 1 word rewritten in the committed prefix

    @property
    def stability_score(self) -> float:
        if self.committed_segments == 0:
            return 1.0
        penalty = self.late_rewrites / float(self.committed_segments)
        return max(0.0, min(1.0, 1.0 - penalty))

    @property
    def stability_pct(self) -> float:
        return round(self.stability_score * 100.0, 1)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "partial_updates": self.partial_updates,
            "committed_segments": self.committed_segments,
            "late_rewrites": self.late_rewrites,
            "final_rewrites": self.final_rewrites,
            "stability_score": round(self.stability_score, 3),
            "stability_pct": self.stability_pct
        }
