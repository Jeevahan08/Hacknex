import React from 'react';
import { Volume2, CheckCircle2, Clock, Activity, ShieldCheck, AlertCircle } from 'lucide-react';
import { TranslationLaneData } from '../../types/translation';
import { INITIAL_LANGUAGES } from '../../types/language';

interface TranslationLaneProps {
  lane: TranslationLaneData;
  onPlayTTS: (text: string, language: string) => void;
}

export const TranslationLane: React.FC<TranslationLaneProps> = ({ lane, onPlayTTS }) => {
  const langMeta = INITIAL_LANGUAGES.find((l) => l.code === lane.language);

  const getStatusBadge = () => {
    switch (lane.status) {
      case 'final':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-2.5 h-2.5" />
            <span>Final</span>
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <AlertCircle className="w-2.5 h-2.5" />
            <span>Failed</span>
          </span>
        );
      case 'committed':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-brand-50 text-brand-700 border border-brand-200">
            <Activity className="w-2.5 h-2.5" />
            <span>Committed</span>
          </span>
        );
      case 'partial':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200 animate-pulse">
            <span>Interim...</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4">
      {/* Header Info */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center font-bold text-slate-800 text-sm">
            {lane.language.split('-')[0].toUpperCase()}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-900 text-base">{langMeta?.native_name || lane.language}</span>
              <span className="text-xs text-slate-400 font-medium">({langMeta?.name})</span>
            </div>
            <span className="text-[10px] font-mono text-slate-400">{lane.language}</span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {getStatusBadge()}
          <button
            onClick={() => onPlayTTS(lane.caption, lane.language)}
            disabled={!lane.caption}
            className="p-1.5 rounded-lg text-slate-500 hover:text-brand-600 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            title="Play Bulbul v3 TTS voice"
          >
            <Volume2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Translated Caption Body */}
      <div className="min-h-[70px] flex items-center bg-slate-50/50 p-3.5 rounded-xl border border-slate-100">
        <p
          className={`text-base leading-relaxed ${
            lane.status === 'partial'
              ? 'text-brand-700/80 font-normal italic'
              : lane.status === 'committed'
              ? 'text-slate-800 font-medium'
              : 'text-slate-900 font-semibold'
          }`}
        >
          {lane.caption || (
            <span className="text-slate-400 font-normal italic text-sm">
              Live translation in {langMeta?.name || lane.language} will appear here...
            </span>
          )}
        </p>
      </div>

      {/* Latency & Stability Chips Footer */}
      <div className="flex flex-wrap items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 font-mono gap-2">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1" title="First-Word Latency">
            <Clock className="w-3 h-3 text-brand-600" />
            <span>1st:</span>
            <span className="font-semibold text-slate-800">
              {lane.firstWordLatencyMs > 0 ? `${lane.firstWordLatencyMs}ms` : '—'}
            </span>
          </span>

          <span className="flex items-center space-x-1" title="End of speech to Final Latency">
            <Activity className="w-3 h-3 text-indic-teal" />
            <span>Final:</span>
            <span className="font-semibold text-slate-800">
              {lane.finalLatencyMs > 0 ? `${lane.finalLatencyMs}ms` : '—'}
            </span>
          </span>
        </div>

        <div className="flex items-center space-x-1 text-[11px] bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
          <ShieldCheck className="w-3 h-3 text-emerald-600" />
          <span>Stability:</span>
          <span className="font-bold text-slate-800">
            {Math.round(lane.stabilityScore * 100)}%
          </span>
        </div>
      </div>
    </div>
  );
};
