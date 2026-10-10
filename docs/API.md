# IndicLive — API Reference Manual

The IndicLive platform exposes both a RESTful API and a streaming WebSocket protocol.
Interactive Swagger documentation is available at: `http://localhost:8000/docs`

---

## 1. REST Endpoints

### Health Check
- **`GET /api/v1/health`**
- **Response**:
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

### Models Registry
- **`GET /api/v1/models`**
- **Response**:
```json
{
  "stt": {
    "provider": "sarvam",
    "model": "saaras:v4",
    "status": "ready"
  },
  "translation": {
    "provider": "sarvam",
    "model": "sarvam-translate:v1",
    "status": "ready"
  },
  "llm": {
    "provider": "sarvam",
    "model": "sarvam-105b",
    "status": "ready"
  },
  "tts": {
    "provider": "sarvam",
    "model": "bulbul:v3",
    "status": "ready"
  }
}
```

### Supported Languages
- **`GET /api/v1/languages`**
- **Response**:
```json
{
  "languages": [
    { "code": "en-IN", "name": "English", "native_name": "English (India)", "script": "Latin", "enabled": true },
    { "code": "ta-IN", "name": "Tamil", "native_name": "தமிழ்", "script": "Tamil", "enabled": true },
    { "code": "hi-IN", "name": "Hindi", "native_name": "हिन्दी", "script": "Devanagari", "enabled": true },
    { "code": "ml-IN", "name": "Malayalam", "native_name": "മലയാളം", "script": "Malayalam", "enabled": true },
    { "code": "te-IN", "name": "Telugu", "native_name": "తెలుగు", "script": "Telugu", "enabled": true },
    { "code": "kn-IN", "name": "Kannada", "native_name": "ಕನ್ನಡ", "script": "Kannada", "enabled": true }
  ]
}
```

### Parallel Translation
- **`POST /api/v1/translate`**
- **Request**:
```json
{
  "source_language": "en-IN",
  "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
  "text": "Good morning everyone.",
  "mode": "fast"
}
```
- **Response**:
```json
{
  "source_language": "en-IN",
  "text": "Good morning everyone.",
  "segment_id": "seg_001",
  "translations": {
    "ta-IN": { "language": "ta-IN", "translated_text": "அனைவருக்கும் காலை வணக்கம்.", "status": "final", "latency_ms": 610 },
    "hi-IN": { "language": "hi-IN", "translated_text": "सभी को सुप्रभात।", "status": "final", "latency_ms": 610 },
    "ml-IN": { "language": "ml-IN", "translated_text": "എല്ലാവർക്കും സുപ്രഭാതം.", "status": "final", "latency_ms": 610 }
  },
  "pipeline_mode": "fast",
  "total_latency_ms": 610
}
```

### Text-to-Speech (Bulbul v3)
- **`POST /api/v1/tts`**
- **Request**:
```json
{
  "text": "அனைவருக்கும் காலை வணக்கம்",
  "language": "ta-IN",
  "speaker": "ananya"
}
```
- **Response**:
```json
{
  "audio_base64": "<BASE64_WAV_BYTES>",
  "format": "audio/wav",
  "language": "ta-IN",
  "cached": false,
  "duration_ms": 120
}
```

---

## 2. WebSocket Protocol (`/ws/v1/live/{session_id}`)

### Client → Server Events
1. **Start Streaming Session**:
```json
{
  "type": "session.start",
  "source_language": "en-IN",
  "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
  "enable_tts": false,
  "mode": "fast"
}
```

2. **Send 16kHz PCM Audio Chunk**:
```json
{
  "type": "audio.chunk",
  "data": "<BASE64_PCM_CHUNK>"
}
```

3. **Trigger Judge Demo Sentence**:
```json
{
  "type": "demo.trigger",
  "sentence": "Good morning everyone, today we are going to discuss artificial intelligence."
}
```

### Server → Client Events
1. **Partial ASR Transcript**:
```json
{
  "type": "transcript.partial",
  "text": "Good morning everyone",
  "language": "en-IN",
  "timestamp": 1740000000.12
}
```

2. **Committed ASR Transcript**:
```json
{
  "type": "transcript.committed",
  "text": "Good morning everyone, today we are going to discuss artificial intelligence.",
  "segment_id": "seg_a1b2c3d4",
  "confidence": 0.96
}
```

3. **Live Interim Translation**:
```json
{
  "type": "translation.partial",
  "segment_id": "seg_a1b2c3d4",
  "target_language": "ta-IN",
  "text": "அனைவருக்கும் காலை வணக்கம்...",
  "status": "partial"
}
```

4. **Stable Final Translation**:
```json
{
  "type": "translation.final",
  "segment_id": "seg_a1b2c3d4",
  "target_language": "ta-IN",
  "text": "அனைவருக்கும் காலை வணக்கம், இன்று நாம் செயற்கை நுண்ணறிவு பற்றி விவாதிக்க உள்ளோம்.",
  "status": "final",
  "first_word_latency_ms": 620,
  "final_latency_ms": 1240,
  "stability_score": 0.958,
  "rewrites": 1
}
```
