---
title: Phase III
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Todo Backend API

Production-ready FastAPI backend for a full-stack todo application with JWT authentication and PostgreSQL database.

## 🚀 Features

- ✅ **FastAPI** - Modern async Python framework
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **PostgreSQL** - Reliable relational database
- ✅ **SQLModel ORM** - Type-safe queries
- ✅ **User Isolation** - Data security
- ✅ **CORS Protection** - Cross-origin security
- ✅ **Full API Docs** - Auto-generated at `/docs`

## 🔧 Required Configuration

This space requires these environment variables. Set them in Space settings:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `BETTER_AUTH_SECRET` | JWT signing secret (32+ chars) | Generate with Python script |
| `ALLOWED_ORIGINS` | Frontend URL for CORS | `https://your-app.vercel.app` |

**Optional:**
- `APP_ENV`: `production` (default)
- `DEBUG`: `False` (default)
- `JWT_EXPIRATION_DAYS`: `7` (default)

## 📖 API Endpoints

**Health & Documentation:**
- `GET /` - API information
- `GET /health` - Health status
- `GET /docs` - Swagger UI (interactive)
- `GET /redoc` - ReDoc documentation

**Authentication:**
- `POST /api/auth/signup` - Register user
- `POST /api/auth/signin` - Login user
- `POST /api/auth/logout` - Logout user

**Tasks (Require Auth):**
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion

**User Profile (Require Auth):**
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile

## 🔐 Security

- **JWT Validation**: All protected endpoints validate tokens
- **User Isolation**: Each user's data is isolated and secure
- **CORS Protection**: Configurable trusted origins only
- **Input Validation**: Pydantic models validate all requests
- **Error Handling**: Proper HTTP status codes

## 📚 Documentation

For complete setup and deployment instructions:
- `START_HERE.md` - Quick overview (5 min)
- `DEPLOYMENT_TO_HF.md` - Detailed guide
- `README_HF.md` - Full API documentation
- `QUICK_REFERENCE.md` - Command reference

## 🛠 Tech Stack

- **Framework**: FastAPI (async)
- **Language**: Python 3.9+
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon recommended)
- **Authentication**: JWT
- **Testing**: pytest

## 📦 Database

Requires PostgreSQL. Free tier options:
- **Neon**: https://neon.tech (Recommended)
- **Render**: https://render.com
- **Heroku**: https://heroku.com

## 🎯 Getting Started

1. Create PostgreSQL database (Neon.tech)
2. Generate secrets (see DEPLOYMENT_TO_HF.md)
3. Set environment variables in Space settings
4. Space auto-deploys (2-5 minutes)
5. Access API docs at `/docs`

## 📞 Support

- Questions? → See `START_HERE.md`
- Setup help? → See `DEPLOYMENT_TO_HF.md`
- API details? → See `README_HF.md`

## 🌐 Live API

Once deployed, your API is available at:
```
https://huggingface.co/spaces/abbasshajar/phaseIII
```

**Interactive API Docs**: Visit the space URL and navigate to `/docs`
