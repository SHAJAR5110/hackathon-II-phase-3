# Deployment Guide: Todo Backend to Hugging Face Docker Space

This guide walks you through deploying the Todo Backend to Hugging Face using Docker.

## ✅ Prerequisites

1. **Hugging Face Account** - Create at https://huggingface.co
2. **Git installed** - For version control
3. **Hugging Face CLI** (optional but recommended)
4. **PostgreSQL Database** - Neon, Render, or Heroku

## 📦 Files Prepared

The following files have been configured for Hugging Face deployment:

```
├── Dockerfile                    # Docker configuration for HF Spaces
├── .dockerignore                 # Files to exclude from Docker image
├── requirements.txt              # Python dependencies
├── main.py                       # FastAPI application entry point
├── db.py                         # Database configuration
├── models.py                     # SQLModel database models
├── routes/                       # API route handlers
│   ├── auth.py                   # Authentication endpoints
│   ├── tasks.py                  # Task CRUD endpoints
│   └── users.py                  # User endpoints
├── middleware/                   # Middleware modules
│   └── auth.py                   # JWT authentication
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore patterns
├── README_HF.md                  # Hugging Face documentation
└── DEPLOYMENT_TO_HF.md          # This file
```

## 🚀 Step-by-Step Deployment

### Step 1: Create PostgreSQL Database

Choose one of the options below:

#### Option A: Neon (Recommended)
1. Go to https://neon.tech
2. Sign up (free account available)
3. Create a new PostgreSQL database
4. Copy the connection string, it will look like:
   ```
   postgresql://user:xxxxx@ep-xxxx.neon.tech/todo_db?sslmode=require
   ```

#### Option B: Render
1. Go to https://render.com
2. Sign up (free tier available)
3. Create a PostgreSQL instance
4. Copy the external database URL

#### Option C: Heroku
1. Add Heroku PostgreSQL add-on
2. Copy the database URL from config vars

### Step 2: Prepare Your Local Environment

```bash
# Navigate to the HF-Todo-Backend directory
cd C:\Users\HP\Desktop\HF-Todo-Backend

# Create .env file from template
copy .env.example .env

# Edit .env with your database URL and secrets
# Use your favorite text editor to edit:
# - DATABASE_URL (from Step 1)
# - BETTER_AUTH_SECRET (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - ALLOWED_ORIGINS (your frontend URL)
```

### Step 3: Initialize Git Repository

```bash
# Initialize git in the HF-Todo-Backend directory
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Todo Backend for Hugging Face deployment"
```

### Step 4: Create Hugging Face Space

1. Go to https://huggingface.co/spaces/create
2. Fill in the form:
   - **Space name**: `todo-backend`
   - **Owner**: Select your account
   - **Space SDK**: Select **"Docker"**
   - **Space type**: Select **"Private"** (or Public if you prefer)
   - **Visibility**: Check "Private" for production
3. Click **"Create Space"**
4. Wait for the space to be created
5. Note your space URL: `https://huggingface.co/spaces/your-username/todo-backend`

### Step 5: Set Remote and Push Code

```bash
# Add Hugging Face as remote
git remote add hf https://huggingface.co/spaces/your-username/todo-backend

# Replace 'your-username' with your actual HF username

# Push to Hugging Face
git push hf main

# If you get authentication error, use Git credentials:
# When prompted, use your HF username and access token
# Get token from: https://huggingface.co/settings/tokens
```

**⚠️ Important**: When asked for password, use your **Hugging Face API token**, not your password.

To create/view tokens:
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it a name (e.g., "todo-backend-deployment")
4. Set scope to "Read & Write"
5. Click "Generate token"
6. Copy the token and use as password during `git push`

### Step 6: Configure Environment Variables

Once the space is created:

1. Go to your space: `https://huggingface.co/spaces/your-username/todo-backend`
2. Click **"Settings"** (gear icon in top right)
3. Click **"Repository secrets"** on the left menu
4. Add the following secrets:

   | Secret Name | Value |
   |---|---|
   | `DATABASE_URL` | Your PostgreSQL connection string |
   | `BETTER_AUTH_SECRET` | Your 32+ character secret key |
   | `ALLOWED_ORIGINS` | Your frontend URL (e.g., `https://xxx.vercel.app`) |

   **Optional**:
   | Secret Name | Value |
   |---|---|
   | `JWT_ALGORITHM` | `HS256` |
   | `JWT_EXPIRATION_DAYS` | `7` |
   | `APP_ENV` | `production` |
   | `DEBUG` | `False` |

5. Click **"Save"** for each secret

### Step 7: Monitor Deployment

1. Stay on your space page
2. You should see a "Building" status indicator
3. Wait 2-5 minutes for Docker image to build
4. Once complete, you'll see the API running

You can view build logs:
- Click the **"Logs"** tab to see build progress
- Check for any errors in the build output

### Step 8: Verify Deployment

Once deployment is complete:

1. **Health Check**: Open `https://abbasshajar-todo-backend.hf.space/health`
   - Should return: `{"status":"healthy","message":"Todo API is running"}`

2. **Interactive Docs**: Open `https://abbasshajar-todo-backend.hf.space/docs`
   - Should show Swagger UI with all available endpoints

3. **ReDoc**: Open `https://abbasshajar-todo-backend.hf.space/redoc`
   - Alternative API documentation

### Step 9: Update Frontend URL

Once the backend is running, update your frontend configuration:

**File**: `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space
```

Or in Vercel project settings:
1. Go to https://vercel.com/dashboard
2. Select your project
3. Click **"Settings" → "Environment Variables"**
4. Update `NEXT_PUBLIC_API_URL`:
   - Value: `https://abbasshajar-todo-backend.hf.space`
   - Scope: Production, Preview, Development

Then redeploy your frontend on Vercel.

## 🔄 Updating the Backend

To update the backend code:

```bash
# Make your changes
# Edit files as needed

# Stage and commit changes
git add .
git commit -m "Your commit message"

# Push to Hugging Face (auto-triggers rebuild)
git push hf main
```

The space will automatically rebuild with your new code.

## 🚨 Troubleshooting

### Build fails with "Command not found"
- Check requirements.txt has all dependencies
- Verify Python syntax is correct

### "Connection refused" to database
- Verify DATABASE_URL is correct in secrets
- Check database is running and accessible
- Verify IP whitelist allows Hugging Face IPs (usually no restrictions needed)

### "Module not found" error
- Add the missing package to `requirements.txt`
- Run: `pip install <package-name>` locally first
- Update requirements.txt: `pip freeze > requirements.txt`
- Commit and push again

### API returns 500 errors
- Check logs in Hugging Face space
- Verify all environment variables are set
- Test database connection manually

### CORS errors in frontend
- Verify `ALLOWED_ORIGINS` secret includes your frontend URL
- Frontend URL must match exactly (protocol + domain)
- Redeploy space after updating secrets

### Git authentication issues
Use Hugging Face CLI instead:

```bash
huggingface-cli login
# Enter your username and token

git push hf main
# Should work without password prompt
```

## 📊 Monitoring

To monitor your API:

1. **View Logs**:
   - Go to your space page
   - Click "Logs" tab to see real-time output

2. **Check Health**:
   - Visit `/health` endpoint regularly
   - Set up monitoring (optional)

3. **API Usage**:
   - View in Hugging Face space statistics
   - Monitor request count and performance

## 🔐 Security Best Practices

✅ **Do**:
- Keep `.env` out of git (use `.gitignore`)
- Use strong SECRET keys (32+ characters)
- Update secrets regularly
- Use HTTPS endpoints only
- Verify ALLOWED_ORIGINS matches your frontend

❌ **Don't**:
- Commit `.env` file
- Share API tokens publicly
- Use test secrets in production
- Allow `*` in ALLOWED_ORIGINS (production)
- Expose DATABASE_URL in logs

## 📝 Next Steps

1. ✅ Deploy backend to Hugging Face
2. ✅ Verify API is running
3. ✅ Update frontend `NEXT_PUBLIC_API_URL`
4. ✅ Redeploy frontend on Vercel
5. ✅ Test authentication flow end-to-end
6. ✅ Monitor both applications

## 📚 Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Hugging Face Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neon PostgreSQL](https://neon.tech/docs/)

## 🎉 You're Done!

Once everything is set up:
- Backend runs at: `https://abbasshajar-todo-backend.hf.space`
- Frontend at: Your Vercel URL
- Both are connected and ready to use!

---

**Questions?** Check the README_HF.md file for more details about the API.
