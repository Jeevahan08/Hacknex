# IndicLive — Deployment Guide

This document describes production deployment practices, security considerations, WebSocket handling, and containerized deployment for IndicLive.

---

## 1. Production Architecture Overview

In production, IndicLive is deployed behind a reverse proxy (such as Nginx, Traefik, or AWS ALB) to manage SSL/TLS termination, static asset delivery, and WebSocket connection upgrade handling.

```
Internet ──► Nginx Reverse Proxy (SSL/TLS 443)
                 ├──► /api/* & /ws/* ──► FastAPI ASGI App (Uvicorn :8000)
                 └──► /*              ──► Frontend Static Assets (:80)
```

---

## 2. Environment Variables & Security

### Key Rules
- **Never expose `SARVAM_API_KEY` to the frontend client.** All Sarvam API requests must be orchestrated exclusively through the FastAPI backend.
- Store sensitive secrets in secret managers (e.g., AWS Secrets Manager, HashiCorp Vault) or secure environment injection.
- Restrict `FRONTEND_URL` in production to specific allowed origins rather than wildcard origins.

### Core Variables (`backend/.env`)
| Variable | Production Default | Description |
|---|---|---|
| `SARVAM_API_KEY` | *(Your Secret Key)* | Official Sarvam AI developer key |
| `DEMO_MODE` | `false` | Enable live AI inference calls |
| `LLM_ENABLED` | `true` | Enable Sarvam 105B contextual refinement |
| `ENABLE_TTS` | `false` | Enable audio synthesis (set true if audio playback needed) |
| `FRONTEND_URL` | `https://your-domain.com` | Allowed CORS origin |
| `DATABASE_URL` | `sqlite+aiosqlite:///./indiclive.db` | Storage connection URI |
| `LOG_LEVEL` | `INFO` | Application log level |

---

## 3. Reverse Proxy Configuration (Nginx Example)

Ensure WebSocket upgrade headers (`Upgrade` and `Connection`) are properly forwarded:

```nginx
server {
    listen 80;
    server_name translation.example.com;

    # Frontend Static Files
    location / {
        root /var/www/indiclive/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend REST API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Live Streaming WebSockets
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

## 4. Containerized Deployment (Docker Compose)

```bash
# Build and run all services in daemon mode
docker-compose up -d --build

# View container logs
docker-compose logs -f backend

# Stop services
docker-compose down
```
