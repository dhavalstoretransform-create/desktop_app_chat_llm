# ChatLLM

> **Centralized enterprise AI platform** — giving organization employees controlled access to multiple LLM providers through one secure, auditable interface.

---

## Overview

ChatLLM is a backend-first enterprise application that provides:

- Centralized access to OpenAI, Anthropic, and Google Gemini
- Role-based access control (RBAC)
- Department management
- Employee token wallets and usage accounting
- Prompt intelligence and reuse rewards
- Complete auditability

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13 + FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Database | PostgreSQL (Neon) |
| Validation | Pydantic 2 + pydantic-settings |
| Auth | JWT + Argon2 |
| HTTP Client | HTTPX |
| Frontend | React + TypeScript + Vite |

## Project Structure

```
ChatLLM/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, database, security
│   │   ├── api/v1/        # HTTP endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── repositories/  # Database queries
│   │   ├── services/      # Business logic
│   │   ├── ai/            # AI Gateway + provider adapters
│   │   ├── workers/       # Background jobs
│   │   └── utils/         # Shared utilities
│   ├── migrations/        # Alembic migrations
│   └── tests/
├── frontend/              # React + TypeScript + Vite
├── docs/                  # Project documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start (Development)

### 1. Start the database

```bash
docker-compose up -d
```

### 2. Set up the backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in real values
```

### 4. Run migrations

```bash
cd backend
alembic upgrade head
```

### 5. Start the backend

```bash
cd backend
uvicorn app.main:app --reload
```

API available at: `http://localhost:8000`  
Docs: `http://localhost:8000/api/v1/docs`  
Health: `http://localhost:8000/health`

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:5173`

## Running Tests

```bash
cd backend
pytest -v
```

## Code Quality

```bash
cd backend

# Lint
ruff check .

# Type check
mypy app/
```

## Development Rules

- Backend development has priority.
- API routes must remain thin — business logic belongs in services.
- Database access belongs in repositories.
- All AI provider calls go through the AI Gateway.
- Never hardcode secrets. Never commit `.env`.
- Token wallet, token usage, and token transactions are separate concepts.
- AI output is always untrusted.

See `docs/Rule.md` for the full engineering rules.

## Development Phases

See `docs/phases.md` for the complete 22-phase development plan.

---

**Current Phase:** 1 — Project Foundation ✅
