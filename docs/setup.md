# IndicLive — Installation & Setup Guide

This guide covers local environment setup for both Windows and Linux/macOS.

---

## 1. Prerequisites

- **Python**: 3.10+ (Verified on Python 3.11, 3.12, 3.13)
- **Node.js**: v18+ (Verified on Node.js v20+)
- **Audio Input Device**: Any working microphone for real-time speech capture.
- **Sarvam AI API Key** *(Optional)*: Required for live cloud ASR/Translation/TTS; mock demo mode works offline without keys.

---

## 2. Backend Setup

### Windows (PowerShell)
```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env

# Run automated test suite
python -m pytest

# Start development server
python -m uvicorn app.main:app --reload --port 8000
```

### Linux / macOS (Bash)
```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run tests
pytest

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend endpoints:
- API Server: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`

---

## 3. Frontend Setup

In a separate terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env  # Or on Windows: copy .env.example .env

# Run development server
npm run dev
```

Frontend app will be running at: `http://localhost:5173`

---

## 4. Docker Deployment

To launch the complete stack with Docker Compose:

```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend API: `http://localhost:8000`
