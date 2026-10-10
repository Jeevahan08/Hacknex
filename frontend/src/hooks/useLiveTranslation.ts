import { useState, useEffect, useRef, useCallback } from 'react';
import { liveWsClient } from '../services/websocket';
import { audioStreamService } from '../services/audio';
import { TranslationLaneData, CaptionHistoryItem, PipelineStageEvent } from '../types/translation';
import { WSConnectionStatus } from '../types/websocket';

export interface DebugInfo {
  micActive: boolean;
  wsStatus: WSConnectionStatus;
  sourceLanguage: string;
  targetLanguages: string[];
  sttMode: string;
  translationModel: string;
  lastSourceText: string;
  lastTranslations: Record<string, string>;
  segmentCount: number;
  audioChunks: number;
  partialCount: number;
  commitCount: number;
  lastTranslationLatencyMs: number;
}

export function useLiveTranslation() {
  const [sessionId] = useState<string>(() => `sess_${Math.random().toString(36).substring(2, 9)}`);
  const [connectionStatus, setConnectionStatus] = useState<WSConnectionStatus>('disconnected');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [volumeLevel, setVolumeLevel] = useState<number>(0);
  const [sourceLanguage, setSourceLanguage] = useState<string>('en-IN');
  const [targetLanguages, setTargetLanguages] = useState<string[]>(['ta-IN', 'hi-IN', 'ml-IN', 'mr-IN']);
  const [pipelineMode, setPipelineMode] = useState<string>('fast');
  const [enableTTS, setEnableTTS] = useState<boolean>(false);

  // Live Transcript — SEPARATE from translations
  // The source transcript MUST NEVER automatically populate the target translation field.
  const [partialTranscript, setPartialTranscript] = useState<string>('');
  const [committedTranscript, setCommittedTranscript] = useState<string>('');

  // Pipeline State & Stage
  const [currentStage, setCurrentStage] = useState<PipelineStageEvent>({ stage: 'mic', timestamp: Date.now() });

  // Target Translation Lanes — keyed by language code
  // IMPORTANT: These hold target-language translations, NOT source transcripts.
  const [lanes, setLanes] = useState<Record<string, TranslationLaneData>>({
    'ta-IN': {
      language: 'ta-IN',
      caption: '',
      status: 'final',
      firstWordLatencyMs: 0,
      finalLatencyMs: 0,
      stabilityScore: 1.0,
      rewrites: 0,
      lastUpdated: Date.now()
    },
    'hi-IN': {
      language: 'hi-IN',
      caption: '',
      status: 'final',
      firstWordLatencyMs: 0,
      finalLatencyMs: 0,
      stabilityScore: 1.0,
      rewrites: 0,
      lastUpdated: Date.now()
    },
    'ml-IN': {
      language: 'ml-IN',
      caption: '',
      status: 'final',
      firstWordLatencyMs: 0,
      finalLatencyMs: 0,
      stabilityScore: 1.0,
      rewrites: 0,
      lastUpdated: Date.now()
    },
    'mr-IN': {
      language: 'mr-IN',
      caption: '',
      status: 'final',
      firstWordLatencyMs: 0,
      finalLatencyMs: 0,
      stabilityScore: 1.0,
      rewrites: 0,
      lastUpdated: Date.now()
    }
  });

  // History of completed sentences
  const [captionHistory, setCaptionHistory] = useState<CaptionHistoryItem[]>([]);

  // Latency & Metrics telemetry
  const [firstWordLatency, setFirstWordLatency] = useState<number>(0);
  const [finalLatency, setFinalLatency] = useState<number>(0);
  const [stabilityScore, setStabilityScore] = useState<number>(1.0);
  const [rewriteCount, setRewriteCount] = useState<number>(0);

  // Debug info for the debug panel
  const [debugInfo, setDebugInfo] = useState<DebugInfo>({
    micActive: false,
    wsStatus: 'disconnected',
    sourceLanguage: 'en-IN',
    targetLanguages: ['ta-IN', 'hi-IN', 'ml-IN'],
    sttMode: 'TRANSCRIBE (saaras:v4)',
    translationModel: 'sarvam-translate:v1',
    lastSourceText: '',
    lastTranslations: {},
    segmentCount: 0,
    audioChunks: 0,
    partialCount: 0,
    commitCount: 0,
    lastTranslationLatencyMs: 0,
  });

  // Refs for values needed inside callbacks without causing re-renders
  const committedTranscriptRef = useRef<string>('');
  const sourceLanguageRef = useRef<string>('en-IN');
  const targetLanguagesRef = useRef<string[]>(['ta-IN', 'hi-IN', 'ml-IN']);
  const debugInfoRef = useRef<DebugInfo>(debugInfo);

  useEffect(() => { sourceLanguageRef.current = sourceLanguage; }, [sourceLanguage]);
  useEffect(() => { targetLanguagesRef.current = targetLanguages; }, [targetLanguages]);
  useEffect(() => { committedTranscriptRef.current = committedTranscript; }, [committedTranscript]);
  useEffect(() => { debugInfoRef.current = debugInfo; }, [debugInfo]);

  // Connect WebSocket on mount — stable dependency array to prevent reconnect loops
  useEffect(() => {
    liveWsClient.connect(sessionId);
    const unbindStatus = liveWsClient.onStatusChange((status) => {
      setConnectionStatus(status);
      setDebugInfo((prev) => ({ ...prev, wsStatus: status }));
    });

    const unbindMsg = liveWsClient.onMessage((msg) => {
      if (msg.type === 'pipeline.stage') {
        setCurrentStage({ stage: msg.stage, details: msg.details, timestamp: Date.now() });

      } else if (msg.type === 'transcript.partial') {
        // Source language partial — update transcript display only
        setPartialTranscript(msg.text);
        setDebugInfo((prev) => ({
          ...prev,
          partialCount: prev.partialCount + 1,
          lastSourceText: msg.text
        }));

      } else if (msg.type === 'transcript.committed') {
        // Source language final segment committed — preserve continuous transcript
        committedTranscriptRef.current = msg.text;
        setCommittedTranscript((prev) => (prev ? `${prev} ${msg.text}` : msg.text));
        setPartialTranscript('');
        setDebugInfo((prev) => ({
          ...prev,
          commitCount: prev.commitCount + 1,
          lastSourceText: msg.text
        }));

      } else if (msg.type === 'translation.partial') {
        // TARGET language partial translation — this is the translated text, NOT source text
        const lang = msg.target_language;
        setLanes((prev) => ({
          ...prev,
          [lang]: {
            ...(prev[lang] || { language: lang, rewrites: 0, stabilityScore: 1 }),
            caption: msg.text,
            status: 'partial',
            lastUpdated: Date.now()
          }
        }));

      } else if (msg.type === 'translation.final' || msg.type === 'translation.failed') {
        // TARGET language final or failed translation
        const lang = msg.target_language;
        const translatedText = msg.text;
        const isFailed = msg.type === 'translation.failed' || msg.status === 'failed' || translatedText?.startsWith('[TRANSLATION ERROR') || translatedText?.startsWith('[Translation unavailable');

        setFirstWordLatency(msg.first_word_latency_ms || 0);
        setFinalLatency(msg.final_latency_ms || 0);
        setStabilityScore(msg.stability_score ?? (isFailed ? 0 : 0.95));
        setRewriteCount(msg.rewrites ?? 0);

        setLanes((prev) => ({
          ...prev,
          [lang]: {
            language: lang,
            caption: translatedText,
            status: isFailed ? 'failed' : 'final',
            error: isFailed ? (msg.error || translatedText) : undefined,
            firstWordLatencyMs: msg.first_word_latency_ms || 0,
            finalLatencyMs: msg.final_latency_ms || 0,
            stabilityScore: msg.stability_score ?? (isFailed ? 0 : 0.95),
            rewrites: msg.rewrites ?? 0,
            lastUpdated: Date.now()
          }
        }));

        setDebugInfo((prev) => ({
          ...prev,
          segmentCount: prev.segmentCount + (lang === targetLanguagesRef.current[0] ? 1 : 0),
          lastTranslations: { ...prev.lastTranslations, [lang]: translatedText },
          lastTranslationLatencyMs: msg.final_latency_ms || 0,
        }));

        // Upsert into caption history: track all target languages per segment ID
        setCaptionHistory((prev) => {
          const segId = msg.segment_id || `seg_${Date.now()}`;
          const existingIdx = prev.findIndex((item) => item.segmentId === segId);
          if (existingIdx >= 0) {
            const updated = [...prev];
            updated[existingIdx] = {
              ...updated[existingIdx],
              translations: {
                ...updated[existingIdx].translations,
                [lang]: translatedText
              }
            };
            return updated;
          } else {
            return [
              {
                id: `cap_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
                segmentId: segId,
                sourceText: msg.source_text || committedTranscriptRef.current || '',
                sourceLanguage: sourceLanguageRef.current,
                translations: {
                  [lang]: translatedText
                },
                firstWordLatencyMs: msg.first_word_latency_ms || 0,
                finalLatencyMs: msg.final_latency_ms || 0,
                timestamp: Date.now()
              },
              ...prev.slice(0, 19)
            ];
          }
        });

      } else if (msg.type === 'tts.audio') {
        if (msg.audio_base64) {
          const snd = new Audio(`data:${msg.format || 'audio/wav'};base64,${msg.audio_base64}`);
          snd.play().catch((e) => console.log('Audio autoplay prevented:', e));
        }
      }
    });

    return () => {
      unbindStatus();
      unbindMsg();
      liveWsClient.disconnect();
      audioStreamService.stopCapture();
    };
  }, [sessionId]); // Only sessionId — stable, prevents reconnect loops on language change

  const startRecording = useCallback(async () => {
    try {
      // Send session.start with current language selection
      const currentSource = sourceLanguageRef.current;
      const currentTargets = targetLanguagesRef.current;

      console.log(`[Hook] Starting session: source=${currentSource} targets=${currentTargets.join(',')}`);

      liveWsClient.send({
        type: 'session.start',
        source_language: currentSource,
        target_languages: currentTargets,
        enable_tts: enableTTS,
        mode: pipelineMode
      });

      // Reset transcript state for new session
      setCommittedTranscript('');
      setPartialTranscript('');
      committedTranscriptRef.current = '';
      setLanes((prev) => {
        const reset: Record<string, TranslationLaneData> = {};
        currentTargets.forEach((lang) => {
          reset[lang] = {
            language: lang,
            caption: '',
            status: 'final',
            firstWordLatencyMs: 0,
            finalLatencyMs: 0,
            stabilityScore: 1.0,
            rewrites: 0,
            lastUpdated: Date.now()
          };
        });
        return { ...prev, ...reset };
      });

      setDebugInfo((prev) => ({
        ...prev,
        micActive: true,
        sourceLanguage: currentSource,
        targetLanguages: currentTargets,
        audioChunks: 0,
        partialCount: 0,
        commitCount: 0,
        segmentCount: 0,
        lastSourceText: '',
        lastTranslations: {},
      }));

      // Start PCM audio capture — sends audio.chunk messages to backend for Sarvam STT
      await audioStreamService.startCapture(
        currentSource,
        (chunkB64) => {
          liveWsClient.send({
            type: 'audio.chunk',
            data: chunkB64
          });
          setDebugInfo((prev) => ({ ...prev, audioChunks: prev.audioChunks + 1 }));
        },
        (vol) => {
          setVolumeLevel(vol);
        }
        // NOTE: No transcript callback — transcription goes through backend Sarvam STT only
      );

      setIsRecording(true);
    } catch (err) {
      console.error('[Hook] Failed to start recording:', err);
      setIsRecording(false);
    }
  }, [enableTTS, pipelineMode]); // sourceLanguage and targetLanguages accessed via refs

  const stopRecording = useCallback(() => {
    audioStreamService.stopCapture();
    setIsRecording(false);
    setVolumeLevel(0);
    setDebugInfo((prev) => ({ ...prev, micActive: false }));
    liveWsClient.send({ type: 'session.stop' });
    console.log('[Hook] Session stopped');
  }, []);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  const triggerDemoSentence = useCallback((sentence: string) => {
    const currentSource = sourceLanguageRef.current;
    const currentTargets = targetLanguagesRef.current;

    // Reset translation lanes before demo
    setLanes((prev) => {
      const reset: Record<string, TranslationLaneData> = {};
      currentTargets.forEach((lang) => {
        reset[lang] = {
          language: lang,
          caption: '',
          status: 'final',
          firstWordLatencyMs: 0,
          finalLatencyMs: 0,
          stabilityScore: 1.0,
          rewrites: 0,
          lastUpdated: Date.now()
        };
      });
      return { ...prev, ...reset };
    });
    setCommittedTranscript('');
    setPartialTranscript('');
    committedTranscriptRef.current = '';

    liveWsClient.send({
      type: 'session.start',
      source_language: currentSource,
      target_languages: currentTargets,
      enable_tts: enableTTS,
      mode: pipelineMode
    });

    liveWsClient.send({
      type: 'demo.trigger',
      sentence,
      delay_ms: 220
    });
  }, [enableTTS, pipelineMode]);

  const playTTS = useCallback((text: string, language: string) => {
    import('../services/api').then(({ apiService }) => {
      apiService.synthesizeTTS({ text, language }).then((res) => {
        if (res.audio_base64) {
          const snd = new Audio(`data:audio/wav;base64,${res.audio_base64}`);
          snd.play();
        }
      }).catch(console.error);
    });
  }, []);

  return {
    sessionId,
    connectionStatus,
    isRecording,
    volumeLevel,
    sourceLanguage,
    setSourceLanguage,
    targetLanguages,
    setTargetLanguages,
    pipelineMode,
    setPipelineMode,
    enableTTS,
    setEnableTTS,
    partialTranscript,
    committedTranscript,
    currentStage,
    lanes,
    captionHistory,
    firstWordLatency,
    finalLatency,
    stabilityScore,
    rewriteCount,
    debugInfo,
    toggleRecording,
    triggerDemoSentence,
    playTTS
  };
}
