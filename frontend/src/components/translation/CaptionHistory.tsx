import React from 'react';
import { History } from 'lucide-react';
import type { CaptionHistoryItem } from '../../types/translation';

interface CaptionHistoryProps {
  history: CaptionHistoryItem[];
}

export const CaptionHistory: React.FC<CaptionHistoryProps> = ({ history }) => {
  if (history.length === 0) return null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
      <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-500">
        <History className="w-3.5 h-3.5 text-slate-400" />
        <span>Recent Caption Stream History</span>
      </div>

      <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
        {history.map((item) => (
          <div
            key={item.id}
            className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 text-xs space-y-1.5"
          >
            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
              <span>1st: {item.firstWordLatencyMs}ms • Final: {item.finalLatencyMs}ms</span>
            </div>
            <p className="text-slate-800 font-medium">"{item.sourceText}"</p>
            <div className="flex flex-wrap gap-2 pt-1 border-t border-slate-200/50">
              {Object.entries(item.translations).map(([lang, trans]) => (
                <div key={lang} className="text-[11px] text-brand-800 bg-brand-50 px-2 py-0.5 rounded border border-brand-100 flex items-center space-x-1">
                  <span className="font-bold text-brand-600">{lang.split('-')[0].toUpperCase()}:</span>
                  <span>{trans}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
