# 🔧 Frontend Environment Configuration

Your new backend is live at: **https://abbasshajar-todo-backend.hf.space**

Both Phase 2 and Phase 3 frontends must be configured to use this backend URL.

## 📋 Phase 3 Frontend Configuration

### File: `frontend/.env.local`

```env
# Backend API URL
NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space

# JWT Secret (MUST be identical to backend!)
NEXT_PUBLIC_BETTER_AUTH_SECRET=your-secret-key-here
```

**Replace `your-secret-key-here` with the actual secret you set on HuggingFace!**

---

## 📋 Phase 2 Frontend Configuration

### File: `frontend/.env.local`

Same as Phase 3:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space

# JWT Secret (MUST be identical to backend!)
NEXT_PUBLIC_BETTER_AUTH_SECRET=your-secret-key-here
```

---

## ⚠️ CRITICAL: Secret Key MUST Match

Your `BETTER_AUTH_SECRET` must be **IDENTICAL** in three places:

1. **HuggingFace Backend Secrets**
   - https://huggingface.co/spaces/abbasshajar/todo-backend/settings/secrets
   - Secret name: `BETTER_AUTH_SECRET`

2. **Phase 2 Frontend**
   - `frontend/.env.local`
   - Variable: `NEXT_PUBLIC_BETTER_AUTH_SECRET`

3. **Phase 3 Frontend**
   - `frontend/.env.local`
   - Variable: `NEXT_PUBLIC_BETTER_AUTH_SECRET`

**If they don't match, authentication will fail with 401 errors!**

---

## 🔑 Finding Your Secret

Your secret is already set on HuggingFace. To find it:

1. Go to: https://huggingface.co/spaces/abbasshajar/todo-backend
2. Click **Settings** (gear icon)
3. Click **Repository secrets** on left menu
4. Find `BETTER_AUTH_SECRET`
5. Copy the value
6. Add to **both** frontend `.env.local` files

---

## 📝 Complete Environment File

### Phase 3 Frontend Example

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space
NEXT_PUBLIC_BETTER_AUTH_SECRET=your-actual-secret-key

# Optional: Enable debug logging
# NEXT_PUBLIC_DEBUG=true
```

### Phase 2 Frontend Example

Exactly the same:

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space
NEXT_PUBLIC_BETTER_AUTH_SECRET=your-actual-secret-key

# Optional: Enable debug logging
# NEXT_PUBLIC_DEBUG=true
```

---

## ✅ Verification

After setting `.env.local`, test if it works:

1. Start frontend dev server:
   ```bash
   npm run dev
   ```

2. Try to sign up or log in

3. If you see the app load and can see tasks, it's working! ✅

4. If you get 401 errors, the secret doesn't match ❌

---

## 🚀 Steps to Deploy

1. **Update .env.local** in your Phase 3 frontend
2. **Update .env.local** in your Phase 2 frontend (if applicable)
3. **Test locally** - npm run dev
4. **Deploy to Vercel** - git push
5. **Verify** - Visit your Vercel URL and test signup/login

---

## 📞 Quick Reference

| Item | Value |
|------|-------|
| Backend URL | https://abbasshajar-todo-backend.hf.space |
| API Docs | https://abbasshajar-todo-backend.hf.space/docs |
| Env Variable | NEXT_PUBLIC_API_URL |
| Secret Variable | NEXT_PUBLIC_BETTER_AUTH_SECRET |
| Secret Location | HuggingFace space settings |

---

## 🆘 Troubleshooting

### Error: 401 Unauthorized

**Cause**: Secret key doesn't match

**Fix**:
1. Copy secret from HuggingFace
2. Paste in both frontend .env.local files
3. Restart frontend dev server
4. Try again

### Error: Cannot connect to backend

**Cause**: API URL is wrong

**Fix**:
1. Verify: `NEXT_PUBLIC_API_URL=https://abbasshajar-todo-backend.hf.space`
2. No trailing slash
3. Restart frontend

### Error: Backend returned 404

**Cause**: Endpoint doesn't exist

**Fix**:
1. Check API docs: https://abbasshajar-todo-backend.hf.space/docs
2. Verify endpoint is implemented
3. Check backend logs on HuggingFace

---

## ✨ Both Apps Using Same Backend

After configuration:

**Phase 2 App** (if you deploy it):
- Uses REST API only
- No chat assistant
- Points to same backend
- Shares same database

**Phase 3 App**:
- Uses REST API + Chat
- Has chat assistant
- Points to same backend
- Shares same database

**Result**: Same tasks in both apps! 🎉
