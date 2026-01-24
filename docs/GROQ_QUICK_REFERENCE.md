# Groq Integration - Quick Reference Card

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Verify Configuration
```bash
# Check .env has GROQ_API_KEY
grep GROQ_API_KEY backend/.env

# Should output:
# GROQ_API_KEY=gsk_<your-api-key-here>
```

### 3. Run Backend
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 4. Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/testuser/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer testuser" \
  -d '{
    "message": "Add a task to buy milk",
    "conversation_id": null
  }'
```

---

## ⚙️ Configuration

### Environment Variables
```env
# Required
GROQ_API_KEY=gsk_...                          # Your Groq API key

# Model Settings
GROQ_MODEL=openai/gpt-oss-120b                # Model to use
GROQ_TEMPERATURE=1.0                          # 0.0 to 1.0
GROQ_MAX_TOKENS=8192                          # Max response tokens
GROQ_TOP_P=1.0                                # 0.0 to 1.0
GROQ_REASONING_EFFORT=medium                  # low|medium|high

# Other
AGENT_TIMEOUT=30                              # Seconds
DATABASE_URL=postgresql://...                 # PostgreSQL
JWT_SECRET_KEY=...                            # JWT secret
```

### Quick Configuration
```bash
# Change model (in .env)
GROQ_MODEL=mixtral-8x7b-32768         # Faster
GROQ_MODEL=llama-3.1-70b-versatile    # More powerful
GROQ_MODEL=llama-3.1-8b-instant       # Lightweight

# Adjust for speed
GROQ_REASONING_EFFORT=low             # Faster, less reasoning
GROQ_MAX_TOKENS=2048                  # Shorter responses

# Adjust for quality
GROQ_REASONING_EFFORT=high            # Slower, better reasoning
GROQ_TEMPERATURE=0.3                  # More deterministic
```

---

## 🧠 Available Tools

| Tool | Description | Parameters | Example |
|------|-------------|-----------|---------|
| `add_task` | Create task | `title` (req), `description` | "Add a task to buy milk" |
| `list_tasks` | List tasks | `status` (all\|pending\|completed) | "Show pending tasks" |
| `complete_task` | Mark done | `task_id` | "Mark task 1 complete" |
| `delete_task` | Remove task | `task_id` | "Delete task 2" |
| `update_task` | Edit task | `task_id`, `title`, `description` | "Change task 1 to call mom" |

---

## 💬 Example Conversations

### Add Task
```
User: "Add a task to buy groceries"
↓
Agent: Invokes add_task(title="Buy groceries")
↓
Response: "I've added 'Buy groceries' to your tasks!"
Tool Calls: [{"tool": "add_task", "params": {"title": "Buy groceries"}}]
```

### List Tasks
```
User: "What tasks are pending?"
↓
Agent: Invokes list_tasks(status="pending")
↓
Response: "You have 3 pending tasks:..."
Tool Calls: [{"tool": "list_tasks", "params": {"status": "pending"}}]
```

### Complete Task
```
User: "Mark task 1 as done"
↓
Agent: Invokes complete_task(task_id=1)
↓
Response: "Great! Task completed."
Tool Calls: [{"tool": "complete_task", "params": {"task_id": 1}}]
```

### Complex Request
```
User: "Show me my pending tasks and mark the first one done"
↓
Agent: Invokes list_tasks, then complete_task
↓
Response: "Done! Here are your remaining tasks:..."
Tool Calls: [
  {"tool": "list_tasks", "params": {"status": "pending"}},
  {"tool": "complete_task", "params": {"task_id": 1}}
]
```

---

## 📊 Response Format

### Success Response
```json
{
  "conversation_id": 1,
  "response": "I've added 'Buy groceries' to your tasks!",
  "tool_calls": [
    {
      "tool": "add_task",
      "params": {
        "title": "Buy groceries",
        "description": null
      }
    }
  ]
}
```

### No Tools Response
```json
{
  "conversation_id": 2,
  "response": "You currently have 3 tasks.",
  "tool_calls": []
}
```

### Error Response
```json
{
  "error": "Internal server error",
  "request_id": "req-12345"
}
```

---

## 🔍 Debugging

### Check Logs
```bash
# Backend logs show Groq integration
tail -f /tmp/agent.log | grep groq

# Expected output:
# groq_client_initialized model=openai/gpt-oss-120b
# groq_chat_complete_starting message_count=3
# agent_with_tools_completed tool_calls_made=1
```

### Test Components
```python
# Test Groq client
from dotenv import load_dotenv
load_dotenv()
from src.agents.groq_client import GroqClient

client = GroqClient()  # Should work if API key set
print("✓ Client initialized")

# Test agent config
from src.agents.config import AgentConfig
print(AgentConfig.GROQ_MODEL)  # Should print: openai/gpt-oss-120b

# Test agent runner
from src.agents.runner import AgentRunner
runner = AgentRunner()
await runner.initialize_agent()  # Should succeed
```

### Common Errors

```
Error: "GROQ_API_KEY not provided"
Fix: load_dotenv() before importing GroqClient

Error: "Tool calls not extracted"
Fix: Check system prompt includes tool schema

Error: "Timeout"
Fix: Increase AGENT_TIMEOUT or reduce GROQ_MAX_TOKENS

Error: "Model not found"
Fix: Check GROQ_MODEL is supported (see console.groq.com)
```

---

## 📈 Performance Tips

### For Speed ⚡
```env
GROQ_MODEL=llama-3.1-8b-instant
GROQ_REASONING_EFFORT=low
GROQ_MAX_TOKENS=2048
GROQ_TEMPERATURE=0.5
```
Typical: 0.5-1.0 seconds

### For Quality ⭐
```env
GROQ_MODEL=openai/gpt-oss-120b
GROQ_REASONING_EFFORT=high
GROQ_MAX_TOKENS=8192
GROQ_TEMPERATURE=0.3
```
Typical: 2-5 seconds

### Balanced (Default) ⚖️
```env
GROQ_MODEL=openai/gpt-oss-120b
GROQ_REASONING_EFFORT=medium
GROQ_MAX_TOKENS=8192
GROQ_TEMPERATURE=1.0
```
Typical: 1-3 seconds

---

## 🔑 API Key Management

### Get Groq API Key
1. Go to https://console.groq.com
2. Sign up or login
3. Navigate to API keys
4. Generate new key
5. Copy and paste into `.env` as `GROQ_API_KEY`

### Security Best Practices
- ✅ Store in `.env` (never in code)
- ✅ Use in production from environment variables
- ✅ Rotate keys regularly
- ✅ Never share or expose key
- ✅ Use different keys for dev/prod

---

## 🧪 Testing Commands

### Test API Key
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ OK' if os.getenv('GROQ_API_KEY') else '✗ FAIL')"
```

### Test Model Load
```bash
python -c "
from dotenv import load_dotenv
load_dotenv()
from src.agents.config import AgentConfig
print(f'Model: {AgentConfig.GROQ_MODEL}')
print(f'Temperature: {AgentConfig.TEMPERATURE}')
print(f'Max Tokens: {AgentConfig.MAX_TOKENS}')
"
```

### Test Full Integration
```bash
cd backend
python test_groq_integration.py
```

---

## 📚 Files Modified/Created

### New Files
- ✅ `src/agents/groq_client.py` - Groq client implementation
- ✅ `test_groq_integration.py` - Test suite
- ✅ `GROQ_INTEGRATION.md` - Full documentation
- ✅ `GROQ_IMPLEMENTATION_SUMMARY.md` - Implementation details
- ✅ `GROQ_QUICK_REFERENCE.md` - This file

### Modified Files
- ✅ `src/agents/runner.py` - Groq integration
- ✅ `src/agents/config.py` - Groq config
- ✅ `requirements.txt` - Added groq==0.13.2
- ✅ `.env` - Groq variables

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Verify GROQ_API_KEY is valid and in production environment
- [ ] Test with production database
- [ ] Set appropriate AGENT_TIMEOUT
- [ ] Review GROQ_TEMPERATURE for your use case
- [ ] Set GROQ_REASONING_EFFORT (medium recommended)
- [ ] Configure monitoring and logging
- [ ] Set up error alerts
- [ ] Test high-volume scenarios
- [ ] Document custom tool additions
- [ ] Set up backup API key

---

## 📞 Support Resources

### Groq
- **Console:** https://console.groq.com
- **Docs:** https://docs.groq.com
- **Status:** https://status.groq.com

### Project
- **Spec:** `specs/1-chatbot-ai/spec.md`
- **Tests:** `backend/test_groq_integration.py`
- **Logs:** Check application logs for groq_* entries

### Troubleshooting
- Check `.env` configuration
- Verify API key is correct
- Review application logs
- Test with curl commands
- Run test suite: `python test_groq_integration.py`

---

## ✅ Status

| Component | Status | Notes |
|-----------|--------|-------|
| Groq Client | ✅ Complete | Streaming & non-streaming |
| Agent Runner | ✅ Complete | MCP tool integration working |
| Configuration | ✅ Complete | All parameters configurable |
| Error Handling | ✅ Complete | Comprehensive logging |
| Testing | ✅ Complete | Full test suite included |
| Documentation | ✅ Complete | Ready for production |

---

**Production Ready:** ✅ **YES**  
**Last Updated:** 2026-01-22  
**Version:** 1.0.0
