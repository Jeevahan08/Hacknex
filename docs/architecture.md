# IndicLive — System Architecture & Latency Engineering

## 1. High-Level Architectural Overview

IndicLive is a real-time, low-latency live speech translation and intelligence platform tailored for Indian multilingual contexts. It connects continuous microphone audio streams to speech recognition, semantic stabilization, entity protection, neural translation, and text-to-speech synthesis pipelines.

```mermaid
flowchart TD
    subgraph Client["Frontend Client (React + Web Audio API)"]
        MIC["🎙️ Microphone Capture (16kHz PCM Linear)"]
        WS_CLIENT["⚡ WebSocket Client (/ws/v1/live)"]
        DASHBOARD["📺 Live Translation Control Room"]
        AUDIO_PLAY["🔊 Web Audio Synthesizer"]
    end

    subgraph Backend["FastAPI Async Engine"]
        WS_ENDPOINT["🔌 WebSocket Session Manager"]
        SESSION["🧠 Session State & Buffer Manager"]
        
        subgraph Pipeline["Streaming Pipeline"]
            ASR["🗣️ Saaras v4 Realtime Streaming ASR"]
            COMMIT["⏱️ Meaning-Aware Commit Policy"]
            RAG["📚 RAG Glossary & Entity Protection"]
            ROUTER["🔀 LLM Intelligence Router (Sarvam 105B)"]
            TRANSLATE["🌐 Parallel Translation (asyncio.gather)"]
            TTS["🔉 Bulbul v3 Neural TTS Synthesis"]
        end
        
        CACHE["⚡ In-Memory LRU & Audio Cache"]
        DB[(💾 SQLite Database / SQLAlchemy)]
    end

    MIC -->|Linear PCM Audio Chunks| WS_CLIENT
    WS_CLIENT -->|Binary WebSocket Frames| WS_ENDPOINT
    WS_ENDPOINT --> SESSION
    SESSION --> ASR
    ASR -->|Partial Transcripts| COMMIT
    COMMIT -->|Stable Semantic Units| RAG
    RAG -->|Protected Entities + Glossary Matches| ROUTER
    ROUTER --> TRANSLATE
    TRANSLATE -->|Multi-Language Translations| WS_ENDPOINT
    TRANSLATE --> TTS
    TTS --> CACHE
    TTS -->|Base64 WAV Audio| WS_ENDPOINT
    WS_ENDPOINT --> DASHBOARD
    WS_ENDPOINT --> AUDIO_PLAY
    SESSION -.-> DB
```

---

## 2. Component Responsibilities

### Frontend Layer (React + TypeScript + Vite)
- **Audio Worklet / ScriptProcessor**: Captures real-time browser audio at 16,000 Hz, 16-bit mono PCM.
- **WebSocket Manager**: Maintains resilient bi-directional streaming, heartbeats, and auto-reconnects.
- **Control Room UI**: Displays synchronized partial/final transcripts, multi-target translations, latency telemetry, and audio waveform visualizations.

### Backend Layer (FastAPI + AsyncIO)
- **WebSocket Session Handler** (`app/api/websocket.py`): Manages life cycles, stream concurrency, audio packet ingestion, and telemetry reporting.
- **Speech-to-Text Integration** (`app/ai/providers/sarvam/stt.py`): Streams raw audio chunks directly to Saaras v4 ASR.
- **Intelligent Commit Policy** (`app/ai/intelligence/commit_policy.py`): Eliminates word jitter and false commits by calculating stability thresholds and pause intervals.
- **RAG & Entity Protection** (`app/ai/intelligence/entity_protection.py`): Retrieves domain terminology and protects proper nouns, numbers, and brand terms.
- **LLM Intelligence Router** (`app/ai/intelligence/llm_router.py`): Employs Sarvam 105B for contextual ambiguity resolution, grammar polishing, and dialectal translation.
- **Parallel Translation Dispatcher**: Leverages `asyncio.gather()` to fan out translations across multiple target languages simultaneously.
- **Text-to-Speech Engine** (`app/ai/providers/sarvam/tts.py`): Converts finalized translations into synthesized Indic speech using Bulbul v3 with LRU caching.
