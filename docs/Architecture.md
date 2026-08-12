# ChatLLM — Architecture

## 1. Architecture Objective

ChatLLM uses a layered, modular architecture designed for enterprise AI usage.

The central architectural principle is:

> **ChatLLM controls the AI; the AI does not control ChatLLM.**

Business rules remain in ChatLLM services. LLM providers are isolated behind the AI Gateway.

---

## 2. High-Level Application Flow

```text
                    ┌─────────────────────┐
                    │       ADMIN         │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
          Roles          Departments         Settings
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                         User Management
                               │
                               ▼
                        Role + Department
                               │
                               ▼
                          Token Wallet
                               │
                               ▼
                    ┌─────────────────────┐
                    │      EMPLOYEE       │
                    └──────────┬──────────┘
                               │
                         Authentication
                               │
                               ▼
                         Chat Session
                               │
                               ▼
                         Select Model
                               │
                               ▼
                        Submit Prompt
                               │
                               ▼
                    Authentication / RBAC
                               │
                               ▼
                         Token Service
                               │
                    ┌──────────┴──────────┐
                    │                     │
              Insufficient            Available
                    │                     │
                    ▼                     ▼
             Token Request          Prompt Service
                                          │
                                          ▼
                                  Prompt Similarity
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                         Repeated                  Reused
                              │                       │
                              ▼                       ▼
                     Prompt Suggestion         Reward Logic
                              │                       │
                              └───────────┬───────────┘
                                          ▼
                                     AI Gateway
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                      OpenAI          Anthropic          Gemini
                         │                │                │
                         └────────────────┼────────────────┘
                                          ▼
                                      Response
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                           Message     Usage       Prompt Log
                              │           │
                              └─────┬─────┘
                                    ▼
                              Wallet Deduction
                                    │
                                    ▼
                            Token Transaction
                                    │
                                    ▼
                               Audit Log
                                    │
                                    ▼
                              Final Response
```

---

## 3. Backend Layer Architecture

```text
API
 ↓
Schema Validation
 ↓
Authentication / Authorization
 ↓
Service
 ↓
Repository
 ↓
Database
```

AI path:

```text
ChatService
 ↓
TokenService
 ↓
PromptService
 ↓
AIGateway
 ↓
Provider Adapter
 ↓
External LLM
```

The API layer should remain thin.

---

## 4. Backend Folder Structure

```text
ChatLLM/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── constants.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   │
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │
│   │   ├── repositories/
│   │   ├── services/
│   │   │
│   │   ├── ai/
│   │   │   ├── base.py
│   │   │   ├── gateway.py
│   │   │   └── providers/
│   │   │
│   │   ├── workers/
│   │   └── utils/
│   │
│   ├── migrations/
│   └── tests/
│
├── frontend/
├── docs/
└── docker-compose.yml
```

### Folder responsibility

| Folder | Responsibility |
|---|---|
| `api/` | HTTP endpoints |
| `schemas/` | Pydantic request/response contracts |
| `models/` | Database models |
| `repositories/` | Database queries |
| `services/` | Business logic |
| `ai/` | AI Gateway/provider adapters |
| `workers/` | Scheduled/background processing |
| `core/` | Configuration, database, security |
| `utils/` | Small reusable utilities |
| `tests/` | Automated tests |

---

## 5. Frontend

Frontend is initialized from the beginning but backend development has priority.

Recommended:

```text
React
TypeScript
Vite
```

The frontend communicates only with the ChatLLM API.

```text
Frontend
   ↓
REST API
   ↓
FastAPI
```

The frontend must never call OpenAI/Anthropic/Gemini directly with organization provider secrets.

---

## 6. Technology Stack

### Backend

- Python 3.13
- FastAPI
- Pydantic 2
- pydantic-settings
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Psycopg 3
- PyJWT
- Argon2
- HTTPX

### AI

- OpenAI SDK
- Anthropic SDK
- Google GenAI SDK

All provider SDKs are accessed through provider adapters.

### Frontend

- React
- TypeScript
- Vite

### Testing

- Pytest
- pytest-asyncio
- pytest-cov

### Development quality

- Ruff
- mypy

---

## 7. Database Architecture

Core domains:

```text
users
roles
departments

ai_providers
ai_models

chat_sessions
chat_messages

employee_token_wallets
token_usage
token_transactions
token_requests

prompt_logs
prompt_suggestions
prompt_rewards

audit_logs
system_settings
```

Important distinction:

```text
Wallet
=
Current state

Token Usage
=
AI consumption

Token Transaction
=
Balance history/reason
```

---

## 8. AI Gateway

The AI Gateway is a first-class architectural component.

```text
AIGateway
    │
    ├── OpenAIProvider
    ├── AnthropicProvider
    └── GeminiProvider
```

Each provider adapter converts provider-specific APIs into a normalized ChatLLM interface.

Normalized response should conceptually contain:

```text
provider
model
content
input_tokens
output_tokens
total_tokens
finish_reason
latency
provider_request_id
```

---

## 9. API Versioning

Production APIs should use:

```text
/api/v1/
```

Examples:

```text
/api/v1/auth/login
/api/v1/users
/api/v1/roles
/api/v1/departments
/api/v1/ai-models
/api/v1/chat/sessions
/api/v1/token-wallet
/api/v1/token-requests
```

---

## 10. Transaction Boundaries

Critical operations should be transactionally consistent.

For a successful AI request:

```text
AI Response
 ↓
Usage Record
 ↓
Wallet Finalization
 ↓
Token Transaction
 ↓
Prompt Log Update
 ↓
Audit Log
```

The exact database transaction boundary will be finalized during implementation, but the system must prevent states where usage is recorded without wallet accounting or vice versa.

---

## 11. Background Processing

Background jobs are reserved for operations such as:

- Daily token reset.
- Carry-forward calculation.
- Token expiration.
- Cleanup.
- Future periodic analytics.

Do not introduce a job framework until a concrete background-processing requirement needs it.

---

## 12. Architecture Principles

1. API routes stay thin.
2. Business logic belongs in services.
3. Database access belongs in repositories.
4. AI calls go through the AI Gateway.
5. Provider-specific logic stays inside provider adapters.
6. Database schema changes use Alembic.
7. Frontend never owns security/business rules.
8. Token accounting is auditable.
9. AI output is untrusted.
10. Do not generate unnecessary files.
11. Do not change the agreed folder structure without a clear requirement or explicit approval.
