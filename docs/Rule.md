# ChatLLM — Engineering Rules

## 1. Purpose

This document defines what developers should do, what they must avoid, how dependencies are selected, how errors are handled, and where the AI boundary exists.

---

# 2. Core Rules

### Rule 1 — Enterprise first

Every implementation should consider:

```text
Security
Auditability
Cost Control
Maintainability
Scalability
Multi-LLM support
```

### Rule 2 — Backend first

Backend development has priority. Frontend is initialized but should not drive backend architecture.

### Rule 3 — File-by-file development

Use:

```text
Implement
 ↓
Test
 ↓
Review
 ↓
Next file
```

Do not generate large amounts of unused placeholder code.

### Rule 4 — No unnecessary files

**Only create files required by the current phase or explicitly approved project structure.**

Do not generate speculative files for future functionality.

### Rule 5 — Controlled structure changes

The agreed folder/file structure should remain stable. A structure change should happen only when:

- A requirement requires it.
- A technical limitation requires it.
- The change is explicitly approved.
- The change clearly improves maintainability without unnecessary complexity.

---

# 3. Code Organization

### API

API routes should:

```text
Validate
Authenticate
Authorize
Call Service
Return Response
```

Do not place large business workflows in route handlers.

### Services

Business rules belong in services.

Examples:

```text
AuthService
UserService
TokenService
ChatService
PromptService
SimilarityService
RewardService
UsageService
AuditService
```

### Repositories

Database queries belong in repositories.

### Models

SQLAlchemy database models belong in `models/`.

### Schemas

Pydantic request/response models belong in `schemas/`.

---

# 4. Libraries and Installation

## Core runtime

```text
Python 3.13
FastAPI
SQLAlchemy 2.x
Alembic
Pydantic 2
pydantic-settings
Psycopg 3
PyJWT
argon2-cffi
HTTPX
python-multipart
```

## AI providers

```text
openai
anthropic
google-genai
```

## Development/testing

```text
pytest
pytest-asyncio
pytest-cov
ruff
mypy
```

## Frontend

```text
React
TypeScript
Vite
```

---

# 5. Dependency Rules

Before adding a library, ask:

1. What requirement needs it?
2. Can the standard library or existing stack solve it?
3. Does it add infrastructure?
4. Does it increase deployment complexity?
5. Is it actively maintained?
6. Does it create unnecessary coupling?

Do not install libraries only because they are popular.

---

# 6. Libraries to Avoid Initially

Do not introduce these without a concrete requirement:

```text
LangChain
LlamaIndex
Celery
Redis
Kafka
Elasticsearch
Vector databases
pgvector
Agent frameworks
```

These may be added later when a phase actually requires them.

---

# 7. Database Rules

- PostgreSQL is the production database target.
- SQLAlchemy is the ORM.
- Alembic manages schema changes.
- Never manually change production schema without a migration.
- Preserve historical usage and audit records.
- Do not delete critical business records without considering historical relationships.
- Wallet changes must be recorded in `token_transactions`.

---

# 8. Authentication and Security

- Never store plain-text passwords.
- Use Argon2 for password hashing.
- Use JWT/access tokens for the initial authentication architecture.
- Never store secrets in source code.
- Never commit `.env`.
- Never expose API keys in frontend code.
- Never trust frontend authorization.
- Every protected operation must be authorized server-side.
- Do not log passwords, JWT secrets, API keys, or database credentials.

---

# 9. Token Rules

Token concepts must remain separate:

```text
Token Wallet
=
Current balance

Token Usage
=
What the AI consumed

Token Transaction
=
Why wallet balance changed

Token Request
=
Employee request for additional allocation
```

### Token flow

```text
Request
 ↓
Authentication
 ↓
Authorization
 ↓
Token reservation/availability
 ↓
AI call
 ↓
Actual usage
 ↓
Finalize wallet
 ↓
Transaction
 ↓
Audit
```

AI failure must not permanently consume tokens that were only reserved for the failed request.

### Never

```text
AI call
 ↓
Charge employee blindly
```

---

# 10. Error Handling Standard

All errors must have:

```text
Safe user response
Internal diagnostic information
Clear error category
Request ID
```

Never return raw stack traces to users.

## Error categories

```text
VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
RESOURCE_NOT_FOUND
TOKEN_ERROR
AI_PROVIDER_ERROR
AI_POLICY_ERROR
RATE_LIMIT_ERROR
DATABASE_ERROR
EXTERNAL_SERVICE_ERROR
CONFIGURATION_ERROR
INTERNAL_ERROR
```

Example:

```json
{
  "error": {
    "code": "AI_PROVIDER_TIMEOUT",
    "message": "The AI service took too long to respond. Please try again.",
    "request_id": "req_123"
  }
}
```

## HTTP conventions

```text
400/422
Validation

401
Authentication

403
Authorization

404
Resource not found

409
Business/state conflict

429
Rate limit

500
Unexpected internal error

502/503/504
External provider/service failure
```

The final status-code mapping should remain consistent across the API.

---

# 11. AI Error Handling

Provider-specific errors must be normalized.

```text
OpenAI timeout
Anthropic timeout
Gemini timeout
       ↓
AI_PROVIDER_TIMEOUT
```

Retry only transient failures.

Do not blindly retry:

```text
Invalid API key
Invalid request
Invalid model
Policy rejection
Authentication failure
```

Retries must never create duplicate token deductions.

---

# 12. Request ID

Every API request should eventually receive a unique request ID.

Example:

```text
req_01KABC...
```

The ID should be traceable through:

```text
Application logs
AI provider logs/metadata
Usage records where appropriate
Audit records where appropriate
```

---

# 13. Idempotency

Important state-changing operations should be designed for safe retries.

Examples:

```text
Chat generation
Token approval
Wallet adjustment
Reward creation
Token request
```

A retry must not accidentally:

- Charge tokens twice.
- Grant a reward twice.
- Approve a request twice.
- Create duplicate business records.

---

# 14. AI Boundary

## Fundamental rule

> **AI can recommend, generate, analyze, and assist. ChatLLM decides what is allowed to happen.**

AI is **not** an administrator.

---

## AI is allowed to

```text
Generate text
Answer questions
Summarize
Rewrite
Analyze
Suggest
Improve prompts
Classify
Extract structured information
```

---

## AI is not allowed to directly

```text
Create users
Delete users
Change roles
Change permissions
Modify token balances
Approve token requests
Grant rewards
Modify audit logs
Change system settings
Access database credentials
Access provider secrets
Execute arbitrary SQL
Execute shell commands
Modify infrastructure
```

---

# 15. AI Output Is Untrusted

Never treat AI output as authoritative business state.

Bad:

```text
AI says:
role = admin
 ↓
Database update
```

Correct:

```text
AI output
 ↓
Validate
 ↓
Business rules
 ↓
Authorization
 ↓
Service
 ↓
Database
```

---

# 16. AI Cannot Access the Database Directly

The AI may eventually request an approved tool, but tools must pass through:

```text
Tool Request
 ↓
Tool Registry
 ↓
Authentication
 ↓
Authorization
 ↓
Input Validation
 ↓
Business Service
 ↓
Repository
 ↓
Database
```

Never provide arbitrary SQL or code execution.

---

# 17. AI Cannot Access Secrets

Never send these to an LLM:

```text
API keys
JWT secrets
Database passwords
Cloud credentials
Infrastructure credentials
Internal secret tokens
```

---

# 18. Prompt Injection Boundary

Treat the following as untrusted:

```text
Employee prompt
Uploaded document
Retrieved content
External web content
Tool result
```

User content must not override:

```text
Platform policies
Authorization rules
Token rules
Security controls
System instructions
```

---

# 19. AI Data Privacy

Before sending data to an external provider, ChatLLM must eventually define:

- What data may leave the organization.
- Which providers may receive it.
- Retention expectations.
- Department-specific restrictions.
- Sensitive-data policies.

Never assume all employee prompts are safe for every provider.

---

# 20. AI Cost and Rate Boundaries

The AI Gateway must be able to enforce:

```text
Employee limits
Department limits
Model limits
Provider limits
Global limits
Input limits
Output limits
```

The backend remains responsible for cost control.

---

# 21. Audit Rules

Audit important events:

```text
LOGIN
LOGIN_FAILED
USER_CREATED
USER_UPDATED
ROLE_CHANGED
CHAT_SESSION_CREATED
MESSAGE_SENT
TOKEN_USED
TOKEN_REQUESTED
TOKEN_APPROVED
TOKEN_REJECTED
PROMPT_SUBMITTED
PROMPT_SUGGESTED
PROMPT_REUSED
REWARD_GRANTED
SETTING_CHANGED
```

Audit logs are business/security records and must not be treated as ordinary debug logs.

---

# 22. Testing Rules

Test business behavior, not only HTTP responses.

Important tests include:

- Employee cannot access admin operations.
- Token cannot become invalid through concurrent requests.
- Insufficient tokens prevent an AI call.
- Failed AI calls do not permanently consume reserved tokens.
- Approved token requests update wallet and ledger.
- Rejected requests do not update wallet.
- Self-reuse does not generate rewards.
- Duplicate reuse does not generate duplicate rewards.
- AI provider failures are normalized.
- Sensitive values are not exposed in error responses.

---

# 23. Final Golden Rules

```text
1. Security before convenience.
2. API routes stay thin.
3. Business logic belongs in services.
4. Database access belongs in repositories.
5. All LLM calls go through the AI Gateway.
6. Wallet, usage, and transactions are separate.
7. Every important wallet change is auditable.
8. AI output is untrusted.
9. AI never controls authorization or business state.
10. Do not generate unnecessary files.
11. Do not change the project structure without approval.
12. Implement → test → review → continue.
13. Do not add infrastructure without a concrete requirement.
14. Never expose secrets or raw exceptions.
15. Keep ChatLLM provider-independent.

---

# 24. Database Foreign Key Rules

To maintain absolute data integrity, auditability, and clear lifecycle ownership:

### Rule 24.1 — Naming Conventions
- Foreign keys must follow the standard naming convention: `fk_<table_name>_<column_name>_<referred_table_name>`.
- Generated automatically by SQLAlchemy metadata configurations.

### Rule 24.2 — On-Delete Behavior
- **Audit & Prompt Logs**: Must NEVER allow cascade delete. Deleting a User or Session must be blocked (`RESTRICT` or `NO ACTION`) if prompt logs, audit logs, or token usages reference them.
- **Transactional Data**: Safe to use cascade delete (e.g. deleting a `chat_sessions` cascades to delete its associated `chat_messages`).
- **Core Entities**: Roles, Departments, and Users must not be deleted if active links exist (use soft-deletes or `RESTRICT`).

### Rule 24.3 — Nullable Relationships
- Foreign keys must be `nullable=False` unless the business workflow explicitly demands optionality (e.g. `TokenRequest.reviewed_by` is nullable when pending approval).

### Rule 24.4 — Relationship Ownership
- The model declaring the foreign key is the owner of the relationship.
- Back-references (`relationship(..., back_populates=...)`) should only be declared on the parent model when programmatic navigation is explicitly required.

---

# 25. Database Deletion and Soft Delete Policy

To fulfill corporate compliance and strict enterprise auditability, ChatLLM enforces a tiered deletion strategy based on data classification:

### Rule 25.1 — Core Entities (Soft Delete Only)
- **Entities**: `User`, `Role`, `Department`, `AIModel`, `ChatSession`, `EmployeeTokenWallet`.
- **Strategy**: Never physically delete. Deactivation is managed by setting `is_active = False`.
- **Implementation**: Managed by the inherited `is_active` attribute on all entities subclassing `BaseModel`. Queries for active records should filter with `.where(Model.is_active == True)`.

### Rule 25.2 — Ledger & Compliance Records (Immutable)
- **Entities**: `AuditLog`, `PromptLog`, `TokenUsage`, `PromptReward`.
- **Strategy**: Immutable. Once written, these records must NEVER be updated or deleted (neither physical nor soft deletion is permitted).
- **Enforcement**: Database access layers (repositories) must not expose update or delete methods for these entities.

### Rule 25.3 — User Messages
- **Entities**: `ChatMessage`.
- **Strategy**: If an employee deletes a message, it is marked inactive (`is_active = False`) to remove it from view in the client. The underlying prompt and actual completion details remain fully intact and immutable inside `prompt_logs` and `token_usages` for compliance mapping.

---

# 26. Unique Constraint Strategy

To guarantee data reliability, identity consistency, and prevent duplicate registration anomalies:

### Rule 26.1 — Database Level Uniqueness
- Application-level validation is supplementary. Crucial unique business identifiers must be strictly enforced via PostgreSQL unique constraints and index checks.
- Unique index naming must adhere to: `uq_%(table_name)s_%(column_0_name)s`.

### Rule 26.2 — Core Business Uniqueness Constraints
The following attributes are uniquely constrained at the database layer:
- **`User`**: `email` (unique index), `employee_code` (unique index).
- **`Role`**: `name` (unique index).
- **`Department`**: `name` (unique index).
- **`AIModel`**: `model_name` (unique index).
- **`SystemSetting`**: `setting_key` (unique index).
- **`EmployeeTokenWallet`**: `user_id` (unique index).

### Rule 26.3 — Error Translation
- Database-level unique constraint violations (`IntegrityError` in SQLAlchemy) must be intercepted by repository/service layers and translated to normalized API conflict errors (e.g. `VALIDATION_ERROR` with custom messages), preventing raw database tracing details from reaching users.

---

# 27. Database Transaction Management

To ensure atomic state changes and absolute consistency, especially for token wallet adjustments:

### Rule 27.1 — Service Layer Boundaries
- **Transaction Owner**: The Service layer defines and controls transaction boundaries. Repositories must perform operations (`add`, `delete`, `flush`) inside the session but should not commit transaction scopes independently if orchestrated inside a larger business workflow.
- **Scope**: Single-model basic CRUD operations may rely on repository auto-commits. Multi-table workflows (such as *AI Request → Token Reservation → Actual Usage → Wallet Finalization*) must be wrapped in a single service-level atomic transaction block.

### Rule 27.2 — Atomic Operations
- Implement transaction blocks using SQLAlchemy's async context manager:
  ```python
  async with db.begin():
      # Multiple repository modifications
      # Any error raises rollback automatically
  ```
- No partial writes are permitted. If any step fails (e.g., the AI provider call fails or token limits are exceeded), the entire transaction scope must be cleanly rolled back.

### Rule 27.3 — Safe Rollbacks
- In case of non-DB exceptions (e.g., external API timeouts or network failures), services must explicitly catch the exception and trigger `await session.rollback()` to prevent dangling locks or uncommitted partial state in the session context.

---

# 28. FastAPI Database Session Management

To ensure connection efficiency and avoid resource leaks, the database session pattern is strictly scoped to the HTTP request lifecycle:

### Rule 28.1 — Request-Scoped Lifecycle
- **Flow**:
  $$\text{HTTP Request} \longrightarrow \text{Yield AsyncSession} \longrightarrow \text{Repository/Service Operation} \longrightarrow \text{Commit/Rollback} \longrightarrow \text{Session Cleanup}$$
- **FastAPI Dependency injection**:
  Use `get_db` generator (mapped via `DatabaseDep`) to yield request-scoped sessions.
- **Cleanup**: The session is automatically committed or rolled back and explicitly closed at the end of the request via the `get_db` `finally` block, releasing the connection back to the database pool.

### Rule 28.2 — Restrictions & anti-patterns
- **No Global Mutable Sessions**: Sessions must never be declared as global module variables or shared between concurrent requests.
- **No Long-Lived Request Sessions**: Sessions are short-lived. They exist only for the duration of a single HTTP request lifecycle.
- **No Hidden Commits**: Commits must never be hidden inside unrelated query operations in repositories. The transaction owner is always the Service layer.
- **No Silent Failures**: Database exceptions must never be swallowed silently. If a query fails, the exception must propagate to trigger a clean rollback in the `get_db` context manager and log the traceback internally.

---

# 29. Alembic Migration Conventions

To maintain a deterministic database schema lifecycle and prevent unscheduled schema drifts:

### Rule 29.1 — Schema Modifications
- **Alembic Mandatory**: Every schema change (table creation, column modifications, constraints, indices) must be implemented strictly via an Alembic migration script.
- **No Manual Alterations**: Direct manual DDL modification of databases is prohibited.

### Rule 29.2 — Review & Verifiability
- **Human Verification**: Every auto-generated migration file must be reviewed for correctness before being applied to the live environment to ensure no unexpected column changes or missing keys exist.
- **No Meaningless Revisions**: Do not generate empty or boilerplate migrations containing zero DDL modifications.
- **Name Clarity**: Revision messages must be short and explicitly describe the change (e.g. `create_ai_models_table`, `add_is_verified_to_users`).

### Rule 29.3 — Safety Guidelines
- **Destructive Migrations**: Avoid destructive migrations (dropping tables, dropping active columns, reducing data width) in production unless explicitly approved and planned with a data backup/recovery strategy.

---

# 30. Database Testing Guidelines

To ensure schema safety and query accuracy without polluting live databases, the following testing rules apply:

### Rule 30.1 — Test Isolation
- **No Production/Staging Pollution**: Tests must never run or perform write/modify operations against the live production or staging databases.
- **In-Memory Testing**: Use `sqlite+aiosqlite:///:memory:` for fast, self-contained unit and integration testing of repositories, services, and schemas.
- **Fixture Lifecycle**: Use a module or function-scoped `memory_db_session` fixture that creates all tables (`Base.metadata.create_all`) before tests run and disposes of the engine afterward.

### Rule 30.2 — Required Test Coverage
Future model and database implementations must cover:
- **Constraints**: Nullability, string length bounds, default values.
- **Unique Constraints**: Assert duplicate insertions of unique columns (e.g. user emails) raise `IntegrityError`.
- **Foreign Keys**: Assert invalid/missing references raise constraints.
- **Repository Operations**: Verify CRUD logic (create, read, update, delete, count) matches SQL constructs.
- **Transaction Rollbacks**: Assert transaction failure cascades rollback to prevent partial writes.
- **Relationships**: Verify eager/lazy loading of mapped relationships.

### Rule 30.3 — No Placeholder Tests
- Do not write mock or speculative business logic tests for features that are not yet implemented in the current phase.

---

# 31. Database Error Translation Policy

To protect system security and prevent leaking internal schema configurations or connection properties:

### Rule 31.1 — Direct Exposure Prohibition
- **Exclusion**: Database exception tracebacks, SQL queries, database connection strings, database credentials, and PostgreSQL internals must NEVER be exposed directly in API responses.
- **Normalization**: All raw database exceptions must be caught and normalized into standardized application-level errors.

### Rule 31.2 — Exception Mapping Matrix
Raw database exceptions must be translated at the boundary layer according to this matrix:
- **`sqlalchemy.exc.IntegrityError`** (Unique constraint / FK violations):
  Map to HTTP 409 Conflict or HTTP 400 Bad Request, returning code `VALIDATION_ERROR` or `CONFLICT_ERROR` with a user-friendly field-level error explanation.
- **`sqlalchemy.exc.OperationalError`** (PostgreSQL down, connection timeout, lock timeouts):
  Map to HTTP 503 Service Unavailable, returning code `DATABASE_ERROR` with a generic description ("Database service temporarily unavailable").
- **Other Unhandled Database Errors**:
  Map to HTTP 500 Internal Server Error, returning code `INTERNAL_ERROR` with a generic description ("An unexpected error occurred. Please try again later.").

### Rule 31.3 — Diagnostic Logging
- While hiding exception details from users is mandatory, the application must log the complete traceback, exact failing SQL query, and exception context internally at the `error` or `critical` level for developers.

---

# 32. Database Performance Principles

To ensure efficient throughput, fast query times, and minimal memory consumption without premature optimization:

### Rule 32.1 — Query Design & Pagination
- **Avoid N+1 Queries**: Never fetch related objects inside a loop. Always use explicit joins or eager loading strategies (e.g. `joinedload`, `selectinload` in SQLAlchemy) when related records are required.
- **Avoid Unbounded Queries**: Enforce pagination on all list queries. Set safe defaults (e.g., `skip=0, limit=100`) and enforce strict maximum caps on API limits (e.g., maximum `limit=1000`) to prevent out-of-memory errors on large tables.
- **Avoid Unnecessary Columns**: For large columns (such as prompt texts or completions in `prompt_logs` or `chat_messages`), defer loading or project only specific columns (`select(Model.col1, Model.col2)`) when displaying lists or summary dashboards.
- **Avoid Unnecessary Joins**: Do not include joins to unrelated lookup tables if the fields are not needed in the result set.

### Rule 32.2 — Schema Optimization
- **Index Pattern Alignment**: Indexes must be configured on columns frequently used for search filters, sorting, or foreign key joins (e.g. `User.email`, `PromptLog.prompt_hash`, `EmployeeTokenWallet.user_id`).
- **Database-Level Constraints**: Rely on PostgreSQL's query optimizer and engine by enforcing unique, foreign key, and check constraints at the database layer rather than replicating checks entirely in application loops.
- **Optimize Later**: Keep database designs clean and standard. Do not introduce speculative indexes, materialized views, caching layers, or denormalization patterns until profiling tools identify concrete latency bottlenecks.

---

# 33. Database Security Principles

To protect corporate data assets, prevent injection vectors, and enforce credentials isolation:

### Rule 33.1 — Credentials Isolation
- **Configuration Bound**: Database connection credentials (host, username, password, port, database name) must be loaded dynamically from environment variables using `pydantic-settings` (`Settings.DATABASE_URL`).
- **No Hardcoding**: Database credentials or connection URIs must never be hardcoded into configuration defaults or python scripts.
- **Backend Enclosed**: Credentials and connection variables must remain encapsulated within the backend server environment and must never be exposed or returned to the client frontend under any circumstances.

### Rule 33.2 — Database Access Controls
- **Direct Access Prohibition**: The client frontend must never have direct read or write access to the PostgreSQL database or any query execution endpoints.
- **SQL Injection Prevention**: Direct manual execution of raw, string-concatenated SQL queries is strictly prohibited. All queries must be executed using SQLAlchemy's parameterized expression engine or parameterized `text()` constructs.
- **Exception Protection**: Raw database tracebacks, PostgreSQL connection exceptions, constraint violation details, and SQL statements must never be returned in HTTP response payloads.

### Rule 33.3 — Data Integrity & Storage Minimization
- **Minimize Sensitive Storage**: Do not store passwords, raw secret keys, or sensitive employee PII in database columns unless encrypted or hashed using approved cryptographic functions (e.g. Argon2 for password hashing).
- **Ledger Security**: Financial ledger details (available tokens, carry forward limit, tokens used today) and transaction records are immutable. Their integrity is preserved by restricting write paths and strictly blocking delete workflows.









