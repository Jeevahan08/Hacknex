# IndicLive — API Reference Manual

Interactive Swagger documentation is available at `http://localhost:8000/docs` when the backend is running.

---

## 1. REST Endpoints

### Health Check
- **`GET /api/v1/health`**
- Returns backend status, database connectivity, and Sarvam provider status.
```json
{
  "status": "healthy",
  "demo_mode": true,
  "backend": "connected",
  "database": "connected",
  "provider": "sarvam",
  "provider_connected": true,
  "timestamp": 1740000000.0
}
```

### Model Registry
- **`GET /api/v1/models`**
- Returns currently configured AI models and operational readiness.
```json
{
  "stt": { "provider": "sarvam", "model": "saaras:v4", "status": "ready" },
  "translation": { "provider": "sarvam", "model": "sarvam-translate:v1", "status": "ready" },
  "llm": { "provider": "sarvam", "model": "sarvam-105b", "status": "ready" },
  "tts": { "provider": "sarvam", "model": "bulbul:v3", "status": "ready" }
}
```

### Supported Languages
- **`GET /api/v1/languages`**
- Returns supported Indic languages, native display names, scripts, and status.

### Synchronous Text Translation
- **`POST /api/v1/translate`**
- Translates input text into specified target languages with optional LLM refinement.
- **Request Body**:
```json
{
  "text": "Good morning, welcome to our conference.",
  "source_language": "en-IN",
  "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
  "use_llm": false,
  "enable_tts": false
}
```

### Domain Glossaries (RAG Engine)
- **`GET /api/v1/glossary`** — List all registered glossary rules.
- **`POST /api/v1/glossary`** — Register a new term preservation or translation override.
- **`DELETE /api/v1/glossary/{term_id}`** — Remove a glossary rule.

### Benchmark & Telemetry
- **`GET /api/v1/benchmark/summary`** — Retrieve pipeline latency metrics (STT, translation, TTS turnaround times).

---

## 2. WebSocket Streaming Protocol

### Connection
- **Endpoint**: `ws://localhost:8000/ws/v1/live/{session_id}`

### Inbound Events (Client → Server)
1. **Configure Session** (`config`):
```json
{
  "type": "config",
  "source_language": "en-IN",
  "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
  "enable_tts": false,
  "use_llm": false
}
```
2. **Audio Streaming (Binary)**:
   - Raw 16kHz 16-bit mono PCM chunks sent as binary WebSocket frames.

### Outbound Events (Server → Client)
1. **Partial Transcription** (`partial_transcript`):
```json
{
  "type": "partial_transcript",
  "text": "Good morning every...",
  "stability": 0.65
}
```
2. **Final Translation** (`translation_final`):
```json
{
  "type": "translation_final",
  "source_text": "Good morning everyone.",
  "translations": {
    "ta-IN": "அனைவருக்கும் காலை வணக்கம்.",
    "hi-IN": "सभी को सुप्रभात।",
    "ml-IN": "എല്ലാവർക്കും സുപ്രഭാതം."
  },
  "latency_ms": 320
}
```
