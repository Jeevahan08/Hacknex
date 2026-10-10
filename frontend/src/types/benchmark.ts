export interface BenchmarkMetric {
  approach: string;
  first_word_latency_ms: number;
  final_latency_ms: number;
  rewrites: number;
  stability_pct: number;
  asr_confidence_pct: number;
  translation_success_pct: number;
  is_simulated: boolean;
}

export interface BenchmarkRunResponse {
  run_id: string;
  timestamp: number;
  source_language: string;
  target_languages: string[];
  comparisons: BenchmarkMetric[];
  details: Array<{
    test_sentence: string;
    naive_rewrites: number;
    indiclive_rewrites: number;
    indiclive_first_word_ms: number;
    buffered_first_word_ms: number;
  }>;
}
