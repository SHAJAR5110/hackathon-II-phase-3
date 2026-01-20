# Implementation Tasks: AI-Powered Todo Chatbot with MCP Integration

**Feature**: `1-chatbot-ai` — AI-Powered Todo Chatbot with MCP Integration  
**Created**: 2025-01-20  
**Status**: Ready for Implementation  
**Spec Reference**: `specs/1-chatbot-ai/spec.md`  
**Sample Reference**: ChatKit-Gemini-Bot for architectural patterns

---

## Overview

This tasks.md breaks down the chatbot feature into 48 independently testable, sequenced implementation tasks across 8 phases:

- **Phase 1**: Backend Setup & Infrastructure (5 tasks)
- **Phase 2**: Database & Core Models (5 tasks)
- **Phase 3**: Authentication & Middleware (4 tasks)
- **Phase 4**: MCP Server & Tools (8 tasks)
- **Phase 5**: OpenAI Agent & ThreadItemConverter (6 tasks)
- **Phase 6**: Chat Endpoint & User Stories (16 tasks)
- **Phase 7**: Frontend ChatKit Integration (8 tasks)
- **Phase 8**: Integration Tests & Polish (4 tasks)

**Total Tasks**: 48  
**MVP Scope**: Phase 1-6  
**Full Feature**: All 8 phases  
**Estimated Duration**: 2-3 weeks (full), 1 week (MVP)

---

## Phase 1: Backend Setup & Infrastructure

### Goal
Initialize FastAPI backend, configure dependencies, environment variables, and logging.

### Independent Test Criteria
- FastAPI server starts on `http://localhost:8000` without errors
- All required dependencies installed
- Environment variables loaded from `.env`
- Structured logging outputs JSON format

### Tasks

- [x] T001 Create backend directory structure in `backend/src/` with subdirectories: `models/`, `repositories/`, `routes/`, `middleware/`, `mcp_server/`, `agents/`, `services/`, `tests/`

- [x] T002 [P] Create FastAPI application in `backend/src/main.py`:
  - Initialize FastAPI app with title "AI Todo Chatbot"
  - Configure CORS for frontend domain
  - Add middleware for logging and error handling
  - Include health check endpoint `GET /health`

- [x] T003 [P] Create requirements.txt in `backend/` with dependencies:
  - fastapi==0.115.6
  - uvicorn[standard]==0.32.1
  - openai-chatkit<=1.4.0
  - openai-agents[litellm]>=0.6.2
  - sqlmodel==0.0.14
  - python-dotenv==1.0.1
  - psycopg2-binary==2.9.9
  - alembic==1.13.1

- [x] T004 [P] Create environment configuration in `backend/.env.example`:
  - NEON_DATABASE_URL=postgresql://user:password@host/db
  - OPENAI_API_KEY=sk-...
  - BETTER_AUTH_SECRET=your-secret-key
  - GEMINI_API_KEY=your-gemini-key (for LiteLLM multi-provider)
  - MCP_HOST=localhost
  - MCP_PORT=8001
  - LOG_LEVEL=INFO

- [x] T005 [P] Create logging configuration in `backend/src/logging_config.py`:
  - Configure structlog for JSON logging
  - Add context processors: user_id, conversation_id, tool_name
  - Set log level from environment
  - Include request ID generation middleware

**Phase 1 Gate**: Run `uvicorn backend.src.main:app --reload` — server starts on port 8000

---

## Phase 2: Database & Core Models

### Goal
Define database schema, create SQLModel ORM models, set up Neon PostgreSQL connection and migrations.

### Independent Test Criteria
- All models create/update/read without errors
- Database migrations run successfully on Neon
- Connection pooling configured with overflow protection
- Repositories execute CRUD operations

### Tasks

- [x] T006 Create SQLModel models in `backend/src/models/__init__.py`:
  - **User**: user_id (str, PK), created_at, updated_at
  - **Task**: id (int, PK), user_id (FK), title (str, max 1000), description (str, max 1000), completed (bool), created_at, updated_at
  - **Conversation**: id (int, PK), user_id (FK), created_at, updated_at
  - **Message**: id (int, PK), user_id (FK), conversation_id (FK), role (enum: user/assistant), content (text), created_at

- [x] T007 [P] Create SQLAlchemy engine & session in `backend/src/db.py`:
  - Parse NEON_DATABASE_URL from environment
  - Configure engine with echo=False, pool_size=20, max_overflow=0
  - Create Session factory with sessionmaker
  - Include circuit breaker for connection failures

- [x] T008 [P] Create Alembic migration in `backend/migrations/versions/001_initial_schema.py`:
  - CREATE TABLE users (user_id VARCHAR PRIMARY KEY)
  - CREATE TABLE tasks (id SERIAL, user_id FK, title VARCHAR, description VARCHAR, completed BOOLEAN, timestamps)
  - CREATE TABLE conversations (id SERIAL, user_id FK, timestamps)
  - CREATE TABLE messages (id SERIAL, user_id FK, conversation_id FK, role VARCHAR, content TEXT, created_at)
  - Add indexes on user_id, conversation_id, created_at
  - Add UNIQUE constraints: (user_id, id) on tasks/conversations

- [x] T009 [P] Create repository layer in `backend/src/repositories/`:
  - **TaskRepository**: create(), read(), update(), delete(), list_by_user(status), list_by_conversation()
  - **ConversationRepository**: create(), read(), list_by_user()
  - **MessageRepository**: create(), list_by_conversation(limit, offset), count_by_conversation()
  - All methods accept session and user_id for permission checking

- [x] T010 [P] Create database utilities in `backend/src/db_utils.py`:
  - async_get_db_session() context manager
  - health_check() function testing database connection
  - get_db_pool_status() returning connection pool statistics

**Phase 2 Gate**: Run migrations, verify tables in Neon console, execute repository tests

---

## Phase 3: Authentication & Middleware

### Goal
Implement user authentication validation, authorization, and request/response middleware.

### Independent Test Criteria
- Requests without auth header return 401
- Valid auth headers pass through
- All endpoints reject unauthorized access
- Error responses have no stack traces
- Structured logs include user_id

### Tasks

- [x] T011 Create authentication middleware in `backend/src/middleware/auth.py`:
  - Extract user_id from Authorization header (Better Auth session token)
  - Validate user_id exists, non-empty, matches pattern
  - Attach user to request state as request.state.user_id
  - Return {"detail": "Unauthorized"} with 401 for missing/invalid

- [x] T012 [P] Create authorization dependency in `backend/src/middleware/auth.py`:
  - Create get_current_user() dependency for FastAPI
  - Return user_id from request.state
  - Use in all protected endpoints: `@app.get("/") def route(user_id: str = Depends(get_current_user))`

- [x] T013 [P] Create error handling middleware in `backend/src/middleware/errors.py`:
  - Catch all exceptions globally
  - Log with context: user_id, endpoint, method, exception type
  - Return structured error: {"error": "Internal error", "request_id": "..."}
  - Map database errors (IntegrityError, OperationalError) to user-friendly messages
  - Return 500 with no stack trace

- [x] T014 [P] Create request/response logging middleware in `backend/src/middleware/logging_middleware.py`:
  - Generate request_id for traceability
  - Log request: method, path, user_id, timestamp
  - Log response: status_code, latency_ms
  - Use structlog for JSON output

**Phase 3 Gate**: POST to /api/user/chat without auth → 401. With valid auth → succeeds.

---

## Phase 4: MCP Server & Tools

### Goal
Implement stateless MCP server with all five task operation tools (add_task, list_tasks, complete_task, delete_task, update_task).

### Independent Test Criteria
- All 5 tools callable via Python MCP client
- Tool responses match schema specification
- Database changes persists after tool execution
- Tool errors return structured error dict
- User isolation: Tools reject cross-user task access

### Tasks

- [x] T015 Create MCP server foundation in `backend/src/mcp_server/__init__.py`:
  - Import official MCP SDK: `from mcp.server import Server`
  - Initialize Server with name "todo-mcp-server", version "1.0.0"
  - Define tool registry dictionary
  - Create start_server() function

- [x] T016 [P] Implement `add_task` MCP tool in `backend/src/mcp_server/tools/add_task.py`:
  - Parameters: user_id (string, required), title (string, required, max 1000), description (string, optional, max 1000)
  - Returns: {"task_id": int, "status": "created", "title": str}
  - Call TaskRepository.create(user_id, title, description)
  - Example: {"user_id": "user123", "title": "Buy groceries", "description": "milk, eggs"} → {"task_id": 5, "status": "created", "title": "Buy groceries"}
  - Validation: title cannot be empty, length checks

- [x] T017 [P] Implement `list_tasks` MCP tool in `backend/src/mcp_server/tools/list_tasks.py`:
  - Parameters: user_id (string, required), status (string, optional: "all" | "pending" | "completed", default "all")
  - Returns: Array of {"id": int, "title": str, "description": str, "completed": bool, "created_at": str}
  - Call TaskRepository.list_by_user(user_id, status)
  - Filter by completion status in SQL (not in Python)
  - Sort by created_at DESC

- [x] T018 [P] Implement `complete_task` MCP tool in `backend/src/mcp_server/tools/complete_task.py`:
  - Parameters: user_id (string, required), task_id (integer, required)
  - Returns: {"task_id": int, "status": "completed", "title": str}
  - Call TaskRepository.read(user_id, task_id) → verify ownership
  - Call TaskRepository.update(task_id, completed=True)
  - Error if task not found: {"error": "task_not_found", "message": "Task {id} not found"}

- [x] T019 [P] Implement `delete_task` MCP tool in `backend/src/mcp_server/tools/delete_task.py`:
  - Parameters: user_id (string, required), task_id (integer, required)
  - Returns: {"task_id": int, "status": "deleted", "title": str}
  - Call TaskRepository.read(user_id, task_id) → verify ownership
  - Call TaskRepository.delete(task_id)
  - Return deleted task info before deletion

- [x] T020 [P] Implement `update_task` MCP tool in `backend/src/mcp_server/tools/update_task.py`:
  - Parameters: user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional)
  - Returns: {"task_id": int, "status": "updated", "title": str}
  - Require at least one of title/description to be provided
  - Call TaskRepository.read(user_id, task_id) → verify ownership
  - Call TaskRepository.update(task_id, title=title, description=description)

- [x] T021 Create MCP tool registry in `backend/src/mcp_server/registry.py`:
  - Register all 5 tools with MCP server
  - Define tool schemas with JSON Schema
  - Map tool names to callable functions
  - Include tool descriptions for agent context

- [x] T022 Create unit tests for MCP tools in `backend/tests/test_mcp_tools.py`:
  - Mock database repositories
  - Test each tool with valid inputs → verify correct output
  - Test each tool with invalid inputs → verify error response
  - Test authorization: task from user A, call with user B → error
  - Test schema compliance: responses match declared schema

**Phase 4 Gate**: Test each tool independently, verify database changes persist, user isolation confirmed

---

## Phase 5: OpenAI Agent & ThreadItemConverter

### Goal
Integrate OpenAI Agents SDK with conversation context, MCP tools, and ChatKit's ThreadItemConverter for history management.

### Independent Test Criteria
- Agent initializes without errors
- Agent calls correct MCP tools based on user message
- Full conversation history reconstructed correctly
- ID mapping prevents message collisions (LiteLLM fix)
- Agent errors handled gracefully

### Tasks

- [x] T023 Create agent configuration in `backend/src/agents/config.py`:
  - System prompt: "You are a helpful task management assistant. Help users manage their todo tasks using natural language. Available tools: add_task, list_tasks, complete_task, delete_task, update_task. Always confirm actions and provide friendly responses."
  - Load model from environment (default: "openai/gpt-4o", supports "gemini/gemini-2.0-flash" via LiteLLM)
  - Configure via LitellmModel from agents.extensions.models.litellm_model
  - Timeout: 30 seconds

- [x] T024 [P] Create message history converter in `backend/src/agents/converter.py`:
  - Import ThreadItemConverter from chatkit.agents
  - Convert Message ORM objects → ThreadItem format
  - Handle user messages: role="user", content
  - Handle assistant messages: role="assistant", content
  - Return list in chronological order (oldest first)
  - Handle large histories: pass last 30 messages if > 100 messages total

- [x] T025 [P] Create agent context builder in `backend/src/agents/context.py`:
  - Load conversation from database
  - Load all messages for conversation via MessageRepository
  - Build conversation_history array using ThreadItemConverter
  - Include current user_id in context for tool access
  - Return: {conversation_history: [], user_id: str, conversation_id: int}

- [x] T026 [P] Create ID mapping fix in `backend/src/agents/id_mapper.py` (LiteLLM collision prevention):
  - Track mapping: {provider_id → generated_id}
  - When agent returns message with provider ID
  - Generate new unique ID via store.generate_item_id("message", thread, context)
  - Update ThreadItemAddedEvent.item.id with new ID
  - Apply same mapping to ThreadItemUpdatedEvent, ThreadItemDoneEvent

- [x] T027 [P] Create agent runner in `backend/src/agents/runner.py`:
  - Initialize Agent from config
  - Accept: conversation_history (list), user_message (str), user_id (str), context (dict)
  - Prepare agent input: [history_items..., new_user_message]
  - Execute: runner = Runner(); result = await runner.run_agent(agent, agent_input)
  - Stream response events, apply ID mapping fix
  - Extract final response text and tool_calls
  - Return: {response: str, tool_calls: [{tool: str, params: dict}]}
  - Error handling: timeout → "I'm having trouble reaching my brain. Please try again."

- [x] T028 Create integration test for agent in `backend/src/tests/test_agent_integration.py`:
  - Create test conversation with 5 prior messages
  - Call agent with "Add a task to buy milk"
  - Verify agent calls add_task tool with correct parameters
  - Verify response includes confirmation message
  - Test with long history (100+ messages) → pagination works
  - Test error case: MCP tool fails → agent handles gracefully

**Phase 5 Gate**: Agent receives conversation history, calls tools correctly, no ID collisions

---

## Phase 6: Chat Endpoint & User Stories

### Goal
Implement POST `/api/{user_id}/chat` endpoint and complete all 6 user story flows (Add, List, Complete, Update, Delete, Context).

### Independent Test Criteria
- Chat endpoint accepts requests from authenticated users
- All user story flows work end-to-end
- Conversation history persists and is retrievable
- All MCP tools execute successfully from chat
- Agent confirmations are clear and actionable
- Each user story independently testable

### Tasks

#### Endpoint Foundation

- [x] T029 Create chat endpoint skeleton in `backend/src/routes/chat.py`:
  - Route: `POST /api/{user_id}/chat`
  - Auth: Require user_id in path matches authenticated user (via get_current_user dependency)
  - Request body: `{conversation_id?: int, message: string}`
  - Response body: `{conversation_id: int, response: string, tool_calls: [{tool: string, params: dict}]}`
  - Error responses: `{error: string, request_id: string}` (500, 400, 401)

- [x] T030 Implement conversation retrieval in `backend/src/routes/chat.py`:
  - If conversation_id provided in request:
    - Load Conversation from database via ConversationRepository
    - Verify conversation.user_id == authenticated user_id
    - Load all messages for conversation
  - If conversation_id not provided:
    - Create new Conversation(user_id=authenticated_user)
    - Initialize with empty message history
  - Return conversation_id to client

- [x] T031 Implement user message storage in `backend/src/routes/chat.py`:
  - Generate message_id via store.generate_item_id("message", thread, context)
  - Create Message object: {user_id, conversation_id, role="user", content=request.message, created_at=now}
  - Store to database via MessageRepository.create()
  - Commit transaction

- [x] T032 Implement agent execution in `backend/src/routes/chat.py`:
  - Call agent_context_builder with conversation_history
  - Call agent_runner with (history, user_message, user_id)
  - Handle timeout (30s) → return error response
  - Handle API unavailable → return error response
  - Extract response text and tool_calls from agent result

- [x] T033 Implement assistant response storage in `backend/src/routes/chat.py`:
  - Generate message_id via store.generate_item_id()
  - Create Message: {user_id, conversation_id, role="assistant", content=agent_response, created_at=now}
  - Store to database via MessageRepository.create()
  - Extract tool_calls array from agent execution
  - Commit transaction

- [x] T034 Implement response formatting in `backend/src/routes/chat.py`:
  - Format JSON response:
    ```json
    {
      "conversation_id": 1,
      "response": "I've added 'Buy groceries' to your task list!",
      "tool_calls": [
        {"tool": "add_task", "params": {"user_id": "user123", "title": "Buy groceries"}}
      ]
    }
    ```
  - Validate schema before returning
  - Set appropriate HTTP status code (200)

#### User Story 1: Add Task via Natural Language (P1)

- [x] T035 [US1] Implement add_task flow in chat endpoint:
  - User message: "Add a task to buy groceries"
  - Agent calls add_task(user_id, title="Buy groceries", description=null)
  - MCP tool creates task in database
  - Agent responds: "I've added 'Buy groceries' to your task list!"
  - Return response + tool_calls to client
  - Verify: Task appears in database, conversation history updated

- [x] T036 [US1] Handle task creation with description:
  - User message: "Add a task to buy groceries with milk, eggs, and bread"
  - Agent extracts title and description
  - Call add_task with both parameters
  - Response confirms both title and description stored

- [x] T037 [US1] Handle ambiguous task creation:
  - User message: "Add something"
  - Agent recognizes incomplete request
  - Agent asks clarification: "What would you like to add?"
  - No task created yet
  - Next message: user provides details, task created

#### User Story 2: List and Filter Tasks (P1)

- [x] T038 [US2] Implement list_tasks all flow:
  - User message: "Show me all my tasks"
  - Agent calls list_tasks(user_id, status="all")
  - MCP tool returns array of all tasks
  - Agent formats readable list: "You have 3 tasks: 1) Buy groceries, 2) Call mom, 3) Finish project"
  - Response returned to client

- [x] T039 [US2] Implement list_tasks pending filter:
  - User message: "What's pending?"
  - Agent calls list_tasks(user_id, status="pending")
  - Only incomplete tasks returned
  - Agent lists pending items only

- [x] T040 [US2] Handle empty task list:
  - User message: "Show me all my tasks"
  - list_tasks returns empty array
  - Agent responds: "You have no tasks yet. Want to add one?"
  - No error thrown, friendly message given

#### User Story 3: Complete Task via Conversation (P1)

- [x] T041 [US3] Implement complete_task by ID:
  - User message: "Mark task 1 as complete"
  - Agent calls complete_task(user_id, task_id=1)
  - Task updated: completed=true
  - Agent confirms: "I've marked 'Buy groceries' as complete!"
  - Response includes tool_calls

- [x] T042 [US3] Implement complete_task by ambiguous reference:
  - User message: "I finished the meeting"
  - Agent calls list_tasks(user_id) to get all tasks
  - Finds multiple pending tasks including "Meeting" item
  - Agent asks: "I found 'Meeting' task. Is that the one you finished?"
  - Wait for confirmation, then call complete_task

- [x] T043 [US3] Handle task not found:
  - User message: "Mark task 999 as complete"
  - complete_task returns error (task_not_found)
  - Agent handles gracefully: "I couldn't find task 999. Here are your pending tasks: ..."
  - Lists valid pending tasks for user reference

#### User Story 4: Update Task Description (P2)

- [x] T044 [US4] Implement update_task title:
  - User message: "Change task 1 to 'Call mom tonight'"
  - Agent calls update_task(user_id, task_id=1, title="Call mom tonight")
  - Task.title updated in database
  - Agent confirms: "I've updated task 1 to 'Call mom tonight'"

- [x] T045 [US4] Implement update_task description:
  - User message: "Add details to task 1: remember to buy organic milk"
  - Agent calls update_task(user_id, task_id=1, description="remember to buy organic milk")
  - Task.description updated
  - Agent confirms update

#### User Story 5: Delete Task (P2)

- [x] T046 [US5] Implement delete_task by ID:
  - User message: "Delete task 4"
  - Agent calls delete_task(user_id, task_id=4)
  - Task removed from database
  - Agent confirms: "I've deleted 'Old meeting' task"

- [x] T047 [US5] Implement delete_task with ambiguity:
  - User message: "Delete the task"
  - Agent calls list_tasks to get pending tasks
  - Multiple tasks exist
  - Agent asks: "Which task would you like to delete? [list options]"
  - User confirms, agent deletes

#### User Story 6: Maintain Conversation Context (P1)

- [x] T048 [US6] Implement conversation history across turns:
  - Message 1: "Add a task to buy groceries"
  - Message 2: "Show me all my tasks" (agent has context from msg 1)
  - Message 3: "Mark task 1 as complete" (agent knows task 1 = "buy groceries")
  - Agent references prior messages correctly
  - Conversation ID persists across all 3 messages

- [x] T049 [US6] Implement conversation resume after page refresh:
  - User sends 5 messages in conversation 1
  - Frontend refreshes page
  - User requests conversation_id=1 in next request
  - Backend loads all 5 prior messages from database
  - Agent has full context: "I remember we added 'Buy groceries' earlier..."
  - No data loss, seamless continuation

- [x] T050 [US6] Implement server restart resilience:
  - Conversation with 10 messages exists in database
  - Server restarts (process dies)
  - Server starts again
  - User requests conversation_id=1
  - Backend queries database, loads all 10 messages
  - User can continue conversation from where they left off
  - Zero data loss

**Phase 6 Gate**: All 6 user stories end-to-end tested, 100+ messages persisted, user isolation verified

---

## Phase 7: Frontend ChatKit Integration

### Goal
Integrate OpenAI ChatKit React component on dashboard for chat UI, connect to backend endpoint.

### Independent Test Criteria
- ChatKit renders on dashboard without console errors
- User can type and send messages
- Messages appear in chat history
- Backend responses appear as assistant messages
- Conversation persists across page refreshes
- Error handling displays friendly messages

### Tasks

- [ ] T051 [P] Create ChatKit wrapper component in `frontend/src/components/ChatBot.tsx`:
  - Import: `import { useChatKit } from "@openai/chatkit-react"`
  - Import: `import ChatKit from "@openai/chatkit-react"`
  - Configure useChatKit hook with backend URL
  - Pass API endpoint, domain key, conversation ID
  - Export ChatBot component for use in pages

- [ ] T052 [P] Create chat popup layout component in `frontend/src/components/ChatBotPopup.tsx`:
  - State: isOpen (bool)
  - Button: floating, bottom-right corner (position: fixed, right: 2rem, bottom: 2rem)
  - Button style: 60x60px circle, blue gradient, chat icon SVG
  - Popup: 420x600px, position: fixed, bottom: 2rem, right: 2rem, z-index: 1000
  - Content: ChatBot component inside popup
  - Close button: X button top-right of popup
  - Backdrop: semi-transparent overlay (z-index: 999) when open

- [ ] T053 [P] Integrate ChatBotPopup in dashboard page `frontend/src/app/dashboard/page.tsx`:
  - Import ChatBotPopup component
  - Render `<ChatBotPopup />` at bottom of dashboard
  - Ensure dashboard content not blocked by popup
  - Pass user_id from auth context to ChatBot via prop

- [ ] T054 [P] Add ChatKit CDN script in `frontend/src/app/layout.tsx`:
  - Add in `<head>`: `<script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>`
  - Ensure script loads before ChatKit components mount
  - Add error handler: if script fails to load, log warning

- [ ] T055 [P] Create environment variables in `frontend/.env.local`:
  - NEXT_PUBLIC_API_URL=http://localhost:8000
  - NEXT_PUBLIC_OPENAI_DOMAIN_KEY=localhost (development)
  - NEXT_PUBLIC_CONVERSATION_ID=null (null = create new)

- [ ] T056 [P] Implement ChatKit configuration in `frontend/src/config/chatkit.config.ts`:
  - Export config object:
    ```js
    {
      api: {
        url: process.env.NEXT_PUBLIC_API_URL,
        domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY
      },
      startScreen: {
        prompts: [
          { label: "Add a task", prompt: "Add a task to..." },
          { label: "Show tasks", prompt: "Show me all my tasks" }
        ]
      }
    }
    ```
  - Store conversation_id in localStorage
  - Load conversation_id on component mount

- [ ] T057 [P] Create error boundary for ChatKit in `frontend/src/components/ChatBotErrorBoundary.tsx`:
  - Catch ChatKit render errors
  - Display fallback UI: "Chat is temporarily unavailable"
  - Log error to console for debugging
  - Include retry button

- [ ] T058 Create ChatKit integration test in `frontend/__tests__/ChatBot.integration.test.tsx`:
  - Mock ChatKit component
  - Verify popup renders on dashboard
  - Simulate message send
  - Verify response handling
  - Test error states

**Phase 7 Gate**: Open dashboard, click chat button, send message, receive response from backend

---

## Phase 8: Integration Tests & Polish

### Goal
Comprehensive testing, performance validation, security checks, and production readiness.

### Independent Test Criteria
- End-to-end flows pass with real database
- Concurrent requests handled correctly
- Performance meets SLOs (p95 latency)
- No security vulnerabilities
- Error handling graceful throughout
- All code committed and documented

### Tasks

- [ ] T059 Create end-to-end integration test `backend/tests/test_e2e_full_flow.py`:
  - Scenario 1: Add task → List tasks → Complete task (3 messages)
  - Scenario 2: Multiple tasks, filter by pending → filter by completed
  - Scenario 3: Long conversation (10+ messages) → history persists
  - Scenario 4: Concurrent users (User A and User B) → isolated task lists
  - Verify database state after each step

- [ ] T060 [P] Create security test suite `backend/tests/test_security.py`:
  - User isolation: User A cannot see/modify User B's tasks (test with direct API calls)
  - Auth validation: Request without user_id returns 401
  - SQL injection prevention: Attempt injection in task title → parameterized queries block
  - Schema validation: Invalid JSON in request → 400 error
  - Rate limiting (future): Track requests per user_id

- [ ] T061 [P] Create performance test `backend/tests/test_performance.py`:
  - Latency test: Add task (call add_task tool directly) → measure ≤ 500ms
  - Latency test: Chat endpoint POST (full flow) → measure p95 ≤ 3s
  - Latency test: List tasks → measure p95 ≤ 2s
  - Concurrent load: 10 simultaneous requests → verify no errors
  - Large conversation: 100+ messages → verify pagination works

- [ ] T062 [P] Create deployment readiness checklist in `backend/DEPLOYMENT.md`:
  - Environment variables validated
  - Database migrations tested on Neon
  - ChatKit domain allowlist configured
  - Error logging configured
  - Health check endpoint working
  - Performance benchmarks met
  - Security audit passed
  - README updated with setup instructions

**Phase 8 Gate**: All tests passing, performance targets met, security validated, production ready

---

## Dependency Graph & Execution Order

```
Phase 1: Setup
    ↓
Phase 2: Database & Models
    ↓
Phase 3: Auth & Middleware
    ↓
Phase 4: MCP Tools ← CRITICAL BLOCKER
    ↓
Phase 5: Agent & History ← CRITICAL BLOCKER
    ↓
Phase 6: Chat Endpoint & User Stories (sequential per story)
    ├─→ US1 [T035-T037]
    ├─→ US2 [T038-T040]
    ├─→ US3 [T041-T043]
    ├─→ US4 [T044-T045]
    ├─→ US5 [T046-T047]
    └─→ US6 [T048-T050]
    ↓
Phase 7: Frontend (CAN START PARALLEL WITH PHASE 6 AFTER T034)
    ├─→ ChatKit Setup [T051-T057]
    └─→ Integration Tests [T058]
    ↓
Phase 8: Full Testing & Polish
    └─→ E2E & Security & Performance Tests [T059-T062]
```

---

## Parallelizable Tasks

**Backend Services** (Phase 4-5): Different developers can work in parallel
- T016-T020: Each MCP tool implementation (5 parallel)
- T023-T027: Agent setup tasks (can overlap)

**Frontend Components** (Phase 7): Can start after T034
- T051-T057: ChatKit components (mostly parallel)

**Testing** (Phase 8): Independent test suites
- T059-T062: Different test types (concurrent)

---

## MVP Scope & Prioritization

### MVP = Phase 1-6 Complete

**Includes**:
- ✅ All project setup & infrastructure
- ✅ Full database schema & models
- ✅ Auth & middleware complete
- ✅ All 5 MCP tools functional
- ✅ Agent integration with conversation history
- ✅ Chat endpoint fully working
- ✅ User Story 1: Add Task (P1) — COMPLETE
- ✅ User Story 2: List Tasks (P1) — COMPLETE
- ✅ User Story 3: Complete Task (P1) — COMPLETE
- ✅ User Story 6: Context (P1) — COMPLETE
- ✅ ChatKit frontend integrated
- ⏸ User Story 4: Update Task (P2) — DEFERRED
- ⏸ User Story 5: Delete Task (P2) — DEFERRED
- ⏸ Full test suite (Phase 8) — DEFERRED

**MVP Estimated Time**: 1-1.5 weeks

### Full Feature = Phase 1-8 Complete

**Additional**:
- ✅ User Story 4: Update Task (P2)
- ✅ User Story 5: Delete Task (P2)
- ✅ Comprehensive tests (unit, integration, security, performance)
- ✅ Production deployment guide

**Full Feature Estimated Time**: 2-2.5 weeks

---

## Quality Gates & Acceptance Criteria

### Per Phase Gate

| Phase | Gate Criteria | Verified By |
|-------|---------------|-------------|
| **1** | Server starts, all dependencies installed | `uvicorn backend.src.main:app` runs |
| **2** | Migrations pass, tables in Neon, repo tests pass | `alembic upgrade head`, Neon console check |
| **3** | Auth blocks unauth requests, logs structured | Manual testing + T014 |
| **4** | All 5 tools callable, database changes persist | T022 unit tests pass |
| **5** | Agent calls tools, history reconstructed | T028 integration test passes |
| **6** | All user stories end-to-end working | T035-T050 e2e tests pass |
| **7** | ChatKit renders, messages sent/received | T058 integration test passes |
| **8** | All tests pass, perf targets met, secure | T059-T062 all passing |

---

## Notes for Implementation

1. **TDD Recommended**: Write test assertions first (Given-When-Then), then implementation
2. **Commit Frequently**: After each task, commit with message referencing task ID: "feat: T001 - Create project structure"
3. **Database Safety**: Always test migrations on Neon staging first
4. **Error Messages**: User-friendly; never expose stack traces to frontend
5. **Logging**: Every operation logged with user_id, conversation_id, tool_name
6. **Documentation**: Update README after each phase
7. **Code Review**: Reference spec.md and this tasks.md in PRs

---

**Status**: ✅ Tasks Generated | Ready for Implementation

**Start with**: T001 (Project Setup)  
**Next Review**: After Phase 1 completion (T001-T005)

