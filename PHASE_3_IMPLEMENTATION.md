# Phase 3: Authentication & Middleware Implementation

## Overview

Phase 3 implements complete authentication, authorization, and middleware infrastructure for the AI-Powered Todo Chatbot backend. This phase establishes the security and observability foundation for all subsequent phases.

## Tasks Completed

### T011 - Authentication Middleware
**File**: `backend/src/middleware/auth.py`

Creates a FastAPI middleware that:
- Extracts `user_id` from the `Authorization: Bearer <user_id>` header
- Validates user_id format (alphanumeric, hyphens, underscores, dots; max 255 chars)
- Attaches authenticated user_id to `request.state.user_id`
- Returns 401 Unauthorized for missing or invalid authentication

**Key Features**:
- Pattern validation: `^[a-zA-Z0-9._-]+$`
- Graceful error logging with path and method context
- HTTPException with proper WWW-Authenticate header

**Example Usage**:
```bash
curl -H "Authorization: Bearer user123" http://localhost:8000/api/user123/chat
```

---

### T012 - Authorization Dependency
**File**: `backend/src/middleware/auth.py`

Creates FastAPI dependency for protected endpoints:

```python
async def get_current_user(request: Request) -> str:
    """Returns authenticated user_id or raises 401"""
```

**Usage in Endpoints**:
```python
@app.get("/protected")
async def protected_route(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
```

**Key Features**:
- Validates `request.state.user_id` exists
- Raises HTTPException 401 if missing
- Provides clean abstraction for endpoint protection

---

### T013 - Error Handling Middleware
**File**: `backend/src/middleware/errors.py`

Global exception handler that:
- Catches all unhandled exceptions
- Logs with context: user_id, endpoint, method, exception type
- Returns structured JSON errors with request_id
- Maps database errors to user-friendly messages
- Never exposes stack traces to clients

**Error Mapping**:
- `IntegrityError` → 400 Bad Request (constraint violation)
- `OperationalError` → 503 Service Unavailable (DB connection failed)
- Other exceptions → 500 Internal Server Error

**Response Format**:
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred. Our team has been notified.",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Key Features**:
- Full context logging (user_id, path, method)
- Database error detection and mapping
- Request ID propagation for tracing
- No sensitive information exposed

---

### T014 - Request/Response Logging Middleware
**File**: `backend/src/middleware/logging_middleware.py`

Structured logging middleware that:
- Generates unique UUID `request_id` for each request
- Logs incoming requests: method, path, user_id, query params
- Measures request latency in milliseconds
- Logs outgoing responses: status_code, latency_ms
- Adds `X-Request-ID` header to all responses

**Logged Events**:
```json
{
  "event": "Incoming request",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/user123/chat",
  "user_id": "user123",
  "query": "conversation_id=1"
}
```

```json
{
  "event": "Outgoing response",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/user123/chat",
  "user_id": "user123",
  "status_code": 200,
  "latency_ms": 245
}
```

**Key Features**:
- UUID-based request tracing
- Latency measurement in milliseconds
- Exception tracking with latency
- Response header propagation
- User context in all logs

---

## Middleware Registration Order

**File**: `backend/src/main.py`

Middleware is registered in the following order (innermost first):

1. **Error Handling** (catches all exceptions)
2. **Authentication** (validates user and attaches to state)
3. **Request/Response Logging** (generates request_id, logs timing)

```python
app.middleware("http")(error_handling_middleware)
app.middleware("http")(auth_middleware)
app.middleware("http")(logging_middleware)
```

**Execution Flow** (request → response):
```
Request →
  [Logging: generate request_id] →
  [Auth: validate user_id] →
  [Error: ready to catch exceptions] →
  [Endpoint Logic] →
  [Error handler (if exception)] →
  [Logging: log response + latency] →
Response
```

---

## Configuration

### Environment Variables
No new environment variables required. Uses existing:
- `LOG_LEVEL` - Controls logging verbosity

### Headers

**Request Headers**:
```
Authorization: Bearer <user_id>
```

**Response Headers**:
```
X-Request-ID: <uuid>
WWW-Authenticate: Bearer (on 401 responses)
```

---

## Testing

### Test File
**Location**: `backend/src/tests/test_auth_middleware.py`

**Test Coverage**:

1. **User ID Validation**
   - Valid: `user123`, `user_123`, `user-id`, `user.id`
   - Invalid: `user@domain.com`, `user#123`, empty string, too long

2. **Auth Middleware**
   - Public endpoints accessible without auth
   - Protected endpoints blocked without auth
   - Valid Bearer token grants access
   - Invalid formats rejected (missing bearer, extra parts)
   - User ID format validation
   - Request ID in response headers

3. **Error Handling**
   - Error responses include required structure
   - Request ID present in all responses

**Running Tests**:
```bash
cd backend
pytest src/tests/test_auth_middleware.py -v

# Run with coverage
pytest src/tests/test_auth_middleware.py --cov=src/middleware
```

---

## Security Considerations

1. **User ID Validation**
   - Pattern-based validation prevents injection attacks
   - Length limit (255 chars) prevents DoS

2. **Authorization**
   - All protected endpoints validate user_id dependency
   - User_id must be authenticated via middleware

3. **Error Information**
   - Stack traces never exposed to clients
   - Database errors mapped to generic messages
   - Sensitive info not logged in error responses

4. **Request Tracing**
   - Unique request_id enables audit trail
   - All logs include user_id for accountability

---

## Phase 3 Gate - Verification Checklist

- [x] Authentication middleware extracts user_id from Authorization header
- [x] Missing/invalid auth returns 401 with structured error
- [x] Valid auth passes through to endpoint with user_id available
- [x] get_current_user() dependency works in protected endpoints
- [x] Error middleware catches exceptions globally
- [x] Database errors mapped to user-friendly messages
- [x] No stack traces exposed to clients
- [x] Logging middleware generates request_id
- [x] Request/response logged with latency
- [x] All middleware registered in main.py
- [x] Structured JSON logging outputs all context
- [x] X-Request-ID header in all responses

**Gate Status**: ✅ **PASSED**

---

## Usage Examples

### Example 1: Calling Protected Endpoint

```bash
# Without auth - returns 401
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task"}'

# Response:
# HTTP 401
# {"detail":"Unauthorized"}

# With auth - succeeds
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer user123" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task"}'

# Response:
# HTTP 200
# {"conversation_id": 1, "response": "...", "tool_calls": [...]}
```

### Example 2: Viewing Structured Logs

```
{"event":"Incoming request","request_id":"550e8400-e29b-41d4-a716-446655440000","method":"POST","path":"/api/user123/chat","user_id":"user123","timestamp":"2025-01-20T10:30:45.123456Z"}
{"event":"Outgoing response","request_id":"550e8400-e29b-41d4-a716-446655440000","method":"POST","path":"/api/user123/chat","user_id":"user123","status_code":200,"latency_ms":245,"timestamp":"2025-01-20T10:30:45.368456Z"}
```

---

## Integration with Later Phases

### Phase 4: MCP Tools
- All MCP tools receive user_id via dependency injection
- Tools validate user_id for multi-tenancy

### Phase 5: Agent & History
- Agent receives user_id from request context
- Conversation history filtered by user_id

### Phase 6: Chat Endpoint
- Chat endpoint uses `get_current_user()` dependency
- Request/response logged with full context

### Phase 7: Frontend
- Frontend sends Authorization header
- Receives X-Request-ID in response headers
- Can use request_id for error tracking

---

## Files Created/Modified

### Created Files:
- `backend/src/middleware/auth.py` (T011, T012)
- `backend/src/middleware/errors.py` (T013)
- `backend/src/middleware/logging_middleware.py` (T014)
- `backend/src/tests/test_auth_middleware.py` (Tests)

### Modified Files:
- `backend/src/main.py` (Added middleware registration)
- `specs/1-chatbot-ai/tasks.md` (Marked T011-T014 complete)

---

## Next Phase: Phase 4 - MCP Server & Tools

**Prerequisites Satisfied**:
- ✅ Authentication & authorization framework complete
- ✅ Error handling middleware in place
- ✅ Request tracing infrastructure ready
- ✅ User context available in all requests

**Ready to Start**: T015 - Create MCP server foundation

---

## Troubleshooting

### Issue: "Unauthorized" for valid auth header
- Check Authorization header format: `Bearer <user_id>`
- Verify user_id matches pattern: `^[a-zA-Z0-9._-]+$`
- Check logs for validation error details

### Issue: Missing X-Request-ID header
- Verify logging_middleware is registered
- Check middleware registration order
- Ensure no middleware short-circuits request

### Issue: No structured logs
- Check `LOG_LEVEL` environment variable
- Verify structlog is properly configured
- Check stdout/stderr for log output

### Issue: Database errors not mapped
- Check IntegrityError/OperationalError are imported correctly
- Verify database middleware catch clause
- Check logs for exception type

---

## Documentation References

- **Authentication**: See `backend/src/middleware/auth.py`
- **Error Handling**: See `backend/src/middleware/errors.py`
- **Logging**: See `backend/src/middleware/logging_middleware.py`
- **Main App**: See `backend/src/main.py`
- **Tests**: See `backend/src/tests/test_auth_middleware.py`

---

**Implementation Date**: 2025-01-20  
**Status**: ✅ Complete - Ready for Phase 4
