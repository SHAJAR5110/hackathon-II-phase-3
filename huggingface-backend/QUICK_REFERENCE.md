# ⚡ Quick Reference - Hugging Face Deployment

## 🚀 Deploy in 5 Steps

```bash
# 1. Setup environment
cd C:\Users\HP\Desktop\HF-Todo-Backend
copy .env.example .env
# Edit .env with your DATABASE_URL and BETTER_AUTH_SECRET

# 2. Initialize git
git init
git add .
git commit -m "Initial commit: Todo Backend"

# 3. Add Hugging Face remote
# Replace YOUR_USERNAME with your actual Hugging Face username
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/todo-backend

# 4. Push to Hugging Face
git push hf main

# 5. Configure secrets on Hugging Face
# Go to: https://huggingface.co/spaces/YOUR_USERNAME/todo-backend/settings/secrets
# Add:
#   - DATABASE_URL
#   - BETTER_AUTH_SECRET
#   - ALLOWED_ORIGINS
```

## 🔑 Generate Secrets

```python
# In Python terminal:
import secrets
print(secrets.token_urlsafe(32))  # Your BETTER_AUTH_SECRET
```

## 📋 Essential Secrets

| Secret | Example | Where to Get |
|--------|---------|--------------|
| `DATABASE_URL` | `postgresql://user:pass@neon.tech/db?sslmode=require` | Neon.tech or Render |
| `BETTER_AUTH_SECRET` | `oH7KdK-Z8_9a1bCdEfGhIjKlMnOpQrS` | Generate with Python script above |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` | Your Vercel frontend URL |

## 🌐 Deployment URLs

After deployment, access at:

```
https://abbasshajar-todo-backend.hf.space
├── /                   API info
├── /health            Health check
├── /docs              Swagger UI
├── /redoc             ReDoc docs
└── /api/*            Your API endpoints
```

## 🔄 Update Backend Code

```bash
# Make your changes to files
# ...

# Commit and push
git add .
git commit -m "Your message"
git push hf main
# Space automatically rebuilds!
```

## 🧪 Test Your API

```bash
# Health check
curl https://abbasshajar-todo-backend.hf.space/health

# Get API info
curl https://abbasshajar-todo-backend.hf.space/

# View docs
open https://abbasshajar-todo-backend.hf.space/docs
```

## 🔐 Security Commands

```bash
# Generate strong secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Verify .env not in git
git status  # Should NOT list .env

# Check gitignore is working
git ls-files -o --exclude-standard  # Should not show .env
```

## 📝 Environment Variables

```env
# Required
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your-secret-here
ALLOWED_ORIGINS=https://frontend-url.com

# Optional (defaults work)
APP_ENV=production
DEBUG=False
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
```

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Check `requirements.txt` has all dependencies |
| Connection error | Verify `DATABASE_URL` in secrets |
| 401 Unauthorized | Check `BETTER_AUTH_SECRET` matches frontend |
| CORS errors | Add frontend URL to `ALLOWED_ORIGINS` secret |
| Module not found | Add to `requirements.txt`, then `git push hf main` |

## 📚 Documentation Files

```
HF-Todo-Backend/
├── SETUP_SUMMARY.md          ← Start here (overview)
├── DEPLOYMENT_TO_HF.md       ← Step-by-step deployment
├── QUICK_REFERENCE.md        ← This file (commands)
├── README_HF.md              ← Full documentation
└── Dockerfile                ← Container config
```

## 🎯 Frontend Integration

After backend is live:

```env
# Update: frontend/.env.local
NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space
```

## 📊 Useful Links

- 🏠 **Space Dashboard**: https://huggingface.co/spaces/YOUR_USERNAME/todo-backend
- 🔑 **API Tokens**: https://huggingface.co/settings/tokens
- 📖 **FastAPI Docs**: https://fastapi.tiangolo.com/
- 🐘 **Neon PostgreSQL**: https://neon.tech/

## 💡 Pro Tips

✅ Always use `.env.example` as template
✅ Keep secrets in Hugging Face secrets, not in git
✅ Use meaningful commit messages
✅ Test locally before pushing
✅ Check build logs if deployment fails
✅ Monitor API health regularly

---

**Stuck?** Check DEPLOYMENT_TO_HF.md for detailed instructions.
