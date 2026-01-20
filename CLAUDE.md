# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

### Major Features 
**Already** 
- **Frontend**: already implemented todo application. I want to enhance it with more features like rag based bot inside the frontend and dashboard only not on the landing page bot only accessable to the dashboard on the frontend.
- **Backend**: Already implemented REST API for todo operations. Add the rag based bot inside the backend and dashboard only not on the landing page bot only accessable to the dashboard on the backend.
- **RAG**: Implement a RAG based bot inside the frontend and backend. The RAG bot should be accessible only to the dashboard on the frontend and backend.
**NEW Features and stack shows blow**
Objective: Create an AI-powered chatbot interface for managing todos through natural 
language using MCP (Model Context Protocol) server architecture and using Claude Code 
and Spec-Kit Plus. 
Requirements 
1. Implement conversational interface for all Basic Level features 
2. Use OpenAI Agents SDK for AI logic 
3. Build MCP server with Official MCP SDK that exposes task operations as tools 
4. Stateless chat endpoint that persists conversation state to database 
5. AI agents use MCP tools to manage tasks. The MCP tools will also be stateless and 
will store state in the database.  
Technology Stack 
Component Technology 
Frontend OpenAI ChatKit 
Backend Python FastAPI 
AI Framework OpenAI Agents SDK 
MCP Server Official MCP SDK 
ORM SQLModel 
Database Neon Serverless PostgreSQL 
Authentication Better Auth 
Architecture 
┌─────────────────┐     ┌──────────────────────────────────────────────┐     
┌─────────────────┐ 
│                 │     │              FastAPI Server                   │     │               
│ 
│                 │     │  ┌────────────────────────────────────────┐  │     │                
│ 
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │    
Neon DB      │ 
│  (Frontend)     │     │  │  POST /api/chat                        │  │     │  
(PostgreSQL)   │ 
│                 │     │  └───────────────┬────────────────────────┘  │     │                
│ 
│                 │     │                  │                           │     │  - tasks        │ 
│                 │     │                  ▼                           │     │  - conversations│ 
│                 │     │  ┌────────────────────────────────────────┐  │     │  - messages     │ 
│                 │◀────│  │      OpenAI Agents SDK                 │  │     │                
│ 
│                 │     │  │      (Agent + Runner)                  │  │     │                
│ 
│                 │     │  └───────────────┬────────────────────────┘  │     │                
│ 
│                 │     │                  │                           │     │                
│ 
Page 17 of 38 
Hackathon II: Spec-Driven Development 
│                 │     │                  ▼                           │     │                
│ 
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                
│ 
│                 │     │  │         MCP Server                 │  │     │                 
│ 
│                 │     │  │  (MCP Tools for Task Operations)       │  │◀────│                
│ 
│                 │     │  └────────────────────────────────────────┘  │     │                
│ 
└─────────────────┘     └──────────────────────────────────────────────┘     
└─────────────────┘ 
Database Models 
Model Fields Description 
Task user_id, id, title, description, 
completed, created_at, updated_at 
Todo items 
Conversation user_id, id, created_at, updated_at Chat session 
Message user_id, id, conversation_id, role 
(user/assistant), content, created_at 
Chat history 
Chat API Endpoint 
Method Endpoint Description 
POST /api/{user_id}/chat Send message & get AI response 
Request 
Field Type Required Description 
conversation_id integer No Existing conversation ID (creates new if 
not provided) 
message string Yes User's natural language message 
Response 
Field Type Description 
conversation_id integer The conversation ID 
response string AI assistant's response 
tool_calls array List of MCP tools invoked 
MCP Tools Specification 
The MCP server must expose the following tools for the AI agent: 
Tool: add_task 
Purpose Create a new task 
Parameters user_id (string, required), title (string, required), description (string, 
optional) 
Returns task_id, status, title 
Example Input {“user_id”: “ziakhan”, "title": "Buy groceries", "description": "Milk, eggs, 
bread"} 
Page 18 of 38 
Hackathon II: Spec-Driven Development 
Example Output {"task_id": 5, "status": "created", "title": "Buy groceries"} 
Tool: list_tasks 
Purpose Retrieve tasks from the list 
Parameters status (string, optional: "all", "pending", "completed") 
Returns Array of task objects 
Example Input {user_id (string, required), "status": "pending"} 
Example Output [{"id": 1, "title": "Buy groceries", "completed": false}, ...] 
Tool: complete_task 
Purpose Mark a task as complete 
Parameters user_id (string, required), task_id (integer, required) 
Returns task_id, status, title 
Example Input {“user_id”: “ziakhan”, "task_id": 3} 
Example Output {"task_id": 3, "status": "completed", "title": "Call mom"} 
Tool: delete_task 
Purpose Remove a task from the list 
Parameters user_id (string, required), task_id (integer, required) 
Returns task_id, status, title 
Example Input {“user_id”: “ziakhan”, "task_id": 2} 
Example Output {"task_id": 2, "status": "deleted", "title": "Old task"} 
Tool: update_task 
Purpose Modify task title or description 
Parameters user_id (string, required), task_id (integer, required), title (string, 
optional), description (string, optional) 
Returns task_id, status, title 
Example Input {“user_id”: “ziakhan”, "task_id": 1, "title": "Buy groceries and fruits"} 
Example Output {"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"} 
Agent Behavior Specification 
Behavior Description 
Task Creation When user mentions adding/creating/remembering something, use 
add_task 
Task Listing When user asks to see/show/list tasks, use list_tasks with 
appropriate filter 
Task Completion When user says done/complete/finished, use complete_task 
Task Deletion When user says delete/remove/cancel, use delete_task 
Task Update When user says change/update/rename, use update_task 
Confirmation Always confirm actions with friendly response 
Error Handling Gracefully handle task not found and other errors 
 
Page 19 of 38 
Hackathon II: Spec-Driven Development 
Conversation Flow (Stateless Request Cycle) 
1. Receive user message 
2. Fetch conversation history from database 
3. Build message array for agent (history + new message) 
4. Store user message in database 
5. Run agent with MCP tools 
6. Agent invokes appropriate MCP tool(s) 
7. Store assistant response in database 
8. Return response to client 
9. Server holds NO state (ready for next request) 
Natural Language Commands 
The chatbot should understand and respond to: 
User Says 
Agent Should 
"Add a task to buy groceries" 
"Show me all my tasks" 
"What's pending?" 
Call add_task with title "Buy groceries" 
Call list_tasks with status "all" 
Call list_tasks with status "pending" 
"Mark task 3 as complete" 
"Delete the meeting task" 
"Change task 1 to 'Call mom tonight'" 
"I need to remember to pay bills" 
"What have I completed?" 
Deliverables 
1. GitHub repository with: 
● /frontend – ChatKit-based UI 
Call complete_task with task_id 3 
Call list_tasks first, then delete_task 
Call update_task with new title 
Call add_task with title "Pay bills" 
Call list_tasks with status "completed" 
● /backend – FastAPI + Agents SDK + MCP 
● /specs – Specification files for agent and MCP tools 
● Database migration scripts 
● README with setup instructions 
2. Working chatbot that can: 
● Manage tasks through natural language via MCP tools 
● Maintain conversation context via database (stateless server) 
● Provide helpful responses with action confirmations 
● Handle errors gracefully 
● Resume conversations after server restart 
OpenAI ChatKit Setup & Deployment 
Domain Allowlist Configuration (Required for Hosted ChatKit) 
Before deploying your chatbot frontend, you must configure OpenAI's domain allowlist for 
security: 
1. Deploy your frontend first to get a production URL: 
Page 20 of 38 
Vercel: `https://your-app.vercel.app` 
Hackathon II: Spec-Driven Development -  -  -  
GitHub Pages: `https://username.github.io/repo-name` 
Custom domain: `https://yourdomain.com` 
2. Add your domain to OpenAI's allowlist: - - - - 
Navigate to: 
https://platform.openai.com/settings/organization/security/domain-allowlist 
Click "Add domain" 
Enter your frontend URL (without trailing slash) 
Save changes 
3. Get your ChatKit domain key: - - 
After adding the domain, OpenAI will provide a domain key 
Pass this key to your ChatKit configuration 
Environment Variables 
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here 
Note: The hosted ChatKit option only works after adding the correct domains under Security 
→ Domain Allowlist. Local development (`localhost`) typically works without this 
configuration. 
Key Architecture Benefits 
Aspect 
Benefit 
MCP Tools 
Single Endpoint 
Standardized interface for AI to interact with your app 
Simpler API — AI handles routing to tools 
Stateless Server 
Tool Composition 
Scalable, resilient, horizontally scalable 
Agent can chain multiple tools in one turn 
Key Stateless Architecture Benefits 
● Scalability: Any server instance can handle any request 
● Resilience: Server restarts don't lose conversation state 
● Horizontal scaling: Load balancer can route to any backend 
● Testability: Each request is independent and reproducible 

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.
