import React, { useState } from 'react';
import { Sliders, Cpu, Volume2, Info } from 'lucide-react';

export const Settings: React.FC = () => {
  const [aiMode, setAiMode] = useState('fast');
  const [minTokens, setMinTokens] = useState(3);
  const [maxWaitMs, setMaxWaitMs] = useState(1200);
  const [silenceMs, setSilenceMs] = useState(450);
  const [stabilityThresh, setStabilityThresh] = useState(0.80);
  const [enableTTS, setEnableTTS] = useState(false);
  const [ttsVoice, setTtsVoice] = useState('ananya');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <span className="text-xs font-bold uppercase tracking-wider text-brand-600 bg-brand-50 px-2.5 py-0.5 rounded-full border border-brand-200">
          Configuration & Engine Tuning
        </span>
        <h2 className="text-xl font-bold text-slate-900 mt-1">Platform Settings</h2>
        <p className="text-xs text-slate-500">
          Fine-tune the intelligent commit policy, AI orchestration layer, and model parameters.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* AI Processing Mode */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-brand-600" />
            <span>AI Orchestration Mode</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div
              onClick={() => setAiMode('fast')}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                aiMode === 'fast'
                  ? 'border-brand-500 bg-brand-50/50 ring-2 ring-brand-200'
                  : 'border-slate-200 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-xs text-slate-900">Fast Mode</span>
                <span className="text-[10px] bg-brand-100 text-brand-800 px-1.5 py-0.5 rounded font-mono font-bold">~600ms</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-normal">
                Direct Saaras v4 STT → Sarvam Translate. LLM disabled for ultra-low latency.
              </p>
            </div>

            <div
              onClick={() => setAiMode('balanced')}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                aiMode === 'balanced'
                  ? 'border-brand-500 bg-brand-50/50 ring-2 ring-brand-200'
                  : 'border-slate-200 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-xs text-slate-900">Balanced Mode</span>
                <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-mono font-bold">~800ms</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-normal">
                Entity protection & code-mixing active. Sarvam-105B triggered for ambiguous terms.
              </p>
            </div>

            <div
              onClick={() => setAiMode('quality')}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                aiMode === 'quality'
                  ? 'border-brand-500 bg-brand-50/50 ring-2 ring-brand-200'
                  : 'border-slate-200 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-xs text-slate-900">Quality Mode</span>
                <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-mono font-bold">~1.2s</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-normal">
                Post-translation LLM quality validation and error correction enabled on final captions.
              </p>
            </div>
          </div>
        </div>

        {/* Commit Policy Thresholds */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-indic-teal" />
            <span>Intelligent Commit Policy Thresholds</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5">
              <label className="font-semibold text-slate-700 flex justify-between">
                <span>Minimum Translation Tokens:</span>
                <span className="font-mono text-brand-600 font-bold">{minTokens} tokens</span>
              </label>
              <input
                type="range"
                min="1"
                max="8"
                value={minTokens}
                onChange={(e) => setMinTokens(Number(e.target.value))}
                className="w-full accent-brand-600"
              />
              <p className="text-[10px] text-slate-400">Tokens required before partial translation triggers.</p>
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-slate-700 flex justify-between">
                <span>Max Partial Wait (Latency Ceiling):</span>
                <span className="font-mono text-brand-600 font-bold">{maxWaitMs} ms</span>
              </label>
              <input
                type="range"
                min="500"
                max="3000"
                step="100"
                value={maxWaitMs}
                onChange={(e) => setMaxWaitMs(Number(e.target.value))}
                className="w-full accent-brand-600"
              />
              <p className="text-[10px] text-slate-400">Force partial translation if sentence continues uncommitted.</p>
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-slate-700 flex justify-between">
                <span>Silence Commit Threshold:</span>
                <span className="font-mono text-brand-600 font-bold">{silenceMs} ms</span>
              </label>
              <input
                type="range"
                min="200"
                max="1000"
                step="50"
                value={silenceMs}
                onChange={(e) => setSilenceMs(Number(e.target.value))}
                className="w-full accent-brand-600"
              />
              <p className="text-[10px] text-slate-400">Speaker pause duration that commits previous utterance.</p>
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-slate-700 flex justify-between">
                <span>Partial Stability Threshold:</span>
                <span className="font-mono text-brand-600 font-bold">{Math.round(stabilityThresh * 100)}%</span>
              </label>
              <input
                type="range"
                min="0.5"
                max="0.99"
                step="0.05"
                value={stabilityThresh}
                onChange={(e) => setStabilityThresh(Number(e.target.value))}
                className="w-full accent-brand-600"
              />
              <p className="text-[10px] text-slate-400">Prefix repetition agreement threshold across ASR interim frames.</p>
            </div>
          </div>
        </div>

        {/* TTS Settings */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Volume2 className="w-4 h-4 text-amber-600" />
            <span>Text-to-Speech (Bulbul v3)</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs items-center">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="enableTTS"
                checked={enableTTS}
                onChange={(e) => setEnableTTS(e.target.checked)}
                className="w-4 h-4 text-brand-600 rounded border-slate-300 focus:ring-brand-500"
              />
              <label htmlFor="enableTTS" className="font-semibold text-slate-700 cursor-pointer">
                Automatically speak completed final captions
              </label>
            </div>

            <div className="space-y-1">
              <label className="font-semibold text-slate-700">Voice Speaker Profile:</label>
              <select
                value={ttsVoice}
                onChange={(e) => setTtsVoice(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs text-slate-800"
              >
                <option value="ananya">Ananya (Female • Fluent Standard)</option>
                <option value="aravind">Aravind (Male • Formal Deep)</option>
                <option value="priya">Priya (Female • Colloquial Expressive)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Security / API Note */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-start space-x-3 text-xs text-slate-600">
          <Info className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" />
          <p>
            <strong>Security Architecture:</strong> API keys are safely managed in <code className="bg-slate-200/80 px-1 py-0.5 rounded text-slate-800">backend/.env</code>. The browser client never touches or stores API credentials.
          </p>
        </div>

        <button
          type="submit"
          className="bg-brand-600 hover:bg-brand-700 text-white font-semibold px-6 py-2.5 rounded-xl text-xs transition-colors shadow-sm"
        >
          {saved ? 'Settings Saved!' : 'Save Configuration'}
        </button>
      </form>
    </div>
  );
};
