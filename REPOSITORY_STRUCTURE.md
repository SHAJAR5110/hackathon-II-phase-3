# Repository Structure: hackathon-II-phase-3

```
hackathon-II-phase-3/
├── .claude/                           # Claude Code integration
│   ├── agents/
│   │   ├── chatkit-expert.md         # ChatKit integration specialist
│   │   └── fullstack-developer.md    # Full-stack development guidance
│   ├── commands/                      # Spec-Kit Plus CLI commands
│   │   ├── sp.*.md                   # Command definitions
│   │   └── ...
│   └── skills/                        # Domain-specific skills
│       ├── backend-expert/
│       ├── fastapi-expert/
│       ├── fullstack-developer/
│       ├── chatkit-backend/
│       ├── chatkit-frontend/
│       └── ...
│
├── .specify/                          # Spec-Kit Plus infrastructure
│   ├── memory/
│   │   └── constitution.md            # PROJECT CONSTITUTION (10 principles)
│   ├── templates/                     # SDD templates
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── phr-template.prompt.md
│   │   └── ...
│   └── scripts/bash/                  # Automation scripts
│       ├── create-new-feature.sh
│       ├── create-phr.sh
│       ├── create-adr.sh
│       └── ...
│
├── .gitignore                         # Git ignore patterns
├── CLAUDE.md                          # Original hackathon specification
├── AGENTS.md                          # Agent descriptions
├── README.md                          # 📌 START HERE - Quick start guide
├── REPOSITORY_STRUCTURE.md            # This file
│
├── specs/                             # Feature specifications (Spec-Driven Development)
│   └── 1-chatbot-ai/                  # Feature 1: AI Todo Chatbot
│       ├── spec.md                    # ✅ COMPLETE - 6 user stories, 18 FRs, 10 success criteria
│       └── checklists/
│           └── requirements.md        # ✅ Quality checklist (24/24 items pass)
│
├── history/                           # Development history & decisions
│   ├── prompts/                       # Prompt History Records (PHRs)
│   │   ├── constitution/
│   │   │   └── 1-create-constitution.constitution.prompt.md
│   │   └── 1-chatbot-ai/
│   │       └── 1-create-specification.spec.prompt.md
│   └── adr/                           # Architecture Decision Records (TBD)
│
├── frontend/                          # React + Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── auth/                  # Authentication pages
│   │   │   ├── dashboard/             # Dashboard with task management
│   │   │   └── page.tsx               # Landing page
│   │   ├── components/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── Header.tsx
│   │   │   └── ...
│   │   ├── middleware.ts
│   │   └── styles/
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── huggingface-backend/               # FastAPI backend (existing implementation)
│   ├── main.py                        # FastAPI application
│   ├── models.py                      # Database models
│   ├── routes/
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── middleware/
│   │   └── auth.py
│   ├── services/
│   │   └── auth_service.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── .env.example                       # Environment variables template
```

---

## 📌 Key Files & Their Purpose

| File | Purpose | Status |
|------|---------|--------|
| **README.md** | Quick start, tech stack, MCP tools | ✅ Complete |
| **.specify/memory/constitution.md** | 10 project principles, quality gates | ✅ Complete |
| **specs/1-chatbot-ai/spec.md** | Feature specification (6 stories, 18 FRs) | ✅ Complete |
| **specs/1-chatbot-ai/checklists/requirements.md** | Quality validation (24/24 pass) | ✅ Complete |
| **history/prompts/** | Development diary (PHRs) | ✅ 2 records |
| **history/adr/** | Architecture decisions | 🟡 TBD (after planning) |
| **specs/1-chatbot-ai/plan.md** | Architecture & design decisions | 🟡 Ready for `/sp.plan` |
| **specs/1-chatbot-ai/tasks.md** | Implementation tasks breakdown | 🟡 Ready for `/sp.tasks` |

---

## 🎯 Development Workflow

### Phase 1: ✅ Specification (COMPLETE)
- ✅ Constitution created (10 principles)
- ✅ Feature spec created (6 user stories, 18 FRs)
- ✅ Quality checklist validated (24/24 pass)
- ✅ PHRs documented for traceability

**Command**: `/sp.specify` ← Already executed

### Phase 2: 🟡 Planning (NEXT)
- Design architecture
- Define MCP tool integration
- API contracts
- Data flow diagrams
- Technical decisions

**Command**: `/sp.plan` ← Ready to execute

**Input**: Run from project root:
```bash
/sp.plan
```

### Phase 3: 🟡 Task Breakdown (AFTER PLANNING)
- Granular, testable implementation tasks
- Dependency ordering
- Effort estimates
- Assignment to team members

**Command**: `/sp.tasks`

### Phase 4: ⚪ Implementation (AFTER TASKS)
- Red-Green-Refactor cycle
- Unit & integration tests
- Code review
- Continuous integration

**Command**: `/sp.implement`

### Phase 5: ⚪ Deployment (AFTER IMPLEMENTATION)
- Staging verification
- Production deployment
- Rollback strategy

---

## 🔄 Git Workflow

### Branch Naming Convention
```
<number>-<short-name>
Example: 1-chatbot-ai
```

### Commit Message Format
```
<type>: <description>

Longer explanation if needed

Closes #issue-number
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Recent Commits
```
9d01fbd (HEAD -> master) feat: Initial commit - Hackathon II Phase 3 setup
```

---

## 📊 Project Statistics

| Category | Count |
|----------|-------|
| **User Stories** | 6 (3 P1, 2 P2, 1 P1 context) |
| **Functional Requirements** | 18 |
| **Success Criteria** | 10 |
| **Edge Cases** | 6 |
| **Key Entities** | 4 (User, Task, Conversation, Message) |
| **Out of Scope Items** | 10 |
| **MCP Tools** | 5 |
| **Frontend Components** | 12+ |
| **Backend Routes** | 10+ |
| **Database Tables** | 3 |
| **Git Files Committed** | 139 |
| **Lines of Code (Spec)** | ~750 |

---

## 🚀 Next Steps

1. **Execute `/sp.plan`** to generate architecture design
   - Design decisions for MCP integration
   - API contract definition
   - Data flow & deployment strategy
   - Technology choices & trade-offs

2. **Address any ADR suggestions** from planning phase
   - Document significant architectural decisions
   - Explain trade-offs & rationale

3. **Execute `/sp.tasks`** to break down into implementation tasks
   - Frontend tasks (ChatKit integration, UI)
   - Backend tasks (FastAPI endpoints, MCP server)
   - Database tasks (schema, migrations)
   - Integration tests

4. **Begin implementation** using `/sp.implement`
   - Follow constitution principles
   - TDD: tests first, then code
   - Submit PRs with spec/plan/tasks reference

---

## 💾 Local Development Setup

```bash
# Clone the repository
git clone <repo-url> hackathon-II-phase-3
cd hackathon-II-phase-3

# Backend setup
cd huggingface-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with Neon DB and OpenAI API keys
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with backend URL
npm run dev
```

---

## 📚 Important Documentation

- **Constitution**: `.specify/memory/constitution.md` — Project principles & quality standards
- **Spec**: `specs/1-chatbot-ai/spec.md` — User stories & requirements
- **README**: `README.md` — Technology stack & quick start
- **Original Spec**: `CLAUDE.md` — Hackathon II requirements document

---

**Repository Created**: 2025-01-20  
**Status**: 🟢 Specification Phase Complete | 🟡 Ready for Planning | ⚪ Implementation Pending

---

## 🤝 Contributing

1. Read `.specify/memory/constitution.md` first
2. Create feature branch: `git checkout -b <number>-<short-name>`
3. Follow SDD workflow: spec → plan → tasks → implement
4. Write tests before code (TDD)
5. Submit PR with references to spec/plan/tasks

