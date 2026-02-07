# Todo Backend API - Hugging Face Docker Space

A production-ready FastAPI backend for a full-stack Todo application with JWT authentication and PostgreSQL database.

**Live API**: This space deploys to 

## 🚀 Features

- ✅ **FastAPI** - Modern async Python web framework
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **PostgreSQL** - Reliable relational database
- ✅ **SQLModel ORM** - Type-safe database queries
- ✅ **User Isolation** - Each user's data is isolated and secure
- ✅ **CORS Protection** - Configurable cross-origin resource sharing
- ✅ **Async/Await** - Full async support for performance
- ✅ **Docker Ready** - Optimized for Hugging Face Docker Spaces

## 📋 API Endpoints

### Health Check
- `GET /` - API information
- `GET /health` - Health status check

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user
- `POST /api/auth/logout` - Logout user

### Tasks
- `GET /api/tasks` - List all user tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{task_id}` - Get specific task
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task
- `PATCH /api/tasks/{task_id}/complete` - Toggle task completion

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

## 🔧 Setup Instructions

### 1. Clone the Space

```bash
git clone https://huggingface.co/spaces/abbasshajar/todo-backend
cd todo-backend
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

**Required environment variables:**

```env
# Database URL (PostgreSQL)
DATABASE_URL=postgresql://user:password@host/database

# JWT Secret (at least 32 characters)
BETTER_AUTH_SECRET=your-secret-key-here

# Frontend URL
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app

# App settings
APP_ENV=production
DEBUG=False
```

### 3. Deploy on Hugging Face

1. **Create a Hugging Face Account** (if you don't have one)
   - Visit https://huggingface.co
   - Sign up or log in

2. **Create a Docker Space**
   - Go to https://huggingface.co/spaces/create
   - Select "Docker" as the SDK
   - Name it `todo-backend`
   - Set it to Private (or Public if you prefer)

3. **Push Code**
   ```bash
   git remote add hf https://huggingface.co/spaces/your-username/todo-backend
   git push hf main
   ```

4. **Configure Secrets**
   - Go to Space Settings
   - Click "Repository secrets"
   - Add your environment variables as secrets:
     - `DATABASE_URL`
     - `BETTER_AUTH_SECRET`
     - `ALLOWED_ORIGINS`

5. **Space will auto-deploy** 🎉

## 🔌 Database Setup

### Option 1: Neon (Recommended)

1. Create account at https://neon.tech
2. Create a PostgreSQL database
3. Copy connection string: `postgresql://...`
4. Paste in `.env` as `DATABASE_URL`

### Option 2: Render

1. Create account at https://render.com
2. Create a PostgreSQL instance
3. Copy connection string
4. Paste in `.env` as `DATABASE_URL`

### Option 3: Local (Development Only)

```bash
# Install PostgreSQL locally
# Create database
createdb todo_db

# Set connection string
DATABASE_URL=postgresql://localhost/todo_db
```

## 🧪 Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Run specific test file
pytest tests/test_tasks.py -v

# Run with coverage
pytest --cov=. tests/
```

## 📖 API Documentation

Once deployed, access interactive docs at:
- **Swagger UI**: `https://abbasshajar-todo-backend.hf.space/docs`
- **ReDoc**: `https://abbasshajar-todo-backend.hf.space/redoc`

## 🔐 Security Notes

### Environment Variables
- **Never** commit `.env` files to git
- Use Hugging Face "Repository secrets" for sensitive data
- Rotate secrets regularly in production

### JWT Secret
- Must be at least 32 characters
- Must match frontend `NEXT_PUBLIC_BETTER_AUTH_SECRET`
- Use a cryptographically secure random string:
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```

### CORS
- Configure `ALLOWED_ORIGINS` to only allow trusted frontend URLs
- Never use `*` in production (current: limited to configured origins)

### Database
- Use strong passwords for database connections
- Enable SSL for database connections (production)
- Keep database credentials in environment variables only

## 🚨 Troubleshooting

### "Connection refused" error
- Check `DATABASE_URL` is correct
- Verify PostgreSQL service is running
- Check network/firewall access

### "Invalid token" error
- Verify `BETTER_AUTH_SECRET` matches frontend value
- Check token hasn't expired
- Check Authorization header format: `Bearer <token>`

### CORS errors
- Add frontend URL to `ALLOWED_ORIGINS`
- Check frontend makes requests with correct headers
- Verify request origins match configuration

### 500 Internal Server Error
- Check application logs in Hugging Face
- Verify all environment variables are set
- Check database connection is working

## 📚 Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Hugging Face Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in Hugging Face Space settings
3. Open an issue on the project repository

## 📄 License

This project is part of the Phase II Hackathon applications.
