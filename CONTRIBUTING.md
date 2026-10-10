# Contributing to IndicLive

Thank you for your interest in contributing to **IndicLive**! We welcome contributions to help advance real-time Indic language translation, LLM intelligence, and speech synthesis pipelines.

---

## Code of Conduct

We are committed to providing a friendly, safe, and welcoming environment for all contributors. Please be respectful and constructive in all interactions.

---

## Development Workflow

### 1. Branch Naming Conventions
Create a branch from `main` with a clear prefix:
- `feature/description` — For new capabilities or language additions
- `fix/description` — For bug fixes and regression resolutions
- `perf/description` — For latency and optimization improvements
- `docs/description` — For documentation updates
- `test/description` — For new test cases or benchmark scenarios

### 2. Setting Up Your Local Environment

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env
```

---

## Testing & Quality Assurance

Before submitting a Pull Request, verify that all backend tests pass and frontend builds cleanly:

### Backend Tests
```bash
cd backend
python -m pytest
```

### Frontend Build & Type Check
```bash
cd frontend
npm run build
```

---

## Commit Guidelines

Follow conventional commit formats:
- `feat: add Kannada support in language registry`
- `fix: resolve race condition in websocket streaming queue`
- `docs: update live translation architecture diagrams`
- `refactor: optimize RAG glossary term lookup lookup`
- `test: add unit tests for stability commit policy`

---

## Pull Request Process

1. Ensure all tests pass locally.
2. Update documentation if your change affects APIs, WebSocket schemas, or configuration keys.
3. Open a Pull Request targeting `main` with a clear description of what changed and how it was validated.
4. Maintainers will review your PR and provide constructive feedback.
