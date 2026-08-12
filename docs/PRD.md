# ChatLLM — Product Requirements Document (PRD)

## 1. Product Overview

**ChatLLM** is a centralized enterprise AI platform that gives an organization's employees controlled access to multiple LLM providers through one application while managing permissions, token budgets, AI usage, prompt intelligence, rewards, and complete auditability.

ChatLLM is designed for organizations that want employees to use AI productively without requiring employees to maintain separate accounts and workflows across multiple AI platforms.

### Core idea

```text
Organization
     ↓
ChatLLM
     ↓
One controlled AI platform
     ↓
Multiple LLM Providers
     ├── OpenAI
     ├── Anthropic
     └── Google Gemini
```

The organization controls access, users, roles, departments, AI models, token policies, and auditability.

---

## 2. Target Users

### Primary Target User — Organization Employee

The primary application user is an **employee of an organization**.

Employees use ChatLLM to:

- Start AI conversations.
- Select an approved AI model.
- Send prompts.
- Receive AI responses.
- View chat history.
- Monitor token usage.
- Request additional tokens when required.
- Receive prompt improvement suggestions.
- Benefit from prompt reuse/reward functionality.

### Administrative Users

Administrators manage the platform and organization-level controls.

They can:

- Manage users.
- Manage roles.
- Manage departments.
- Manage AI providers/models.
- Configure token policies.
- Review token requests.
- Manage system settings.
- Review audit activity.
- Monitor usage and analytics.

---

## 3. Problem Statement

Organizations increasingly use multiple AI providers, but employees may work across disconnected tools.

This creates problems such as:

- No centralized access control.
- No consistent employee/token budget.
- Limited visibility into AI usage.
- Difficulty controlling approved AI models.
- No centralized audit trail.
- Repeated prompts without improvement.
- Useful prompts are difficult to discover and reuse.
- AI usage costs are difficult to govern.

ChatLLM addresses these problems through one centralized platform.

---

## 4. Product Goals

### Primary goals

1. Provide employees with one interface for multiple LLM providers.
2. Give organizations centralized access control.
3. Implement role-based access control (RBAC).
4. Give employees controlled token budgets.
5. Track actual AI usage.
6. Maintain a token transaction ledger.
7. Record important system and AI activity.
8. Detect repeated/similar prompts.
9. Suggest improved prompts.
10. Reward useful prompts when reused by other employees.
11. Create an architecture that can support additional LLM providers.
12. Maintain strong security and clear AI boundaries.

### Non-goals for the initial version

The initial version should not automatically become:

- A general-purpose autonomous AI agent platform.
- An arbitrary code execution platform.
- A direct database manipulation interface for AI.
- A replacement for every enterprise business system.
- A large AI framework abstraction without a concrete requirement.

Additional capabilities can be introduced through future phases.

---

## 5. Core Features

### 5.1 Authentication

Employees and administrators must authenticate securely.

Requirements:

- Login.
- JWT/access-token based authentication.
- Secure password hashing.
- Active/inactive account handling.
- Current-user identification.
- Login tracking.

---

### 5.2 Roles and RBAC

Administrators can create and manage roles.

Initial examples:

```text
Super Admin
Admin
Manager
Employee
```

The system should not hardcode these roles as the only possible roles.

RBAC must control access to protected operations.

---

### 5.3 Departments

Administrators can create and manage departments.

Examples:

```text
HR
Finance
Sales
Marketing
IT
Operations
```

An employee can be assigned to a department.

Department-specific policies may be introduced later.

---

### 5.4 Employee Management

Administrators can:

- Create employees.
- Update employee information.
- Assign roles.
- Assign departments.
- Activate/deactivate accounts.
- View employee status.
- View usage information where permitted.

The exact password/invitation mechanism will be finalized during the authentication phase.

---

### 5.5 AI Provider and Model Management

ChatLLM must support multiple LLM providers through a common AI Gateway.

Initial provider targets:

```text
OpenAI
Anthropic
Google Gemini
```

Administrators should be able to configure approved models.

Model configuration may include:

- Provider.
- Model identifier.
- Active/inactive status.
- Input token limits.
- Output token limits.
- Pricing information.
- Availability.
- Policy configuration.

---

### 5.6 Token Wallet

Every eligible employee receives a token wallet.

The wallet can contain:

- Daily token allocation.
- Carry-forward tokens.
- Bonus tokens.
- Available tokens.
- Daily usage.
- Last reset date.

The system must separately maintain:

```text
Wallet
=
Current balance/state

Token Usage
=
Actual AI consumption

Token Transaction
=
Reason/history for balance changes
```

---

### 5.7 Chat Sessions

Employees can:

- Create a chat session.
- Select an approved AI model.
- Send messages.
- Receive responses.
- Continue conversations.
- View chat history.

The architecture should allow model selection at the message level if the product later permits switching models inside a session.

---

### 5.8 Token Validation

Before an AI request is sent:

```text
Authentication
 ↓
Authorization
 ↓
Token validation/reservation
 ↓
AI request
```

The system must not call an external AI provider before the required token policy checks.

If the employee does not have sufficient tokens:

```text
AI request
   ↓
Blocked
   ↓
Token request option
```

---

### 5.9 AI Gateway

All LLM provider calls must pass through a centralized AI Gateway.

```text
Chat Service
     ↓
AI Gateway
     ↓
Provider Adapter
     ↓
OpenAI / Anthropic / Gemini
```

The Gateway is responsible for:

- Provider selection.
- Model resolution.
- Request normalization.
- Response normalization.
- Provider errors.
- Timeouts.
- Controlled retries.
- Usage extraction.
- AI policy enforcement.

---

### 5.10 Prompt Logging

Important prompt activity should be recorded.

Prompt logs can contain:

- User.
- Session.
- Message.
- Model.
- Prompt hash.
- Prompt status.
- Response metadata.
- Usage metadata.
- Similarity/reuse information.

Sensitive prompt data must be handled according to the organization's privacy policy.

---

### 5.11 Prompt Intelligence

ChatLLM should identify repeated/similar prompts.

Initial progression:

```text
Exact hash
 ↓
Normalized comparison
 ↓
Similarity
 ↓
Semantic similarity when required
```

If an employee repeatedly asks substantially similar questions, ChatLLM can suggest a better prompt.

The suggestion threshold should be configurable.

---

### 5.12 Prompt Reuse and Rewards

If Employee A creates a useful prompt and Employee B later uses a sufficiently similar prompt:

```text
Employee A
    ↓
Original Prompt
    ↓
Employee B
    ↓
Similar/Reused Prompt
    ↓
Reward Employee A
```

Rules must prevent:

- Self-reuse rewards.
- Duplicate rewards for the same reuse event.
- Rewards when similarity does not meet the configured threshold.

---

### 5.13 Token Requests

Employees can request additional tokens.

Flow:

```text
Employee
 ↓
Insufficient balance
 ↓
Token Request
 ↓
Pending
 ↓
Admin Review
 ├── Approve
 └── Reject
```

An approval must create the appropriate wallet update, token transaction, and audit event.

---

### 5.14 Audit Logging

Important actions must be auditable.

Examples:

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

Audit records should be treated as business/security records, not merely debugging logs.

---

## 6. Employee Experience

Expected employee journey:

```text
Login
 ↓
Employee Dashboard
 ↓
Start Chat
 ↓
Select AI Model
 ↓
Enter Prompt
 ↓
Token Check
 ↓
Prompt Processing
 ↓
AI Response
 ↓
Usage Recorded
 ↓
Wallet Updated
 ↓
Audit Recorded
```

Employee-facing areas can eventually include:

```text
Dashboard
Chat
Chat History
Token Wallet
Token Usage
Prompt Suggestions
Rewards
Token Requests
Profile
```

---

## 7. Admin Experience

Expected administrator journey:

```text
Admin Login
 ↓
Admin Dashboard
 ↓
Roles / Departments
 ↓
Users
 ↓
AI Models
 ↓
Token Policies
 ↓
Token Requests
 ↓
Audit Logs
 ↓
Analytics
 ↓
System Settings
```

---

## 8. Success Criteria

ChatLLM MVP is successful when:

- An employee can authenticate.
- RBAC is enforced.
- An admin can manage employees.
- An employee receives a token wallet.
- An employee can select an approved AI model.
- The platform can call at least one LLM provider through the AI Gateway.
- Token availability is checked before AI calls.
- Actual usage is recorded.
- Wallet transactions are recorded.
- Chat history is persisted.
- Important actions are audited.
- Provider failures do not corrupt wallet state.
- Additional providers can be added without rewriting ChatService.

---

## 9. Future Expansion

Potential future capabilities:

- Additional LLM providers.
- Department-specific AI policies.
- Enterprise SSO/identity providers.
- RAG/document knowledge.
- Embeddings and vector search.
- Controlled AI tools/function calling.
- Advanced analytics.
- Cost reporting.
- AI usage budgets by department.
- Enterprise data-loss prevention policies.
- Model routing and fallback strategies.
