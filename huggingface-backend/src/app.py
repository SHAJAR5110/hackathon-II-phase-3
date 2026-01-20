"""
FastAPI Main Application
Phase II - Todo Full-Stack Web Application

Entry point for the FastAPI backend.
Configures CORS, middleware, error handlers, and routes.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="Full-stack todo application with JWT authentication and user isolation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
# Allow requests from frontend during development
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with consistent JSON response format.
    Returns proper status codes for 400, 401, 403, 404, 500 errors.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    Returns 400 Bad Request with detailed error messages.
    """
    errors = exc.errors()
    error_messages = []

    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "; ".join(error_messages),
            "status": 400
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected errors.
    Returns 500 Internal Server Error without exposing sensitive details.
    """
    # Log the full exception for debugging (in production, use proper logging)
    print(f"Unexpected error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "status": 500
        }
    )


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    Returns 200 OK with status message.
    """
    return {
        "status": "healthy",
        "message": "Todo API is running"
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Todo API - Phase II Full-Stack Application",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Register routes
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router
from routes.users import router as users_router

app.include_router(tasks_router)
app.include_router(auth_router)
app.include_router(users_router)


# Application Lifecycle Events
@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on application startup.
    Creates tables if they don't exist.
    """
    from db import init_db

    print("[STARTUP] Starting Todo API...")
    await init_db()
    print("[STARTUP] Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Close database connections on application shutdown.
    """
    from db import close_db

    print("[SHUTDOWN] Shutting down Todo API...")
    await close_db()
    print("[SHUTDOWN] Database connections closed")
