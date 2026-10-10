import React from 'react';
import { 
  Radio, 
  MessageSquare, 
  BookOpen, 
  BarChart3, 
  Settings, 
  Cpu
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  apiHealth: string;
  modelStatus: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  apiHealth,
  modelStatus
}) => {
  const navItems = [
    { id: 'translate', label: 'Live Translate', icon: Radio },
    { id: 'conversation', label: 'Conversation', icon: MessageSquare },
    { id: 'glossary', label: 'Glossary', icon: BookOpen },
    { id: 'benchmark', label: 'Benchmarks', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-200 bg-white flex flex-col justify-between shrink-0 select-none">
      <div className="p-4 space-y-6">
        {/* Navigation list */}
        <div className="space-y-1">
          <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Workspace
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 shadow-sm border border-brand-100 font-semibold'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        {/* AI Pipeline Architecture Box */}
        <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-2.5">
          <div className="flex items-center justify-between font-semibold text-slate-700">
            <span className="flex items-center space-x-1.5">
              <Cpu className="w-3.5 h-3.5 text-brand-600" />
              <span>AI Stack</span>
            </span>
            <span className="text-[10px] text-emerald-600 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
              {modelStatus}
            </span>
          </div>
          <div className="space-y-1.5 text-[11px] text-slate-500">
            <div className="flex justify-between items-center">
              <span>ASR:</span>
              <span className="font-mono text-slate-800 font-medium">Saaras v4</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Translation:</span>
              <span className="font-mono text-slate-800 font-medium">Sarvam v1</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Context/LLM:</span>
              <span className="font-mono text-slate-800 font-medium">Sarvam-105B</span>
            </div>
            <div className="flex justify-between items-center">
              <span>TTS:</span>
              <span className="font-mono text-slate-800 font-medium">Bulbul v3</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/50 space-y-2 text-xs">
        <div className="flex items-center justify-between text-slate-500 text-[11px]">
          <span>WS Health</span>
          <span className="flex items-center space-x-1 text-emerald-600 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span className="capitalize">{apiHealth}</span>
          </span>
        </div>
        <div className="flex items-center justify-between text-slate-500 text-[11px]">
          <span>Database</span>
          <span className="font-medium text-slate-700">SQLite Async</span>
        </div>
        <div className="pt-1 text-[10px] text-slate-400 text-center">
          IndicLive Intelligence • v1.0.0
        </div>
      </div>
    </aside>
  );
};
