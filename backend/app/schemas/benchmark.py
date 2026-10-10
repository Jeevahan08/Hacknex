from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BenchmarkRunRequest(BaseModel):
    source_language: str = "en-IN"
    target_languages: List[str] = ["ta-IN", "hi-IN", "ml-IN"]
    mode: str = "fast"
    test_suite: str = "indiclive_standard"

class BenchmarkMetric(BaseModel):
    approach: str  # "Naive", "Buffered", "IndicLive"
    first_word_latency_ms: int
    final_latency_ms: int
    rewrites: int
    stability_pct: float
    asr_confidence_pct: float
    translation_success_pct: float
    is_simulated: bool = False

class BenchmarkRunResponse(BaseModel):
    run_id: str
    timestamp: float
    source_language: str
    target_languages: List[str]
    comparisons: List[BenchmarkMetric]
    details: List[Dict[str, Any]] = []
