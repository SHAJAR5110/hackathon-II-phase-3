# 🚀 HuggingFace Deployment Guide - Phase 3 Backend

This guide walks you through deploying the new **AI-Powered Todo Backend** to HuggingFace Spaces.

## 📍 Target

**HuggingFace Space URL**: https://abbasshajar-todo-backend.hf.space

This same backend will serve both:
- Phase 2 Frontend (without chat)
- Phase 3 Frontend (with chat)

## ⚡ 5-Step Deployment

### Step 1: Prepare Environment Variables

#### Get PostgreSQL Database URL
1. Go to https://neon.tech
2. Sign up/Login
3. Create a new project
4. Copy the connection string (looks like):
   ```
   postgresql://user:password@ep-xxx.neon.tech/todo_db?sslmode=require
   ```

#### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Get Groq API Key
1. Go to https://console.groq.com
2. Create an API key
3. Copy it

### Step 2: Push Code to HuggingFace

```bash
# Navigate to huggingface-backend directory
cd "C:\Users\HP\Desktop\H\GIAIC\phase 3\huggingface-backend"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "feat: AI-Powered Todo Backend with Chat Assistant"

# Add HuggingFace remote
# Replace abbasshajar with your HF username if different
git remote add hf https://huggingface.co/spaces/abbasshajar/todo-backend

# Push to HuggingFace
git push hf main
```

**When prompted for password**: Use your HuggingFace API token
- Get token from: https://huggingface.co/settings/tokens

### Step 3: Configure Secrets on HuggingFace

1. Go to: https://huggingface.co/spaces/abbasshajar/todo-backend/settings/secrets

2. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `DATABASE_URL` | `postgresql://user:password@ep-xxx.neon.tech/todo_db?sslmode=require` |
| `BETTER_AUTH_SECRET` | Your generated secret (32+ chars) |
| `ALLOWED_ORIGINS` | `https://your-phase2-app.vercel.app,https://your-phase3-app.vercel.app` |
| `GROQ_API_KEY` | Your Groq API key |
| `ENVIRONMENT` | `production` |
| `GROQ_MODEL` | `openai/gpt-oss-120b` |

3. Click **Save** for each

**⏳ Wait 2-5 minutes for deployment...**

### Step 4: Verify Deployment

```bash
# Check if backend is running
curl https://abbasshajar-todo-backend.hf.space/health

# Expected response:
# {"status": "healthy", "version": "1.0.0", "environment": "production"}
```

View documentation at:
- Swagger UI: https://abbasshajar-todo-backend.hf.space/docs
- ReDoc: https://abbasshajar-todo-backend.hf.space/redoc

### Step 5: Configure Both Frontends

#### Phase 2 Frontend (without chat)
Update `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space
NEXT_PUBLIC_BETTER_AUTH_SECRET=your-secret-key
```

Deploy to Vercel.

#### Phase 3 Frontend (with chat)
Update `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space
NEXT_PUBLIC_BETTER_AUTH_SECRET=your-secret-key
```

Deploy to Vercel.

Both apps now use the same backend and database! ✅

## 🔄 Updating Backend Code

After deployment, if you need to update backend code:

```bash
cd "C:\Users\HP\Desktop\H\GIAIC\phase 3\huggingface-backend"

# Make your changes to files...

# Commit and push
git add .
git commit -m "fix: description of changes"
git push hf main

# HuggingFace automatically rebuilds!
```

Check logs at: https://huggingface.co/spaces/abbasshajar/todo-backend/logs

## 📊 What Each Frontend Gets

### Phase 2 Frontend (Original)
- ✅ REST API for task CRUD
- ✅ Authentication
- ✅ Task listing/creation/update/delete
- ✅ User session management
- ❌ No chat assistant

### Phase 3 Frontend (New with Chat)
- ✅ All of Phase 2 features
- ✅ REST API for task CRUD
- ✅ Authentication
- ✅ Task listing/creation/update/delete
- ✅ User session management
- ✅ **NEW: Chat Assistant for task management**
- ✅ Task IDs visible on cards
- ✅ Clean chat (no JSON visible)
- ✅ Conversation history

## 🔄 Shared Database Structure

```
PostgreSQL (Neon)
├── users                    (Shared)
│   ├── user_id
│   ├── email
│   └── created_at
│
├── tasks                    (Shared)
│   ├── id
│   ├── user_id (indexed)
│   ├── title
│   ├── description
│   ├── completed
│   ├── created_at
│   └── updated_at
│
├── conversations            (Phase 3 only)
│   ├── id
│   ├── user_id (indexed)
│   ├── created_at
│   └── updated_at
│
└── messages                 (Phase 3 only)
    ├── id
    ├── conversation_id
    ├── user_id
    ├── role (user/assistant)
    ├── content
    └── created_at
```

## 🔐 Security Checklist

- ✅ `.env` file NOT pushed to git
- ✅ `.env.example` DOES show structure
- ✅ Secrets stored in HuggingFace secrets
- ✅ `BETTER_AUTH_SECRET` identical for all apps
- ✅ CORS configured with frontend URLs
- ✅ JWT tokens in Authorization header
- ✅ Database queries filter by user_id
- ✅ Dockerfile uses non-root user

## 🐛 Troubleshooting

### Build Failed
**Check**: https://huggingface.co/spaces/abbasshajar/todo-backend/logs

Usually caused by:
- Missing dependency in `requirements.txt`
- Syntax error in code
- Port binding issue

### Database Connection Error
```
psycopg2.OperationalError: could not connect to server
```

**Fix**:
1. Verify `DATABASE_URL` is correct in secrets
2. Check Neon database is active
3. Check IP whitelist (should be open for Neon free tier)

### 401 Unauthorized Errors
**Cause**: `BETTER_AUTH_SECRET` doesn't match between frontend and backend

**Fix**:
1. Ensure all frontends use same secret
2. Update in frontend `.env.local`
3. Update in HuggingFace secrets
4. Redeploy frontends

### CORS Error from Frontend
```
Access to XMLHttpRequest blocked by CORS policy
```

**Fix**:
1. Check frontend URL is in `ALLOWED_ORIGINS` secret
2. URLs must match exactly (https://example.com, NOT https://example.com/)
3. Redeploy space after updating secret

### Chat Not Working
**Cause**: `GROQ_API_KEY` missing or invalid

**Fix**:
1. Verify API key at https://console.groq.com
2. Add/update `GROQ_API_KEY` in HuggingFace secrets
3. Redeploy space

## 📞 Quick Reference

| Task | Command |
|------|---------|
| View logs | https://huggingface.co/spaces/abbasshajar/todo-backend/logs |
| Update code | `git push hf main` |
| Check health | `curl .../health` |
| View API docs | https://abbasshajar-todo-backend.hf.space/docs |
| Manage secrets | https://huggingface.co/spaces/abbasshajar/todo-backend/settings/secrets |

## ✨ Both Apps in Production

**Now you have**:
- Phase 2: Simple todo app (no AI)
  - URL: Your Phase 2 Vercel deployment
  - Backend: https://abbasshajar-todo-backend.hf.space

- Phase 3: AI-powered todo app (with chat)
  - URL: Your Phase 3 Vercel deployment
  - Backend: https://abbasshajar-todo-backend.hf.space ← Same!

Both use the same database, so users can switch between apps and see the same tasks! 🎉

