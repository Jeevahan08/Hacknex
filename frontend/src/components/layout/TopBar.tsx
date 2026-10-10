import React from 'react';
import type { WSConnectionStatus } from '../../types/websocket';
import { Clock, Activity } from 'lucide-react';

interface TopBarProps {
  connectionStatus: WSConnectionStatus;
  sessionId: string;
  firstWordLatency: number;
  finalLatency: number;
  pipelineMode: string;
  setPipelineMode: (mode: string) => void;
  isDemo: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  connectionStatus,
  sessionId,
  firstWordLatency,
  finalLatency,
  pipelineMode,
  setPipelineMode,
  isDemo
}) => {
  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-emerald-600 bg-emerald-50 border-emerald-200';
      case 'connecting':
      case 'reconnecting':
        return 'text-amber-600 bg-amber-50 border-amber-200';
      default:
        return 'text-rose-600 bg-rose-50 border-rose-200';
    }
  };

  return (
    <header className="h-16 border-b border-slate-200 bg-white/95 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Brand Section */}
      <div className="flex items-center space-x-3">
        <img src="/logo.svg" alt="IndicLive" className="w-8 h-8 rounded-lg shadow-sm" />
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-900 tracking-tight text-lg">IndicLive</span>
            <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
              Control Room
            </span>
            {isDemo && (
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                Demo Mode
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 font-medium">Live Translation Intelligence</p>
        </div>
      </div>

      {/* Telemetry Center Info */}
      <div className="hidden lg:flex items-center space-x-6 text-xs text-slate-600 font-mono">
        <div className="flex items-center space-x-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
          <Clock className="w-3.5 h-3.5 text-brand-600" />
          <span>First Word:</span>
          <span className="font-bold text-slate-900">{firstWordLatency > 0 ? `${firstWordLatency} ms` : '—'}</span>
        </div>

        <div className="flex items-center space-x-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
          <Activity className="w-3.5 h-3.5 text-indic-teal" />
          <span>Final Sentence:</span>
          <span className="font-bold text-slate-900">{finalLatency > 0 ? `${(finalLatency / 1000).toFixed(2)} s` : '—'}</span>
        </div>

        <div className="flex items-center space-x-1.5 text-slate-500">
          <span>Session:</span>
          <span className="text-slate-800 font-semibold">{sessionId.substring(0, 12)}</span>
        </div>
      </div>

      {/* Right Controls: Mode Selector & Status */}
      <div className="flex items-center space-x-3">
        {/* Pipeline Mode Switcher */}
        <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs font-medium">
          <button
            onClick={() => setPipelineMode('fast')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              pipelineMode === 'fast'
                ? 'bg-white text-brand-700 shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="Minimum latency direct streaming"
          >
            Fast
          </button>
          <button
            onClick={() => setPipelineMode('balanced')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              pipelineMode === 'balanced'
                ? 'bg-white text-brand-700 shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="Entity protection & code-mixing enabled"
          >
            Balanced
          </button>
          <button
            onClick={() => setPipelineMode('quality')}
            className={`px-2.5 py-1 rounded-md transition-all ${
              pipelineMode === 'quality'
                ? 'bg-white text-brand-700 shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="LLM Quality check & correction enabled"
          >
            Quality
          </button>
        </div>

        {/* Live Status Badge */}
        <div className={`flex items-center space-x-1.5 px-3 py-1 rounded-full border text-xs font-medium ${getStatusColor()}`}>
          <span className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
          <span className="capitalize">{connectionStatus}</span>
        </div>
      </div>
    </header>
  );
};
