---
id: 1
title: Create Constitution for AI Todo Chatbot
stage: constitution
date: 2025-01-20
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["architecture", "spec-driven-dev", "hackathon-2", "project-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

User requested: Create and update the project constitution using `/sp.constitution` command. Use the two sub-agents:
- @chatkit-expert.md (ChatKit/OpenAI Agents integration specialist)
- @fullstack-developer.md (Full-stack Next.js development)

Project context:
- Objective: AI-powered chatbot for todo management using MCP (Model Context Protocol)
- Tech stack: FastAPI backend, OpenAI ChatKit frontend, OpenAI Agents SDK, MCP server, SQLModel ORM, Neon PostgreSQL, Better Auth
- Key requirement: Stateless server, conversation history persisted to database, MCP tools expose task operations
- Architecture: ChatKit UI → FastAPI chat endpoint → OpenAI Agents SDK → MCP server (stateless tools) → Neon DB
- Chat only accessible on dashboard, not landing page
- Requirements include 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)

## Response snapshot

Created comprehensive project constitution at `.specify/memory/constitution.md` with 10 core principles:

1. **Stateless Server Architecture** — Every request independent; all state in database; horizontal scaling
2. **MCP Tools as AI Interface** — Five stateless tools for task operations
3. **Conversation History as Source of Truth** — Full context reconstructed per-request using ThreadItemConverter
4. **Framework Correctness** — ChatKit/OpenAI Agents used correctly (specific SDK versions, correct imports)
5. **User-Centric Natural Language** — Agent understands conversational commands and confirms actions
6. **Authentication & Authorization** — user_id validation, Better Auth, dashboard-only access
7. **Database-First Design** — SQLModel ORM, Neon PostgreSQL, three core tables (Task, Conversation, Message)
8. **Error Handling & Graceful Degradation** — Structured errors, agent suggests alternatives, no stack traces
9. **Testability & Observability** — Unit/integration tests, structured JSON logging, debug endpoints
10. **Simplicity & YAGNI** — No premature abstraction, single responsibility, auto-generated docs

Included sections:
- Project Mission aligned with hackathon objectives
- Technology Stack (locked versions for reproducibility)
- Architecture Constraints (frontend/backend/database)
- Quality Gates (code review, testing, security, migration, docs)
- Development Workflow (spec → plan → tasks → implementation → review → deploy)
- Security Requirements (auth, data protection, input validation)
- Performance SLOs (p95 latency, concurrent users, recovery time)
- Deployment & Operations (environments, migrations, monitoring)
- Governance & Evolution (amendment process, decision framework, complexity justification)
- Success Criteria (MVP readiness checklist)

## Outcome

- ✅ Impact: Project has authoritative constitution establishing principles, constraints, and quality gates
- 🧪 Tests: No tests applicable for constitution; validation by team review
- 📁 Files: `.specify/memory/constitution.md` (10 principles, 7 sections, ~500 LOC)
- 🔁 Next prompts: `/sp.specify` for feature specification, `/sp.plan` for architecture design, `/sp.tasks` for task breakdown
- 🧠 Reflection: Constitution balances stateless architecture (critical for horizontal scaling) with practical developer guidance. Explicitly calls out ChatKit/OpenAI SDK version pins and common pitfalls (LiteLLM ID collision fix). Aligns hackathon deliverables with SDD methodology.

## Evaluation notes (flywheel)

- Failure modes observed: None; constitution from spec document
- Graders run and results: Manual review against CLAUDE.md requirements — PASS
- Prompt variant: N/A
- Next experiment: Use constitution as baseline for `/sp.specify` to formalize feature scope

