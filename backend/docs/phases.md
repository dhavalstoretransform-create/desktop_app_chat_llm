# ChatLLM — Development Phases

## Development Method

Each phase follows:

```text
Understand
 ↓
Design
 ↓
Implement file-by-file
 ↓
Test
 ↓
Review
 ↓
Document
 ↓
Next phase
```

Do not move to the next major phase while the current phase has unresolved foundational failures.

---

# Phase 1 — Project Foundation

### Objective

Create a clean, runnable ChatLLM backend and initialize the frontend.

### Modules

- Repository structure.
- Python virtual environment.
- FastAPI application.
- Configuration.
- Environment variables.
- Basic health endpoint.
- Frontend initialization.
- Git configuration.
- Development tooling.

### Deliverable

```text
GET /health
```

works successfully.

---

# Phase 2 — Database + Models

### Objective

Create the database foundation.

### Modules

- PostgreSQL connection.
- SQLAlchemy setup.
- Base model.
- Alembic.
- Migration workflow.
- Common timestamps/IDs.
- Initial domain model strategy.

### Deliverable

Database connection and migration system work correctly.

---

# Phase 3 — Authentication

### Objective

Secure employee/admin access.

### Modules

- User credentials.
- Password hashing.
- Login.
- JWT.
- Current user.
- Account status.
- Authentication dependencies.
- Authentication errors.

### Deliverable

A user can securely log in and access protected endpoints.

---

# Phase 4 — RBAC

### Objective

Control what authenticated users are allowed to do.

### Modules

- Roles.
- Permissions.
- Role assignment.
- Authorization dependencies.
- Admin protection.
- Employee access boundaries.

### Deliverable

Admin-only operations cannot be accessed by ordinary employees.

---

# Phase 5 — Departments

### Objective

Introduce organization structure.

### Modules

- Department CRUD.
- Department status.
- Employee department assignment.
- Department validation.

### Deliverable

Employees belong to an organization department.

---

# Phase 6 — User / Employee Management

### Objective

Allow administrators to manage employees.

### Modules

- Employee creation.
- Employee update.
- Employee activation/deactivation.
- Role assignment.
- Department assignment.
- Employee code.
- User status.

### Deliverable

Admin can manage the employee population.

---

# Phase 7 — AI Model Management

### Objective

Define which AI providers/models ChatLLM supports.

### Modules

- Providers.
- Models.
- Model status.
- Provider/model configuration.
- Input/output limits.
- Pricing configuration.

### Deliverable

ChatLLM has a controlled list of available AI models.

---

# Phase 8 — Token Wallet + Ledger

### Objective

Build the token accounting foundation.

### Modules

- Employee wallet.
- Daily allocation.
- Carry-forward.
- Bonus tokens.
- Available balance.
- Token transactions.
- Atomic balance operations.

### Deliverable

Employee token balances are accurate and auditable.

---

# Phase 9 — AI Gateway

### Objective

Connect multiple LLM providers behind one abstraction.

### Modules

- Provider interface.
- AI Gateway.
- OpenAI adapter.
- Anthropic adapter.
- Gemini adapter.
- Normalized response.
- Provider error normalization.
- Timeout/retry policy.

### Deliverable

ChatLLM can call an approved provider through the Gateway.

---

# Phase 10 — Chat Sessions + Messages

### Objective

Implement employee conversations.

### Modules

- Chat session.
- Chat message.
- Message history.
- Model selection.
- Prompt submission.
- AI response persistence.

### Deliverable

Employee can have a complete AI conversation.

---

# Phase 11 — Token Usage + Deduction

### Objective

Connect actual AI usage to wallet accounting.

### Modules

- Provider usage extraction.
- Token usage record.
- Reservation/finalization.
- Wallet deduction.
- Token transaction.
- Failure rollback/release.

### Deliverable

Successful AI requests are accurately accounted for.

---

# Phase 12 — Prompt Logging

### Objective

Create the foundation for prompt intelligence.

### Modules

- Prompt log.
- Prompt hash.
- Prompt status.
- Model/session/user association.
- Processing status.
- Failure tracking.

### Deliverable

ChatLLM can trace prompt processing.

---

# Phase 13 — Prompt Similarity

### Objective

Detect repeated or similar prompts.

### Modules

- Prompt normalization.
- Exact hash matching.
- Similarity abstraction.
- Similarity thresholds.
- Repetition detection.

### Deliverable

ChatLLM can identify repeated/similar prompts.

---

# Phase 14 — Prompt Suggestions

### Objective

Help employees improve repeated prompts.

### Modules

- Suggestion threshold.
- Suggested prompt generation.
- Suggestion persistence.
- Employee suggestion display.
- Suggestion status.

### Deliverable

Repeated prompting can trigger a useful improvement suggestion.

---

# Phase 15 — Prompt Reuse + Rewards

### Objective

Reward valuable prompts reused by other employees.

### Modules

- Original prompt.
- Reused prompt.
- Similarity score.
- Reward rules.
- Duplicate prevention.
- Self-reuse prevention.
- Reward history.

### Deliverable

Valid cross-employee prompt reuse can generate a reward.

---

# Phase 16 — Token Requests

### Objective

Allow employees to request additional tokens.

### Modules

- Token request creation.
- Request reason.
- Pending state.
- Admin approval.
- Admin rejection.
- Wallet update.
- Token transaction.
- Audit event.

### Deliverable

Complete token request lifecycle.

---

# Phase 17 — Audit Logging

### Objective

Make business/security actions traceable.

### Modules

- Audit event model.
- Event types.
- Actor.
- Resource.
- Action.
- Timestamp.
- Request ID.
- Admin audit viewing.

### Deliverable

Important platform events are auditable.

---

# Phase 18 — Background Jobs / Daily Reset

### Objective

Automate token lifecycle operations.

### Modules

- Daily reset.
- Carry-forward.
- Token expiration if required.
- Cleanup.
- Scheduled audit events.

### Deliverable

Daily token policy works automatically.

---

# Phase 19 — Admin Dashboard

### Objective

Provide the administrative application.

### Modules

- Dashboard.
- Users.
- Roles.
- Departments.
- AI models.
- Token requests.
- Token management.
- Audit logs.
- Settings.
- Analytics foundation.

### Deliverable

Administrators can manage ChatLLM through the UI.

---

# Phase 20 — Employee Dashboard

### Objective

Provide the employee application.

### Modules

- Employee dashboard.
- Chat.
- Chat history.
- Model selector.
- Token wallet.
- Usage.
- Prompt suggestions.
- Rewards.
- Token requests.
- Profile.

### Deliverable

Employees can use ChatLLM end-to-end.

---

# Phase 21 — Integration Testing

### Objective

Validate cross-module behavior.

### Test flows

```text
Login
 ↓
RBAC
 ↓
Chat
 ↓
Token check
 ↓
AI Gateway
 ↓
AI response
 ↓
Usage
 ↓
Wallet
 ↓
Ledger
 ↓
Audit
```

Also test:

- AI failure.
- Timeout.
- Retry.
- Token shortage.
- Duplicate requests.
- Prompt reuse.
- Reward duplication.
- Permission violations.

---

# Phase 22 — Production Hardening

### Objective

Prepare ChatLLM for production.

### Modules

- Security review.
- Rate limiting.
- CORS.
- Secret management.
- Error handling review.
- Logging.
- Monitoring.
- Database backup strategy.
- Performance review.
- Provider failure strategy.
- Deployment configuration.
- Production environment separation.

### Final deliverable

Production-ready ChatLLM.

---

## Phase Naming Convention

Use:

```text
phase-01-foundation
phase-02-database
phase-03-authentication
phase-04-rbac
...
```

Do not create all phase folders inside the application source code. Phases are development milestones, not necessarily Python packages.
