import React from 'react';

interface AudioWaveformProps {
  isRecording: boolean;
  volumeLevel: number; // 0 to 1
}

export const AudioWaveform: React.FC<AudioWaveformProps> = ({ isRecording, volumeLevel }) => {
  const bars = 24;

  return (
    <div className="flex items-center justify-center space-x-1 h-12 px-4 bg-slate-50 rounded-xl border border-slate-200">
      {Array.from({ length: bars }).map((_, i) => {
        const factor = Math.sin((i / bars) * Math.PI);
        const dynamicHeight = isRecording
          ? Math.max(4, Math.min(36, 6 + volumeLevel * 40 * factor * (0.6 + Math.random() * 0.4)))
          : 4;

        return (
          <div
            key={i}
            className={`w-1 rounded-full transition-all duration-75 ${
              isRecording ? 'bg-brand-600' : 'bg-slate-300'
            }`}
            style={{ height: `${dynamicHeight}px` }}
          />
        );
      })}
    </div>
  );
};
