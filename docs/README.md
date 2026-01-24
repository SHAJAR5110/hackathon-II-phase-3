# AI-Powered Todo Chatbot - Hackathon II: Spec-Driven Development

An enterprise-grade conversational interface for todo task management using MCP (Model Context Protocol), OpenAI Agents SDK, and ChatKit.

## 🎯 Project Overview

Transform task management through natural language. Users interact with an AI-powered chatbot to:
- ✅ Create tasks: "Add a task to buy groceries"
- ✅ List tasks: "Show me all my tasks" / "What's pending?"
- ✅ Complete tasks: "Mark task 3 as complete"
- ✅ Update tasks: "Change task 1 to 'Call mom tonight'"
- ✅ Delete tasks: "Delete the meeting task"

**Architecture**: Stateless FastAPI backend with database-persisted conversation history. MCP tools handle all task operations. Horizontal scalability through state-per-request design.

---

## 📋 Documentation

| Document | Purpose |
|----------|---------|
| [Constitution](.specify/memory/constitution.md) | 10 core principles, quality gates, deployment standards |
| [Feature Spec](specs/1-chatbot-ai/spec.md) | 6 user stories, 18 FRs, 10 success criteria |
| [Spec Checklist](specs/1-chatbot-ai/checklists/requirements.md) | 24-item specification quality validation (all pass) |
| [Architecture Plan](specs/1-chatbot-ai/plan.md) | Design decisions, MCP tools, API contracts (TBD) |
| [Implementation Tasks](specs/1-chatbot-ai/tasks.md) | Breakdown into actionable, dependency-ordered tasks (TBD) |

---

## 🏗️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | React + OpenAI ChatKit | @openai/chatkit-react ^1.3.0 |
| **Backend API** | FastAPI | 0.115.6+ |
| **AI Framework** | OpenAI Agents SDK | 0.6.2+ |
| **MCP Server** | Official MCP SDK | Latest |
| **Multi-Provider LLM** | LiteLLM | Latest |
| **ORM** | SQLModel | Latest |
| **Database** | Neon Serverless PostgreSQL | Latest |
| **Authentication** | Better Auth | Latest |
| **Server** | Uvicorn | 0.32.1+ |

---

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- PostgreSQL (local) or Neon account (cloud)

### Backend Setup

```bash
# Clone repo
git clone <repo-url>
cd phase3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Neon connection string and OpenAI API key

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
# Server runs on http://localhost:8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with backend URL

# Start dev server
npm run dev
# UI runs on http://localhost:5173
```

### Verify Integration

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# Expected response:
# {
#   "conversation_id": 1,
#   "response": "I've added 'Buy groceries' to your task list!",
#   "tool_calls": [{"tool": "add_task", "params": {...}}]
# }
```

---

## 📚 MCP Tools Specification

Five stateless tools expose task operations:

### 1. `add_task`
**Purpose**: Create new task  
**Parameters**: `user_id` (required), `title` (required), `description` (optional)  
**Returns**: `task_id`, `status`, `title`  
**Example**:
```json
{"user_id": "shajar", "title": "Buy groceries", "description": "Milk, eggs, bread"}
→ {"task_id": 5, "status": "created", "title": "Buy groceries"}
```

### 2. `list_tasks`
**Purpose**: Retrieve tasks  
**Parameters**: `user_id` (required), `status` (optional: "all", "pending", "completed")  
**Returns**: Array of task objects  
**Example**:
```json
{"user_id": "shajar", "status": "pending"}
→ [{"id": 1, "title": "Buy groceries", "completed": false}, ...]
```

### 3. `complete_task`
**Purpose**: Mark task completed  
**Parameters**: `user_id` (required), `task_id` (required)  
**Returns**: `task_id`, `status`, `title`  
**Example**:
```json
{"user_id": "shajar", "task_id": 3}
→ {"task_id": 3, "status": "completed", "title": "Call mom"}
```

### 4. `delete_task`
**Purpose**: Remove task  
**Parameters**: `user_id` (required), `task_id` (required)  
**Returns**: `task_id`, `status`, `title`  
**Example**:
```json
{"user_id": "shajar", "task_id": 2}
→ {"task_id": 2, "status": "deleted", "title": "Old task"}
```

### 5. `update_task`
**Purpose**: Modify task  
**Parameters**: `user_id` (required), `task_id` (required), `title` (optional), `description` (optional)  
**Returns**: `task_id`, `status`, `title`  
**Example**:
```json
{"user_id": "shajar", "task_id": 1, "title": "Buy groceries and fruits"}
→ {"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}
```

---

## 🗄️ Database Schema

### Task
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  title VARCHAR(1000) NOT NULL,
  description VARCHAR(1000),
  completed BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, id)
);
```

### Conversation
```sql
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, id)
);
```

### Message
```sql
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  conversation_id INTEGER NOT NULL REFERENCES conversations(id),
  role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES conversations(user_id)
);
```

---

## 🔒 Security & Best Practices

### Authentication
- All requests require authenticated `user_id` (from Better Auth)
- User_id validated in middleware; all queries filtered by user_id
- Prevents cross-user data access

### Database
- Parameterized queries (SQLModel prevents SQL injection)
- TLS/SSL enforced for Neon connections
- Connection pooling with overflow protection

### API
- Input validation: message ≤5000 chars, title ≤1000 chars
- Rate limiting per user (production)
- Error responses without stack traces

### Secrets
- No hardcoded credentials; all in `.env`
- `.env` git-ignored
- Database password, API keys in environment variables

---

## 📊 Performance Targets (SLOs)

| Metric | Target |
|--------|--------|
| Add task (p95 latency) | ≤ 3 seconds |
| List tasks (p95 latency) | ≤ 2 seconds |
| MCP tool success rate | ≥ 95% |
| Concurrent users | 100+ |
| Data loss on restart | 0 (all persisted) |
| NL command interpretation | ≥ 90% accuracy |

---

## 🧪 Testing

### Unit Tests
```bash
pytest tests/unit/test_mcp_tools.py -v
```

### Integration Tests
```bash
pytest tests/integration/test_chat_flow.py -v
```

### End-to-End Tests
```bash
pytest tests/e2e/test_chatbot.py -v
```

### Coverage
```bash
pytest --cov=app tests/ --cov-report=html
```

---

## 📈 Monitoring & Logging

### Structured Logging
All logs include: `user_id`, `conversation_id`, `tool_name`, `latency`, `status`

```python
logger.info("chat_endpoint_called", extra={
    "user_id": user_id,
    "conversation_id": conversation_id,
    "tool_name": "add_task",
    "latency_ms": 245,
    "status": "success"
})
```

### Metrics to Track
- Tool invocation counts
- Tool latency (p50, p95, p99)
- Error rates by tool
- Concurrent user sessions
- Database query latency

### Debug Endpoint (Development Only)
```bash
GET /debug/threads
# Returns: {thread_id: {items: [...], count: N}, ...}
```

---

## 🚢 Deployment

### Staging
```bash
# Deploy to staging environment
docker build -t chatbot:latest .
docker push chatbot:latest

# Deploy to staging cluster
kubectl apply -f k8s/staging/
```

### Production
```bash
# Tag and push production image
docker tag chatbot:latest chatbot:1.0.0
docker push chatbot:1.0.0

# Deploy to production with rollback plan
kubectl apply -f k8s/production/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "add_tasks_table"

# Verify on staging
alembic upgrade head

# Deploy to production
alembic upgrade head
```

---

## 🐛 Troubleshooting

### "Message IDs colliding" (LiteLLM with non-OpenAI providers)
**Fix**: Implement ID mapping in ChatKit Server `respond()` method (see `chatkit-expert.md`)

### "Database connection timeout"
**Fix**: Check Neon connection string in `.env`; verify firewall rules

### "Blank chat screen"
**Fix**: Ensure ChatKit CDN script in `index.html`; check domain allowlist

### "Agent not remembering context"
**Fix**: Verify `ThreadItemConverter` is loading full conversation history

---

## 📖 Architecture Decision Records (ADRs)

Significant architectural decisions documented in `/history/adr/`:
- MCP vs direct API for tool interface
- Stateless vs stateful backend
- Conversation history storage strategy
- ChatKit deployment approach

---

## 🤝 Contributing

1. Check constitution principles (`.specify/memory/constitution.md`)
2. Create feature branch: `git checkout -b <number>-<short-name>`
3. Follow TDD: write tests before implementation
4. Submit PR with spec/plan/tasks reference
5. Verify all tests pass and spec requirements met

---

## 📞 Support

- **Issues**: Check GitHub Issues / GitHub Discussions
- **Architecture**: See `.specify/memory/constitution.md` and `specs/1-chatbot-ai/`
- **Debugging**: Use `/debug/threads` endpoint for conversation state inspection

---

## 📄 License

[Add license type]

---

**Status**: 🟢 Spec Complete | 🟡 Planning Phase | ⚪ Implementation Pending

Last Updated: 2025-01-20
