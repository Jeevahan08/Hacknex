import React from 'react';
import { Mic, MicOff, Globe, PlayCircle } from 'lucide-react';
import { AudioWaveform } from './AudioWaveform';
import { INITIAL_LANGUAGES } from '../../types/language';

interface SourceTranscriptProps {
  sourceLanguage: string;
  setSourceLanguage: (lang: string) => void;
  isRecording: boolean;
  volumeLevel: number;
  toggleRecording: () => void;
  partialTranscript: string;
  committedTranscript: string;
  triggerDemoSentence: (sentence: string) => void;
}

export const SourceTranscript: React.FC<SourceTranscriptProps> = ({
  sourceLanguage,
  setSourceLanguage,
  isRecording,
  volumeLevel,
  toggleRecording,
  partialTranscript,
  committedTranscript,
  triggerDemoSentence
}) => {
  const currentLangObj = INITIAL_LANGUAGES.find((l) => l.code === sourceLanguage);

  const sampleSentences = [
    "Good morning everyone, today we are going to discuss artificial intelligence.",
    "I will be travelling to Chennai tomorrow.",
    "The train leaves at 10:30 AM.",
    "ISRO launched the satellite successfully."
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between h-full space-y-6">
      {/* Top Header & Language Selector */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Speaker Input</span>
          <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
            <span>{currentLangObj?.name || 'English'}</span>
            <span className="text-xs font-normal text-slate-500">({currentLangObj?.native_name})</span>
          </h2>
        </div>

        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-slate-400" />
          <select
            value={sourceLanguage}
            onChange={(e) => setSourceLanguage(e.target.value)}
            className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            {INITIAL_LANGUAGES.filter((l) => l.is_source).map((l) => (
              <option key={l.code} value={l.code}>
                {l.name} ({l.native_name})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Mic Action & Waveform */}
      <div className="flex flex-col items-center justify-center space-y-4 py-2">
        <button
          onClick={toggleRecording}
          className={`w-20 h-20 rounded-full flex items-center justify-center transition-all transform active:scale-95 shadow-lg ${
            isRecording
              ? 'bg-brand-600 text-white animate-mic-pulse ring-4 ring-brand-200'
              : 'bg-slate-900 text-white hover:bg-brand-700 hover:shadow-brand-500/25'
          }`}
          title={isRecording ? 'Click to stop listening' : 'Click to start microphone'}
        >
          {isRecording ? <Mic className="w-8 h-8" /> : <MicOff className="w-8 h-8" />}
        </button>

        <div className="text-center">
          <p className="text-xs font-semibold text-slate-700">
            {isRecording ? 'Listening and streaming...' : 'Click microphone to speak'}
          </p>
          <p className="text-[11px] text-slate-400">16kHz real-time PCM audio streaming</p>
        </div>

        <div className="w-full">
          <AudioWaveform isRecording={isRecording} volumeLevel={volumeLevel} />
        </div>
      </div>

      {/* Live Transcript Box */}
      <div className="flex-1 bg-slate-50/75 rounded-xl border border-slate-200 p-4 min-h-[160px] flex flex-col justify-between">
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Realtime Transcript
          </span>
          <div className="text-sm text-slate-800 leading-relaxed font-normal">
            {committedTranscript && (
              <span className="text-slate-900 font-medium">{committedTranscript} </span>
            )}
            {partialTranscript ? (
              <span className="text-brand-600/80 font-normal italic animate-pulse">
                {partialTranscript}
              </span>
            ) : !committedTranscript ? (
              <span className="text-slate-400 italic">
                Speech recognition transcript will appear here in real time...
              </span>
            ) : null}
          </div>
        </div>

        {/* Demo Sentence Triggers for instant judge walkthrough */}
        <div className="pt-4 border-t border-slate-200/60">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1">
            <PlayCircle className="w-3 h-3 text-brand-600" />
            <span>Judge Test Sentences:</span>
          </p>
          <div className="flex flex-wrap gap-1.5">
            {sampleSentences.map((sent, idx) => (
              <button
                key={idx}
                onClick={() => triggerDemoSentence(sent)}
                className="text-[11px] bg-white hover:bg-brand-50 text-slate-700 hover:text-brand-700 px-2.5 py-1 rounded-md border border-slate-200 transition-colors shadow-2xs"
              >
                "{sent.substring(0, 32)}..."
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
