# AI-Powered Todo Chatbot Constitution
<!-- Hackathon II: Spec-Driven Development Project -->

## Project Mission
Build a production-ready AI-powered conversational interface for todo task management using OpenAI Agents SDK, MCP (Model Context Protocol), and ChatKit. Enable users to manage tasks through natural language on a stateless, horizontally-scalable backend.

---

## Core Principles

### I. Stateless Server Architecture (NON-NEGOTIABLE)
Every request is independent and reproducible. All state persists to the database; server holds zero application state. Benefits:
- Horizontal scalability: any backend instance handles any request
- Resilience: server restarts don't lose conversation state
- Testability: each request is deterministic and reproducible
- Load balancer can route traffic freely

**Enforcement:** No in-memory caches, session stores, or thread-local state. Database is the source of truth.

### II. MCP Tools as the AI Interface
AI agents interact exclusively with task operations through MCP tools. Each tool:
- Is stateless and idempotent where applicable
- Stores side effects in the database immediately
- Returns consistent, documented responses
- Handles user_id validation and authorization

**Toolset:**
- `add_task`: Create new task
- `list_tasks`: Retrieve tasks (filter by status: all/pending/completed)
- `complete_task`: Mark task completed
- `delete_task`: Remove task
- `update_task`: Modify title or description

### III. Conversation History as Source of Truth
Full conversation context persists to the database and is reconstructed per-request using `ThreadItemConverter`. Agent memory comes from fetching historical messages, never from runtime state.

**Pattern:**
1. Receive user message
2. Fetch conversation history + new message
3. Pass full context to agent
4. Store response in database
5. Return to client
6. Clear all runtime state

### IV. Framework Correctness (ChatKit/OpenAI Agents)
Use official SDKs correctly:
- **ChatKit Python (openai-chatkit ≤1.4.0):** Implement all 14 Store abstract methods; use `chatkit.store` (singular), not `chatkit.stores`
- **OpenAI Agents SDK:** Use `Runner.run_streamed()` for agent execution; employ `ThreadItemConverter` for history
- **ChatKit React (@openai/chatkit-react):** Configure `domainKey`, include CDN script, use `label` (not `name`) for prompts
- **LiteLLM integration:** Apply ID mapping fix when using non-OpenAI providers to prevent message collisions

### V. User-Centric Natural Language (Non-Technical)
The agent understands and responds to natural language commands:
- "Add a task to buy groceries" → `add_task(title="Buy groceries")`
- "Show me all my tasks" → `list_tasks(status="all")`
- "Mark task 3 as complete" → `complete_task(task_id=3)`
- "Delete the meeting task" → `list_tasks` then `delete_task`
- "Change task 1 to 'Call mom tonight'" → `update_task(task_id=1, title="Call mom tonight")`

Agent always confirms actions with friendly, conversational responses.

### VI. Authentication & Authorization (Boundary Security)
- Every request validated for user_id (from auth middleware)
- All database queries filtered by user_id
- MCP tools reject requests with missing/invalid user_id
- Chat endpoint only accessible to authenticated users (dashboard)
- Bot inaccessible on landing page

**Implementation:** Leverage Better Auth for session management; centralize user_id extraction in middleware.

### VII. Database-First Design
- **ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Database:** Neon Serverless PostgreSQL
- **Models:** Task, Conversation, Message
- **Migrations:** Version-controlled SQL or Alembic scripts
- **Schema Evolution:** Non-destructive migrations; always backward-compatible

**Schema:**
```
Task: user_id, id, title, description, completed, created_at, updated_at
Conversation: user_id, id, created_at, updated_at
Message: user_id, id, conversation_id, role (user/assistant), content, created_at
```

### VIII. Error Handling & Graceful Degradation
- MCP tools return structured errors (task_not_found, unauthorized, invalid_params)
- Agent acknowledges errors and suggests alternatives
- No stack traces to frontend
- Database unavailability does not crash the server; return 503 Service Unavailable
- Tool failures logged but handled gracefully

### IX. Testability & Observability
- **Unit Tests:** MCP tools tested in isolation with mock database
- **Integration Tests:** End-to-end chat flows with real database (test fixture)
- **Logging:** Structured logs (JSON) with context: user_id, conversation_id, tool_name, latency
- **Metrics:** Track tool invocation counts, latency, error rates
- **Debug Endpoint:** `/debug/threads` to inspect conversation state (development only)

### X. Simplicity & YAGNI
- No premature abstraction; avoid patterns not yet needed
- Features only when explicitly required
- Documentation auto-generated from code; no redundant markdown
- Single responsibility per module; minimal coupling

---

## Technology Stack (Locked)

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | OpenAI ChatKit React | @openai/chatkit-react ^1.3.0 |
| **Frontend Build** | Vite / Next.js | Latest |
| **Backend API** | Python FastAPI | 0.115.6+ |
| **AI Framework** | OpenAI Agents SDK | 0.6.2+ |
| **MCP Server** | Official MCP SDK | Latest stable |
| **Multi-Provider LLM** | LiteLLM | Latest |
| **ORM** | SQLModel | Latest |
| **Database** | Neon Serverless PostgreSQL | Latest |
| **Authentication** | Better Auth | Latest |
| **Server** | Uvicorn | 0.32.1+ |

---

## Architecture Constraints

### Frontend (ChatKit React)
- Chat accessible **only on dashboard**, not landing page
- Popup layout (floating button + 420x600px chat window) or full-page, user's choice
- Single chat instance per session
- Domain allowlist configured for production
- CDN script (`chatkit.js`) included in `index.html`

### Backend (FastAPI + OpenAI Agents)
- Single `POST /api/{user_id}/chat` endpoint
- Request: `{ conversation_id?: int, message: string }`
- Response: `{ conversation_id: int, response: string, tool_calls: array }`
- MCP server runs as subprocess or embedded in FastAPI
- Agent streams responses; client consumes with Server-Sent Events (SSE) or WebSocket if needed

### Database
- Three core tables: Task, Conversation, Message
- Row-level security: all queries filtered by user_id
- Connection pooling via SQLModel/SQLAlchemy
- Transactions maintain consistency across multi-tool operations

---

## Quality Gates (Non-Negotiable)

1. **Code Review:** All PRs reviewed before merge; constitution compliance verified
2. **Testing:**
   - Unit: all MCP tools have 100% branch coverage
   - Integration: chat flow e2e test for each major feature
   - Manual: UAT on staging before production deployment
3. **Security Scan:** Dependency audit (pip, npm) on every merge
4. **Database Migration:** Tested on staging first; rollback plan documented
5. **Documentation:** README, architecture diagram, MCP tool specs included in repo

---

## Development Workflow

### Per-Feature Cycle
1. **Spec:** Feature documented in `specs/<feature>/spec.md`
2. **Plan:** Architecture + task breakdown in `specs/<feature>/plan.md`
3. **Tasks:** Granular, testable tasks in `specs/<feature>/tasks.md`
4. **Implementation:** Red-Green-Refactor; tests written before code
5. **Review:** Constitution compliance + test coverage verified
6. **Deployment:** Staging → Production with rollback plan

### Branching & Commits
- Main branch: always deployable
- Feature branches: `feature/<name>`
- Commits: atomic, descriptive, reference spec/task
- PRs: link to spec/plan/tasks

---

## Security Requirements

### Authentication & Authorization
- Better Auth handles session validation
- User identity extracted in middleware; all endpoints require auth
- user_id passed as path parameter; validated against session
- MCP tools reject unauthorized requests

### Data Protection
- Neon connection: TLS/SSL enforced
- No secrets in code; all in `.env` (git-ignored)
- Password hashing: delegated to Better Auth
- Audit logging: conversation metadata (who/what/when) stored

### Input Validation
- User message: max 5000 chars, sanitized before storage
- Task title/description: max 1000 chars each
- Tool parameters: strict type validation in MCP server
- SQL injection: prevented by SQLModel parameterized queries

---

## Performance Standards (SLOs)

| Metric | Target | Notes |
|--------|--------|-------|
| **Chat endpoint p95 latency** | 3s | Includes agent execution + DB round-trips |
| **MCP tool latency (avg)** | 500ms | Database operations |
| **Database query p99** | 100ms | Simple SELECT/INSERT |
| **Concurrent users** | 1000+ | Horizontal scaling via stateless design |
| **Conversation recovery time** | < 100ms | Resume from history post-restart |

---

## Deployment & Operations

### Environment Management
- **Development:** Local FastAPI + SQLite (or local Postgres)
- **Staging:** FastAPI on Docker, Neon staging DB, ChatKit test domain
- **Production:** FastAPI on Kubernetes/Railway/Vercel, Neon production DB, ChatKit domain configured

### Database Migrations
- Versioned in Git (Alembic or raw SQL)
- Tested on staging before production
- Always backward-compatible (add columns, don't remove)
- Rollback script included for each migration

### Monitoring & Alerts
- **Logs:** Structured JSON with user_id, conversation_id, tool_name, duration
- **Metrics:** Prometheus or similar (tool invocation counts, latencies, errors)
- **Alerts:** Tool error rate > 1%, latency p95 > 5s, database down
- **On-Call:** SLA for incident response

---

## Governance & Evolution

### Constitution Authority
- Constitution supersedes all other project documents and practices
- Amendments require documented rationale, team consensus, and migration plan
- Version history maintained; changelog in git commits

### Decision Framework
1. **Architecturally Significant?** → Suggest ADR (`/sp.adr`)
2. **Violates a principle?** → Reject; propose alternative
3. **Clarification needed?** → Use `sp.clarify` to refine requirements
4. **Ready to build?** → Use `sp.plan`, `sp.tasks`, `sp.implement`

### Complexity Justification
- If a feature violates simplicity (Principle X), document why and trade-offs
- Premature optimization rejected unless performance SLOs demand it
- Code review verifies each new concept/library/pattern is essential

---

## Success Criteria (MVP Ready)

✅ AI agent understands 5 core natural language commands  
✅ MCP tools stateless and database-backed  
✅ Full conversation history reconstructed per-request  
✅ Chat endpoint returns response within 3s p95  
✅ Horizontal scaling tested (stateless proven)  
✅ Authentication enforced; bot dashboard-only  
✅ Unit & integration test coverage ≥ 80%  
✅ README includes setup, architecture diagram, MCP spec  
✅ Database migrations versioned and tested  
✅ Production deployment script ready  

---

## References

- **Spec:** `/specs/chatbot/spec.md` (requirements, scope, deliverables)
- **Architecture:** `/specs/chatbot/plan.md` (design decisions, data models, API contracts)
- **Tasks:** `/specs/chatbot/tasks.md` (implementation breakdown)
- **ADRs:** `/history/adr/` (significant decisions)
- **Prompts:** `/history/prompts/` (development diary)

---

**Version**: 1.0.0 | **Ratified**: 2025-01-20 | **Last Amended**: 2025-01-20
| **Status**: Active
