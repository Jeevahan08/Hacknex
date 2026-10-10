import React from 'react';
import { Mic, AudioLines, GitCommit, ArrowRight, Languages, CheckCircle2 } from 'lucide-react';
import { PipelineStageEvent } from '../../types/translation';

interface PipelineIndicatorProps {
  currentStage: PipelineStageEvent;
}

export const PipelineIndicator: React.FC<PipelineIndicatorProps> = ({ currentStage }) => {
  const stages = [
    { id: 'mic', label: 'Mic Input', icon: Mic },
    { id: 'listening', label: 'Speech Stream', icon: AudioLines },
    { id: 'transcribing', label: 'ASR Partial', icon: Languages },
    { id: 'commit', label: 'Meaning Commit', icon: GitCommit },
    { id: 'translating', label: 'Parallel Translate', icon: ArrowRight },
    { id: 'final', label: 'Stable Caption', icon: CheckCircle2 },
  ];

  const getStageIndex = (stage: string) => {
    switch (stage) {
      case 'mic': return 0;
      case 'listening': return 1;
      case 'transcribing': return 2;
      case 'commit': return 3;
      case 'translating': return 4;
      case 'final': return 5;
      default: return 0;
    }
  };

  const currentIndex = getStageIndex(currentStage.stage);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row items-center justify-between gap-2 overflow-x-auto">
      {stages.map((st, idx) => {
        const Icon = st.icon;
        const isActive = idx === currentIndex;
        const isPassed = idx < currentIndex;

        return (
          <React.Fragment key={st.id}>
            <div className="flex items-center space-x-2.5 shrink-0">
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20 ring-2 ring-brand-300'
                    : isPassed
                    ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                    : 'bg-slate-100 text-slate-400 border border-slate-200'
                }`}
              >
                <Icon className="w-4 h-4" />
              </div>
              <div className="text-left">
                <p className={`text-xs font-semibold ${isActive ? 'text-brand-900 font-bold' : isPassed ? 'text-slate-800' : 'text-slate-400'}`}>
                  {st.label}
                </p>
                <p className="text-[10px] text-slate-400 capitalize">
                  {isActive ? 'Active processing' : isPassed ? 'Completed' : 'Pending'}
                </p>
              </div>
            </div>

            {idx < stages.length - 1 && (
              <div className="hidden md:flex items-center text-slate-300 px-1">
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
