# IndicLive — Testing & Quality Assurance Manual

This guide describes how to run unit tests, regression tests, end-to-end WebSocket checks, and frontend builds.

---

## 1. Backend Automated Test Suite

IndicLive includes a 48-test automated test suite covering:
- **Intelligent Commit Policy** (`tests/test_commit_policy.py`): Verifies token thresholding, pause detection, and commit boundary decision-making.
- **Defect Regressions** (`tests/test_defect_regressions.py`): Ensures protection against historical speech-translation edge cases.
- **RAG & Glossary Preservation** (`tests/test_glossary.py`): Tests custom entity preservation and domain dictionary replacements.
- **Health & Readiness** (`tests/test_health.py`): Checks FastAPI health check endpoints and readiness probes.
- **Pipeline & Parallel Translation** (`tests/test_pipeline_translation.py`): Validates multi-language translation fanout (`asyncio.gather`).
- **Transcript Segmentation** (`tests/test_segmentation.py`): Tests sentence chunking and word boundary alignment.
- **STT & LLM Integration** (`tests/test_stt_llm.py`): Validates Saaras STT and Sarvam 105B LLM prompt assembly and routing.
- **WebSocket Protocol** (`tests/test_websocket.py`, `backend/test_live_ws.py`): Verifies real-time streaming connections and message formats.

### Running Backend Tests
From the `backend` directory:
```bash
python -m pytest
```

*(Note for Windows environments with WDAC enabled: set `$env:DISABLE_SQLALCHEMY_CEXT="1"` before running pytest)*

---

## 2. Frontend Build & Type Validation

From the `frontend` directory:
```bash
# Verify TypeScript typing and create production bundle
npm run build
```

---

## 3. Integration & Benchmark Scripts

Located in the `scripts/` directory:

- **Benchmark Pipeline**:
  ```bash
  python scripts/benchmark_pipeline.py
  ```
  Measures latency profiles across STT, Translation, LLM refinement, and TTS.

- **WebSocket Live Stream Test**:
  ```bash
  python scripts/test_live_ws.py
  ```
  Simulates a real-time client streaming audio packets over WebSockets.

- **API Route Validation**:
  ```bash
  python scripts/test_api.py
  ```
  Validates all REST endpoints against a running backend server.
