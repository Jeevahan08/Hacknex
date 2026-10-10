import React, { useState } from 'react';
import { Mic, Volume2, ArrowLeftRight, Clock } from 'lucide-react';
import { INITIAL_LANGUAGES } from '../types/language';
import { apiService } from '../services/api';

interface Turn {
  id: string;
  speaker: 'Speaker A' | 'Speaker B';
  sourceLanguage: string;
  targetLanguage: string;
  originalText: string;
  translatedText: string;
  latencyMs: number;
  timestamp: number;
}

export const Conversation: React.FC = () => {
  const [langA, setLangA] = useState('en-IN');
  const [langB, setLangB] = useState('ta-IN');
  const [activeSpeaker, setActiveSpeaker] = useState<'A' | 'B'>('A');
  const [inputText, setInputText] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);

  const [conversationHistory, setConversationHistory] = useState<Turn[]>([
    {
      id: 'turn_1',
      speaker: 'Speaker A',
      sourceLanguage: 'en-IN',
      targetLanguage: 'ta-IN',
      originalText: 'Hello, welcome to Chennai! How was your journey?',
      translatedText: 'வணக்கம், சென்னைக்கு நல்வரவு! உங்கள் பயணம் எப்படி இருந்தது?',
      latencyMs: 580,
      timestamp: Date.now() - 60000
    },
    {
      id: 'turn_2',
      speaker: 'Speaker B',
      sourceLanguage: 'ta-IN',
      targetLanguage: 'en-IN',
      originalText: 'பயணம் மிகவும் நன்றாக இருந்தது, நன்றி.',
      translatedText: 'The journey was very good, thank you.',
      latencyMs: 610,
      timestamp: Date.now() - 30000
    }
  ]);

  const handleSpeak = async (phrase?: string) => {
    const textToTranslate = phrase || inputText;
    if (!textToTranslate.trim()) return;

    setIsTranslating(true);
    const src = activeSpeaker === 'A' ? langA : langB;
    const tgt = activeSpeaker === 'A' ? langB : langA;
    const speakerLabel = activeSpeaker === 'A' ? 'Speaker A' : 'Speaker B';

    try {
      const res = await apiService.translateText({
        source_language: src,
        target_languages: [tgt],
        text: textToTranslate
      });

      const targetResult = res.translations[tgt];
      const trans = targetResult?.translated_text && targetResult.status !== 'failed' && !targetResult.translated_text.startsWith('[TRANSLATION ERROR')
        ? targetResult.translated_text
        : `[Translation unavailable for ${tgt}]`;

      const turn: Turn = {
        id: `turn_${Date.now()}`,
        speaker: speakerLabel,
        sourceLanguage: src,
        targetLanguage: tgt,
        originalText: textToTranslate,
        translatedText: trans,
        latencyMs: res.total_latency_ms || 600,
        timestamp: Date.now()
      };

      setConversationHistory((prev) => [...prev, turn]);
      setInputText('');
      // Alternate speaker
      setActiveSpeaker(activeSpeaker === 'A' ? 'B' : 'A');
    } catch (err) {
      console.error(err);
      const turn: Turn = {
        id: `turn_${Date.now()}`,
        speaker: speakerLabel,
        sourceLanguage: src,
        targetLanguage: tgt,
        originalText: textToTranslate,
        translatedText: `[Translation failed: ${(err as Error)?.message || 'network error'}]`,
        latencyMs: 0,
        timestamp: Date.now()
      };
      setConversationHistory((prev) => [...prev, turn]);
    } finally {
      setIsTranslating(false);
    }
  };

  const playTTS = (text: string, lang: string) => {
    apiService.synthesizeTTS({ text, language: lang }).then((res) => {
      if (res.audio_base64) {
        new Audio(`data:audio/wav;base64,${res.audio_base64}`).play();
      }
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-brand-600 bg-brand-50 px-2.5 py-0.5 rounded-full border border-brand-200">
            Stretch Feature
          </span>
          <h2 className="text-xl font-bold text-slate-900 mt-1">Two-Way Conversation Mode</h2>
          <p className="text-xs text-slate-500">Bilingual dialogue translation with automatic speaker turn-taking</p>
        </div>

        {/* Language selectors for A & B */}
        <div className="flex items-center space-x-3 bg-slate-50 p-2 rounded-xl border border-slate-200">
          <div className="text-center">
            <span className="text-[10px] text-slate-400 block font-bold">SPEAKER A</span>
            <select
              value={langA}
              onChange={(e) => setLangA(e.target.value)}
              className="text-xs font-semibold bg-white border border-slate-200 rounded px-2 py-1 text-slate-800"
            >
              {INITIAL_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>

          <ArrowLeftRight className="w-4 h-4 text-brand-600 shrink-0" />

          <div className="text-center">
            <span className="text-[10px] text-slate-400 block font-bold">SPEAKER B</span>
            <select
              value={langB}
              onChange={(e) => setLangB(e.target.value)}
              className="text-xs font-semibold bg-white border border-slate-200 rounded px-2 py-1 text-slate-800"
            >
              {INITIAL_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Conversation Thread */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm min-h-[380px] max-h-[500px] overflow-y-auto space-y-4">
        {conversationHistory.map((turn) => {
          const isA = turn.speaker === 'Speaker A';
          return (
            <div key={turn.id} className={`flex flex-col ${isA ? 'items-start' : 'items-end'}`}>
              <div className="flex items-center space-x-2 text-[11px] text-slate-400 mb-1 px-1">
                <span className="font-bold text-slate-700">{turn.speaker}</span>
                <span>• {turn.sourceLanguage} → {turn.targetLanguage}</span>
                <span className="flex items-center space-x-0.5 font-mono text-brand-600">
                  <Clock className="w-3 h-3" />
                  <span>{turn.latencyMs}ms</span>
                </span>
              </div>

              <div
                className={`max-w-md p-4 rounded-2xl space-y-2 shadow-2xs ${
                  isA
                    ? 'bg-slate-50 border border-slate-200 text-slate-900 rounded-tl-sm'
                    : 'bg-brand-50 border border-brand-200 text-brand-950 rounded-tr-sm'
                }`}
              >
                <p className="text-xs text-slate-500 italic">"{turn.originalText}"</p>
                <div className="flex items-center justify-between pt-1 border-t border-slate-200/50">
                  <p className="text-sm font-semibold">{turn.translatedText}</p>
                  <button
                    onClick={() => playTTS(turn.translatedText, turn.targetLanguage)}
                    className="p-1 text-slate-400 hover:text-brand-600"
                    title="Play audio"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Input Controls */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex items-center space-x-3">
        <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setActiveSpeaker('A')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeSpeaker === 'A' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'
            }`}
          >
            Speaker A
          </button>
          <button
            onClick={() => setActiveSpeaker('B')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeSpeaker === 'B' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-500'
            }`}
          >
            Speaker B
          </button>
        </div>

        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSpeak()}
          placeholder={`Type or speak for ${activeSpeaker === 'A' ? 'Speaker A' : 'Speaker B'}...`}
          className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />

        <button
          onClick={() => handleSpeak()}
          disabled={isTranslating || !inputText.trim()}
          className="bg-brand-600 hover:bg-brand-700 text-white font-semibold px-5 py-2.5 rounded-xl disabled:opacity-40 transition-colors flex items-center space-x-1.5 text-sm"
        >
          <Mic className="w-4 h-4" />
          <span>{isTranslating ? 'Translating...' : 'Translate Turn'}</span>
        </button>
      </div>
    </div>
  );
};
