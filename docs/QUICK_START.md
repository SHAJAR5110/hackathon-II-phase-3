# Quick Start Guide - AI-Powered Todo Chatbot

## 🚀 Prerequisites

- **Node.js:** >= 20.0.0
- **Python:** >= 3.11
- **PostgreSQL:** Neon Serverless (or local PostgreSQL)
- **OpenAI API Key:** From https://platform.openai.com

---

## 📦 Installation

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your credentials:
# - NEON_DATABASE_URL
# - OPENAI_API_KEY
# - JWT_SECRET_KEY (generate a strong random key)

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn src.main:app --reload --port 8000
```

**Backend will be running at:** http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment (optional for development)
# Edit .env.local if needed:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - NEXT_PUBLIC_OPENAI_DOMAIN_KEY=localhost

# Start development server
npm run dev
```

**Frontend will be running at:** http://localhost:3000

---

## 🔑 Environment Variables

### Backend (.env)

```env
# Required
NEON_DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=sk-proj-xxxxx
JWT_SECRET_KEY=your-secret-key-here

# Optional
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional (for production deployment)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
```

---

## 🧪 Testing

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Type checking
npm run type-check

# Linting
npm run lint
```

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

---

## 🏗️ Building for Production

### Frontend

```bash
cd frontend

# Build production bundle
npm run build

# Start production server
npm start
```

### Backend

```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn (production ASGI server)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/signin` | Login user |
| POST | `/api/auth/logout` | Logout user |
| GET | `/api/auth/users/me` | Get current user |

### Tasks (Protected - Requires Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks |
| GET | `/api/tasks/{id}` | Get task by ID |
| POST | `/api/tasks` | Create new task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle task completion |

### Chat (AI-Powered)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message to AI chatbot |

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API information |
| GET | `/docs` | Swagger UI documentation |

---

## 🔒 Authentication Flow

1. **Register:** `POST /api/auth/signup`
   ```json
   {
     "email": "user@example.com",
     "password": "securepass123",
     "name": "John Doe"
   }
   ```

2. **Login:** `POST /api/auth/signin`
   ```json
   {
     "email": "user@example.com",
     "password": "securepass123"
   }
   ```
   Response includes JWT token:
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "bearer",
     "user": {
       "id": "user123",
       "email": "user@example.com",
       "name": "John Doe"
     }
   }
   ```

3. **Use Token:** Include in Authorization header for protected routes
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

---

## 🤖 Chatbot Usage

### Example Chat Request

```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": null
  }'
```

### Example Response

```json
{
  "conversation_id": 1,
  "response": "I've added a new task: Buy groceries. Would you like to add any details?",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "title": "Buy groceries",
        "user_id": "user123"
      },
      "result": {
        "task_id": 5,
        "status": "created"
      }
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Backend won't start

**Issue:** Database connection error
```bash
# Check your NEON_DATABASE_URL in .env
# Verify database is accessible
psql $NEON_DATABASE_URL -c "SELECT 1"
```

**Issue:** Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start

**Issue:** Module not found errors
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
```

**Issue:** Type errors
```bash
# Run type check to see issues
npm run type-check
```

### Tests failing

**Frontend:** Check that test dependencies are installed
```bash
npm list @testing-library/react jest
```

**Backend:** Check Python environment
```bash
python -c "import pytest; print(pytest.__version__)"
```

---

## 📚 Additional Resources

- **Next.js Documentation:** https://nextjs.org/docs
- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **OpenAI Agents SDK:** https://github.com/openai/openai-agents-sdk
- **MCP SDK:** https://github.com/modelcontextprotocol/sdk
- **Neon PostgreSQL:** https://neon.tech/docs

---

## 🎯 Next Steps

1. ✅ Complete database setup with actual credentials
2. ✅ Test authentication flow end-to-end
3. ✅ Create sample tasks via API
4. ✅ Test chatbot with natural language commands
5. ✅ Deploy to production (Vercel + Railway/Fly.io)

---

**Happy Coding! 🚀**
