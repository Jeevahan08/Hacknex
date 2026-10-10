import React, { useState } from 'react';
import { Terminal, ChevronDown, ChevronUp, Wifi, Mic, Languages, Cpu, Activity } from 'lucide-react';
import { DebugInfo } from '../../hooks/useLiveTranslation';
import { INITIAL_LANGUAGES } from '../../types/language';

interface StreamDebugPanelProps {
  sessionId: string;
  firstWordLatency: number;
  finalLatency: number;
  stabilityScore: number;
  rewriteCount: number;
  pipelineMode: string;
  debugInfo?: DebugInfo;
}

const StatusDot: React.FC<{ active: boolean; label: string }> = ({ active, label }) => (
  <span className="flex items-center space-x-1">
    <span className={`w-2 h-2 rounded-full ${active ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
    <span className={active ? 'text-emerald-300' : 'text-slate-500'}>{label}</span>
  </span>
);

export const StreamDebugPanel: React.FC<StreamDebugPanelProps> = ({
  sessionId,
  firstWordLatency,
  finalLatency,
  stabilityScore,
  rewriteCount,
  pipelineMode,
  debugInfo
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const srcLang = INITIAL_LANGUAGES.find((l) => l.code === (debugInfo?.sourceLanguage || 'en-IN'));
  const tgtLangs = (debugInfo?.targetLanguages || ['ta-IN', 'hi-IN', 'ml-IN'])
    .map((code) => INITIAL_LANGUAGES.find((l) => l.code === code))
    .filter(Boolean);

  return (
    <div className="bg-slate-900 text-slate-200 rounded-2xl p-4 shadow-sm font-mono text-xs">
      <div
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-brand-400" />
          <span className="font-bold text-slate-100">Pipeline Debug Panel</span>
          <span className="text-[10px] bg-slate-800 text-brand-300 px-2 py-0.5 rounded border border-slate-700">
            {pipelineMode.toUpperCase()}
          </span>
          <StatusDot active={debugInfo?.micActive || false} label="MIC" />
          <StatusDot
            active={debugInfo?.wsStatus === 'connected'}
            label={debugInfo?.wsStatus?.toUpperCase() || 'DISCONNECTED'}
          />
        </div>
        <div className="flex items-center space-x-3 text-slate-400">
          <span>{firstWordLatency > 0 ? `${firstWordLatency}ms` : '—'} / {finalLatency > 0 ? `${finalLatency}ms` : '—'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>

      {isOpen && (
        <div className="mt-4 pt-3 border-t border-slate-800 space-y-3">
          {/* Row 1: Status grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 flex items-center space-x-1 mb-1">
                <Mic className="w-3 h-3" /><span>MIC</span>
              </span>
              <span className={`text-sm font-bold ${debugInfo?.micActive ? 'text-emerald-400' : 'text-slate-500'}`}>
                {debugInfo?.micActive ? 'ACTIVE' : 'INACTIVE'}
              </span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 flex items-center space-x-1 mb-1">
                <Wifi className="w-3 h-3" /><span>WEBSOCKET</span>
              </span>
              <span className={`text-sm font-bold ${
                debugInfo?.wsStatus === 'connected' ? 'text-emerald-400' :
                debugInfo?.wsStatus === 'reconnecting' ? 'text-amber-400' : 'text-red-400'
              }`}>
                {(debugInfo?.wsStatus || 'DISCONNECTED').toUpperCase()}
              </span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 flex items-center space-x-1 mb-1">
                <Cpu className="w-3 h-3" /><span>STT MODEL</span>
              </span>
              <span className="text-sm font-bold text-cyan-400">saaras:v4</span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 flex items-center space-x-1 mb-1">
                <Languages className="w-3 h-3" /><span>TRANSLATE</span>
              </span>
              <span className="text-sm font-bold text-purple-400">sarvam-translate:v1</span>
            </div>
          </div>

          {/* Row 2: Language config */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block mb-1">SOURCE LANGUAGE</span>
              <span className="text-sm font-bold text-slate-200">
                {srcLang?.name || debugInfo?.sourceLanguage} ({debugInfo?.sourceLanguage})
              </span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block mb-1">TARGET LANGUAGES</span>
              <span className="text-sm font-bold text-slate-200">
                {tgtLangs.map((l) => `${l?.name} (${l?.code})`).join(' · ')}
              </span>
            </div>
          </div>

          {/* Row 3: Last source/translation */}
          <div className="grid grid-cols-1 gap-2">
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block mb-1">LAST SOURCE (STT OUTPUT — should be source language text)</span>
              <span className="text-sm text-amber-300 break-all">
                {debugInfo?.lastSourceText || '—'}
              </span>
            </div>
            {Object.entries(debugInfo?.lastTranslations || {}).map(([lang, text]) => (
              <div key={lang} className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
                <span className="text-[10px] text-slate-400 block mb-1">LAST TRANSLATION → {lang}</span>
                <span className="text-sm text-emerald-300 break-all">{text || '—'}</span>
              </div>
            ))}
          </div>

          {/* Row 4: Counters */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block">AUDIO CHUNKS</span>
              <span className="text-sm font-bold text-emerald-400">{debugInfo?.audioChunks || 0}</span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block">PARTIALS</span>
              <span className="text-sm font-bold text-cyan-400">{debugInfo?.partialCount || 0}</span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block">COMMITS</span>
              <span className="text-sm font-bold text-brand-400">{debugInfo?.commitCount || 0}</span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block">SEGMENTS</span>
              <span className="text-sm font-bold text-purple-400">{debugInfo?.segmentCount || 0}</span>
            </div>
          </div>

          {/* Row 5: Latency */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block">FIRST WORD TIME</span>
              <span className="text-sm font-bold text-emerald-400">{firstWordLatency > 0 ? `${firstWordLatency}ms` : '—'}</span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block">FINAL LATENCY</span>
              <span className="text-sm font-bold text-cyan-400">{finalLatency > 0 ? `${finalLatency}ms` : '—'}</span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block">STABILITY SCORE</span>
              <span className="text-sm font-bold text-brand-400">{Math.round(stabilityScore * 100)}%</span>
            </div>
            <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
              <span className="text-[10px] text-slate-400 block">LATE REWRITES</span>
              <span className="text-sm font-bold text-amber-400">{rewriteCount}</span>
            </div>
          </div>

          <div className="text-[10px] text-slate-600 pt-1">
            Session: {sessionId} · Pipeline: {pipelineMode} · STT→Commit→Translate→Frontend
          </div>
        </div>
      )}
    </div>
  );
};
