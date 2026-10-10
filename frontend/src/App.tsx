import React, { useState } from 'react';
import { TopBar } from './components/layout/TopBar';
import { Sidebar } from './components/layout/Sidebar';
import { LiveTranslate } from './pages/LiveTranslate';
import { Dashboard } from './pages/Dashboard';
import { Conversation } from './pages/Conversation';
import { Glossary } from './pages/Glossary';
import { Benchmark } from './pages/Benchmark';
import { Settings } from './pages/Settings';
import { useLiveTranslation } from './hooks/useLiveTranslation';
import { apiService } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('translate');
  const [isDemo, setIsDemo] = useState<boolean>(false);

  React.useEffect(() => {
    apiService.getHealth().then((h) => {
      if (h.demo_mode !== undefined) {
        setIsDemo(h.demo_mode);
      }
    }).catch(() => {});
  }, []);

  const {
    sessionId,
    connectionStatus,
    isRecording,
    volumeLevel,
    sourceLanguage,
    setSourceLanguage,
    targetLanguages,
    pipelineMode,
    setPipelineMode,
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
  } = useLiveTranslation();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-900 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        apiHealth={connectionStatus}
        modelStatus="ready"
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* TopBar Header */}
        <TopBar
          connectionStatus={connectionStatus}
          sessionId={sessionId}
          firstWordLatency={firstWordLatency}
          finalLatency={finalLatency}
          pipelineMode={pipelineMode}
          setPipelineMode={setPipelineMode}
          isDemo={isDemo}
        />

        {/* Scrollable Page Body */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {currentTab === 'dashboard' && (
            <Dashboard
              onStartLive={() => setCurrentTab('translate')}
              onExploreBenchmarks={() => setCurrentTab('benchmark')}
            />
          )}

          {currentTab === 'translate' && (
            <LiveTranslate
              sourceLanguage={sourceLanguage}
              setSourceLanguage={setSourceLanguage}
              targetLanguages={targetLanguages}
              isRecording={isRecording}
              volumeLevel={volumeLevel}
              toggleRecording={toggleRecording}
              partialTranscript={partialTranscript}
              committedTranscript={committedTranscript}
              currentStage={currentStage}
              lanes={lanes}
              captionHistory={captionHistory}
              firstWordLatency={firstWordLatency}
              finalLatency={finalLatency}
              stabilityScore={stabilityScore}
              rewriteCount={rewriteCount}
              sessionId={sessionId}
              pipelineMode={pipelineMode}
              triggerDemoSentence={triggerDemoSentence}
              playTTS={playTTS}
              debugInfo={debugInfo}
            />
          )}

          {currentTab === 'conversation' && <Conversation />}

          {currentTab === 'glossary' && <Glossary />}

          {currentTab === 'benchmark' && <Benchmark />}

          {currentTab === 'settings' && <Settings />}
        </main>
      </div>
    </div>
  );
};

export default App;
