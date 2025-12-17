from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, onboarding


app = FastAPI(
    title="Learning Coach API",
    description="AI-powered learning companion with Socratic teaching method",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(onboarding.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "message": "Learning Coach API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """
    Legacy health endpoint for local development.
    Kept for backward compatibility.
    """
    return {"status": "healthy"}


@app.get("/api/health")
async def api_health():
    """
    Health endpoint for deployments where the API is mounted under `/api`,
    such as Vercel (`/api/*` routed to the serverless function).
    """
    return {"status": "healthy"}


@app.get("/api/debug/config")
async def debug_config():
    """
    Debug endpoint to check configuration status.
    Returns configuration status without exposing sensitive values.
    """
    import os
    from app.config import settings
    
    config_status = {
        "status": "ok",
        "openai_api_key_set": bool(settings.openai_api_key),
        "openai_api_key_length": len(settings.openai_api_key) if settings.openai_api_key else 0,
        "supabase_url_set": bool(settings.supabase_url),
        "supabase_key_set": bool(settings.supabase_key),
        "router_model": settings.router_model,
        "speed_model": settings.speed_model,
        "quality_model": settings.quality_model,
        "env_vars": {
            "OPENAI_API_KEY": "set" if os.getenv("OPENAI_API_KEY") else "missing",
            "SUPABASE_URL": "set" if os.getenv("SUPABASE_URL") else "missing",
            "SUPABASE_KEY": "set" if os.getenv("SUPABASE_KEY") else "missing",
        }
    }
    
    # Check for issues
    issues = []
    if not settings.openai_api_key:
        issues.append("OPENAI_API_KEY is missing")
    if not settings.supabase_url:
        issues.append("SUPABASE_URL is missing")
    if not settings.supabase_key:
        issues.append("SUPABASE_KEY is missing")
    
    if issues:
        config_status["status"] = "error"
        config_status["issues"] = issues
    
    return config_status

#404 Fixed for Vercel deployment
