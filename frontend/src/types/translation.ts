export type CaptionState = 'partial' | 'committed' | 'final' | 'failed' | 'translating';

export interface TranslationLaneData {
  language: string;
  caption: string;
  status: CaptionState;
  error?: string;
  firstWordLatencyMs: number;
  finalLatencyMs: number;
  stabilityScore: number;
  rewrites: number;
  lastUpdated: number;
}

export interface CaptionHistoryItem {
  id: string;
  segmentId: string;
  sourceText: string;
  sourceLanguage: string;
  translations: Record<string, string>;
  firstWordLatencyMs: number;
  finalLatencyMs: number;
  timestamp: number;
}

export interface PipelineStageEvent {
  stage: 'mic' | 'listening' | 'transcribing' | 'commit' | 'translating' | 'final' | 'generating_speech' | 'translation_failed' | 'voice_failed';
  details?: string;
  timestamp: number;
}
