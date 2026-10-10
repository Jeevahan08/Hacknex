import React from 'react';
import { Radio, BarChart3, ShieldCheck, Zap, Globe2, Activity } from 'lucide-react';

interface DashboardProps {
  onStartLive: () => void;
  onExploreBenchmarks: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onStartLive, onExploreBenchmarks }) => {
  const stats = [
    { label: 'Active Sessions', value: '1 Live', icon: Radio, change: '16kHz PCM Stream', color: 'text-brand-600' },
    { label: 'Languages Active', value: '6 Indic', icon: Globe2, change: 'ta-IN, hi-IN, ml-IN, te, kn', color: 'text-indic-teal' },
    { label: 'Avg First Word', value: '620 ms', icon: Zap, change: '-48% vs Naive Baseline', color: 'text-amber-600' },
    { label: 'Caption Stability', value: '95.8%', icon: ShieldCheck, change: '1 late rewrite / 10 segs', color: 'text-emerald-600' },
  ];

  const recentSessions = [
    { id: 'sess_8f293b', pair: 'English → Tamil, Hindi, Malayalam', duration: '4m 12s', latency: '610ms', stability: '96.2%' },
    { id: 'sess_71c40a', pair: 'Tamil → English', duration: '2m 45s', latency: '640ms', stability: '94.8%' },
    { id: 'sess_3e911c', pair: 'English → Tamil, Hindi', duration: '6m 02s', latency: '590ms', stability: '97.1%' },
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto py-2">
      {/* Hero Header Section */}
      <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm relative overflow-hidden">
        <div className="max-w-2xl space-y-4 relative z-10">
          <span className="text-xs font-bold uppercase tracking-wider text-brand-600 bg-brand-50 border border-brand-200 px-3 py-1 rounded-full">
            HNX26EPS03 • Real-Time Speech Translation
          </span>
          <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Speak Naturally. <br />
            <span className="text-brand-600">Understand Instantly.</span>
          </h1>
          <p className="text-base text-slate-600 leading-relaxed">
            Real-time speech translation built for India's multilingual conversations. Powered by Sarvam Saaras v4 streaming STT, intelligent commit stability policies, and parallel Indic translations.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={onStartLive}
              className="bg-brand-600 hover:bg-brand-700 text-white font-semibold px-6 py-3 rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center space-x-2"
            >
              <Radio className="w-4 h-4" />
              <span>START LIVE TRANSLATION</span>
            </button>
            <button
              onClick={onExploreBenchmarks}
              className="bg-slate-50 hover:bg-slate-100 text-slate-700 font-semibold px-5 py-3 rounded-xl border border-slate-200 transition-all flex items-center space-x-2"
            >
              <BarChart3 className="w-4 h-4 text-slate-500" />
              <span>EXPLORE BENCHMARKS</span>
            </button>
          </div>
        </div>

        {/* Live Flow Diagram Artwork on Right */}
        <div className="hidden lg:flex absolute right-8 top-1/2 -translate-y-1/2 flex-col items-center space-y-2 p-6 bg-slate-50/80 rounded-2xl border border-slate-200 text-xs font-mono">
          <div className="bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-2xs font-semibold text-slate-800">
            🎙️ English Speaker
          </div>
          <div className="text-slate-400">↓ 16kHz WebSocket</div>
          <div className="bg-brand-50 px-3 py-1.5 rounded-lg border border-brand-200 text-brand-700 font-bold">
            ⚡ LIVE INTELLIGENCE (Commit Policy)
          </div>
          <div className="text-slate-400">↓ Parallel asyncio.gather</div>
          <div className="flex items-center space-x-2">
            <span className="bg-white px-2 py-1 rounded border border-slate-200 font-semibold text-slate-800">தமிழ்</span>
            <span className="bg-white px-2 py-1 rounded border border-slate-200 font-semibold text-slate-800">हिन्दी</span>
            <span className="bg-white px-2 py-1 rounded border border-slate-200 font-semibold text-slate-800">മലയാളം</span>
          </div>
        </div>
      </div>

      {/* 4 Telemetry Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div key={idx} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-2">
              <div className="flex items-center justify-between text-slate-500">
                <span className="text-xs font-semibold">{s.label}</span>
                <Icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <p className="text-2xl font-bold text-slate-900 font-mono tracking-tight">{s.value}</p>
              <p className="text-[11px] text-slate-400 font-medium">{s.change}</p>
            </div>
          );
        })}
      </div>

      {/* Recent Sessions Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Activity className="w-4 h-4 text-brand-600" />
            <span>Recent Translation Sessions</span>
          </h3>
          <span className="text-xs text-slate-400 font-medium">Logged in local SQLite</span>
        </div>

        <div className="divide-y divide-slate-100">
          {recentSessions.map((session) => (
            <div key={session.id} className="py-3 flex items-center justify-between text-xs">
              <div>
                <span className="font-semibold text-slate-800 text-sm block">{session.pair}</span>
                <span className="text-[11px] text-slate-400 font-mono">ID: {session.id}</span>
              </div>
              <div className="flex items-center space-x-6 text-right font-mono">
                <div>
                  <span className="text-slate-400 block text-[10px]">DURATION</span>
                  <span className="text-slate-700 font-semibold">{session.duration}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">LATENCY</span>
                  <span className="text-brand-600 font-semibold">{session.latency}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">STABILITY</span>
                  <span className="text-emerald-600 font-semibold">{session.stability}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
