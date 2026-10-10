import React from 'react';
import { SourceTranscript } from '../components/translation/SourceTranscript';
import { PipelineIndicator } from '../components/translation/PipelineIndicator';
import { TranslationLane } from '../components/translation/TranslationLane';
import { CaptionHistory } from '../components/translation/CaptionHistory';
import { StreamDebugPanel } from '../components/translation/StreamDebugPanel';
import { TranslationLaneData, CaptionHistoryItem, PipelineStageEvent } from '../types/translation';
import { DebugInfo } from '../hooks/useLiveTranslation';

interface LiveTranslateProps {
  sourceLanguage: string;
  setSourceLanguage: (lang: string) => void;
  targetLanguages: string[];
  isRecording: boolean;
  volumeLevel: number;
  toggleRecording: () => void;
  partialTranscript: string;
  committedTranscript: string;
  currentStage: PipelineStageEvent;
  lanes: Record<string, TranslationLaneData>;
  captionHistory: CaptionHistoryItem[];
  firstWordLatency: number;
  finalLatency: number;
  stabilityScore: number;
  rewriteCount: number;
  sessionId: string;
  pipelineMode: string;
  triggerDemoSentence: (sentence: string) => void;
  playTTS: (text: string, language: string) => void;
  debugInfo?: DebugInfo;
}

export const LiveTranslate: React.FC<LiveTranslateProps> = ({
  sourceLanguage,
  setSourceLanguage,
  targetLanguages,
  isRecording,
  volumeLevel,
  toggleRecording,
  partialTranscript,
  committedTranscript,
  currentStage,
  lanes,
  captionHistory,
  firstWordLatency,
  finalLatency,
  stabilityScore,
  rewriteCount,
  sessionId,
  pipelineMode,
  triggerDemoSentence,
  playTTS,
  debugInfo
}) => {
  return (
    <div className="space-y-6">
      {/* Central Pipeline Flow Indicator */}
      <PipelineIndicator currentStage={currentStage} />

      {/* Main Translation Control Room Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Speaker Audio & Live Transcript */}
        <div className="lg:col-span-5 h-[580px]">
          <SourceTranscript
            sourceLanguage={sourceLanguage}
            setSourceLanguage={setSourceLanguage}
            isRecording={isRecording}
            volumeLevel={volumeLevel}
            toggleRecording={toggleRecording}
            partialTranscript={partialTranscript}
            committedTranscript={committedTranscript}
            triggerDemoSentence={triggerDemoSentence}
          />
        </div>

        {/* Right Column: 3 Parallel Translation Lanes (Tamil, Hindi, Malayalam) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Parallel Indic Translations (Simultaneous Execution)
            </span>
            <span className="text-xs text-brand-600 font-semibold font-mono">
              asyncio.gather [ta-IN, hi-IN, ml-IN]
            </span>
          </div>

          <div className="space-y-3">
            {targetLanguages.map((lang) => {
              const laneData = lanes[lang] || {
                language: lang,
                caption: '',
                status: 'final',
                firstWordLatencyMs: 0,
                finalLatencyMs: 0,
                stabilityScore: 1.0,
                rewrites: 0,
                lastUpdated: Date.now()
              };
              return (
                <TranslationLane
                  key={lang}
                  lane={laneData}
                  onPlayTTS={playTTS}
                />
              );
            })}
          </div>

          {/* Caption History Log */}
          <CaptionHistory history={captionHistory} />
        </div>
      </div>

      {/* Bottom Telemetry Debug Drawer */}
      <StreamDebugPanel
        sessionId={sessionId}
        firstWordLatency={firstWordLatency}
        finalLatency={finalLatency}
        stabilityScore={stabilityScore}
        rewriteCount={rewriteCount}
        pipelineMode={pipelineMode}
        debugInfo={debugInfo}
      />
    </div>
  );
};
