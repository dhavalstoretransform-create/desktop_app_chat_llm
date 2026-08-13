# ChatLLM — Project Memory

## Purpose

This file is the project continuity record.

It should be updated as development progresses so future work can quickly understand:

- What has been completed.
- What decisions were made.
- What is currently in progress.
- What remains.
- Important architecture decisions.
- Known issues.
- Changes to the approved structure.

---

# Current Project Status

**Status:** Phase 1 — Project Foundation — ✅ COMPLETED.

**Current priority:** Backend-first development.

**Current phase:** Phase 2 — Database + Models.

**Frontend:** Initialized (Vite React-TS scaffold). Backend development has priority.

---

# Project Definition

ChatLLM is:

> A centralized enterprise AI platform that gives employees controlled access to multiple LLM providers while managing permissions, token budgets, AI usage, prompt intelligence, rewards, and complete auditability.

### Target users

- Organization employees.
- Organization administrators.

### Core purpose

Provide multiple approved LLM providers through one centrally controlled enterprise application.

---

# Current Architecture Decisions

## Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy
Alembic
PostgreSQL
```

## AI

```text
AI Gateway
 ├── OpenAI
 ├── Anthropic
 └── Google Gemini
```

## Frontend

```text
React
TypeScript
Vite
```

---

# Core Architectural Rules

- API routes remain thin.
- Business logic belongs in services.
- Database access belongs in repositories.
- AI calls go through the AI Gateway.
- Wallet, usage, and token transactions remain separate.
- AI output is untrusted.
- AI cannot directly modify business state.
- Frontend does not enforce security.
- Secrets are never committed.
- Unnecessary files must not be generated.
- Folder/file structure should not be changed without a clear requirement or approval.
- Development proceeds file-by-file with testing.

---

# Development Phases

```text
Phase 1  — Project Foundation
Phase 2  — Database + Models
Phase 3  — Authentication
Phase 4  — RBAC
Phase 5  — Departments
Phase 6  — User / Employee Management
Phase 7  — AI Model Management
Phase 8  — Token Wallet + Ledger
Phase 9  — AI Gateway
Phase 10 — Chat Sessions + Messages
Phase 11 — Token Usage + Deduction
Phase 12 — Prompt Logging
Phase 13 — Prompt Similarity
Phase 14 — Prompt Suggestions
Phase 15 — Prompt Reuse + Rewards
Phase 16 — Token Requests
Phase 17 — Audit Logging
Phase 18 — Background Jobs / Daily Reset
Phase 19 — Admin Dashboard
Phase 20 — Employee Dashboard
Phase 21 — Integration Testing
Phase 22 — Production Hardening
```

---

# Completed Work

## Documentation / Planning

- [x] ChatLLM product concept defined.
- [x] Target users defined.
- [x] Multi-LLM platform concept defined.
- [x] High-level application flow defined.
- [x] Backend-first development strategy defined.
- [x] Folder architecture defined.
- [x] Engineering rules defined.
- [x] Error-handling principles defined.
- [x] AI boundaries defined.
- [x] Development phases defined.
- [x] Initial design system defined.

## Implementation

### Phase 1 — Project Foundation — ✅ COMPLETED

- Foundation, health endpoint, pytest suite, and React-TS frontend scaffolded.

### Step 2 — Database Architecture — ✅ COMPLETED

- Core models mixins and layered CRUD structures established.

### Step 3 — AI Model Database Table — ✅ COMPLETED

- Created `AIModel` database table and applied migration `e1bd35ae3f65`.

### Step 4 — Complete Database Schema — ✅ COMPLETED

Completed:
- Created and mapped remaining system database models subclassing `BaseModel`:
  - `Department` (`departments` table)
  - `Role` (`roles` table)
  - `User` (`users` table)
  - `EmployeeTokenWallet` (`employee_token_wallets` table)
  - `ChatSession` (`chat_sessions` table)
  - `ChatMessage` (`chat_messages` table)
  - `PromptLog` (`prompt_logs` table)
  - `AuditLog` (`audit_logs` table)
  - `ModelRecommendation` (`model_recommendations` table)
  - `PromptReward` (`prompt_rewards` table)
  - `SuggestedPrompt` (`suggested_prompts` table)
  - `SystemSetting` (`system_settings` table)
  - `TokenRequest` (`token_requests` table)
  - `TokenUsage` (`token_usages` table)
- Registered all models in `app/models/__init__.py`.
- Configured explicit SQLAlchemy `MetaData(naming_convention=...)` on the `Base` class inside `app/core/database.py` to ensure stable and predictable constraint naming (primary keys, foreign keys, unique constraints, check constraints, indices).
- Documented Core Foreign Key Rules (naming conventions, on-delete cascade rules, nullability standards, relationship ownership) in `Steering/Rule.md` section 24.
- Defined and documented Deletion and Soft Delete Policies (Soft delete only, immutable records, user messages) in `Steering/Rule.md` section 25.
- Defined and documented the Unique Constraint Strategy (database level enforcement, unique indices, IntegrityError exception mapping) in `Steering/Rule.md` section 26.
- Defined and documented Database Transaction Management principles (service boundaries, atomic operations, explicit rollbacks) in `Steering/Rule.md` section 27.
- Defined and documented FastAPI Database Session Management guidelines (request-scoped lifecycle, injection helpers, session cleanup, anti-patterns) in `Steering/Rule.md` section 28.
- Defined and documented Alembic Migration Conventions (mandatory migrations, naming rules, destructive modification safety guidelines) in `Steering/Rule.md` section 29.
- Defined and documented Database Testing Guidelines (in-memory SQLite, fixture lifecycle, test coverage requirements, no placeholder tests) in `Steering/Rule.md` section 30.
- Defined and documented the Database Error Translation Policy (direct exposure prohibition, error mapping matrix, diagnostic logging rules) in `Steering/Rule.md` section 31.
- Defined and documented Database Performance Principles (N+1 query avoidance, pagination rules, column deferral, indexing patterns) in `Steering/Rule.md` section 32.
- Defined and documented Database Security Principles (credentials isolation, injection protection, SQL parameterization, exception handling boundaries) in `Steering/Rule.md` section 33.
- Generated and applied Alembic migration `d516fc54c3ed` creating all tables and foreign key constraints on the live Neon DB.
- Added comprehensive integration test (`test_all_domain_models_orm`) verifying instantiation and save transactions for all new models.

### Phase 2.2 — Role + Department Database Models — ✅ COMPLETED

Completed:
- Added `is_active` fields to `Role` and `Department` models.
- Added unique stable `code` machine-readable fields to `Role` and `Department` models and adjusted `name` to allow duplicate/editable display names.
- Generated and applied Alembic migrations `74aea769bf54` and `a07ed0adb246` adding columns and indexes to the live Neon DB.
- Created validation schemas (Pydantic V2 `ConfigDict`), repositories (`RoleRepository`, `DepartmentRepository`), services (`RoleService`, `DepartmentService`), and API CRUD routers.
- Registered endpoints in v1 API router.
- Added lifecycle integration tests verifying duplicate code checks, display name editing, soft deletion, and CRUD.

Tests: **17 passed, 0 failed** (`pytest -v`).
Linters: **Ruff clean, MyPy clean (44 files)**.

Known issues: None.

Next phase: Authentication & Credentials (Phase 3).


---

# Current Phase

**Phase:** 3 — Authentication & Credentials


### Objective

Create the database foundation: PostgreSQL connection, SQLAlchemy 2.x async engine, Base model with UUID + UTC timestamps, Alembic migration setup, and verify Neon DB connectivity.

---

# Important Decisions Log

```text
Date: 2026-08-11
Decision: database.py and security.py not created in Phase 1.
Reason: Rule 4 — no unnecessary files. Rule 7 — no speculative placeholders.
         database.py belongs to Phase 2. security.py belongs to Phase 3.
Impact: None. They will be created when the relevant phase begins.
Approved by: User (Phase 1 approval).
```

```text
Date: 2026-08-11
Decision: Empty folder skeletons (models/, services/, repositories/, etc.) not created.
Reason: Empty directories carry no value until code is placed inside them.
         They will be created as each phase builds the content.
Impact: None.
Approved by: User (Phase 1 approval).
```

```text
Date: 2026-08-11
Decision: requirements.txt scoped to Phase 1 dependencies only.
Reason: SQLAlchemy, Alembic, psycopg, auth libs, AI SDKs added when their
         phase begins — keeping Phase 1 clean and minimal.
Impact: Phase 2 will extend requirements.txt with database dependencies.
Approved by: User (Phase 1 approval).
```

---

# Completed Phase Template

When a phase is completed, add:

```text
## Phase X — Completed

Completed:
- ...

Files added/changed:
- ...

Tests:
- ...

Known issues:
- ...

Next phase:
- ...
```

---

# Known Issues

None recorded yet.

---

# Future Notes

This file must remain factual.

Do not record a feature as completed until:

```text
Implementation
+
Testing
+
Review
```

have been completed.
