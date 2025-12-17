from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

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

# Include routers with error handling
# This allows the app to start even if routers fail to import
try:
    from app.routers import chat, onboarding
    app.include_router(onboarding.router)
    app.include_router(chat.router)
    logger.info("✅ Routers loaded successfully")
except Exception as e:
    logger.error(f"⚠️ Warning: Failed to load routers: {e}")
    logger.error("The app will start but API endpoints may not work.")
    # Create a simple error router for missing endpoints
    from fastapi import APIRouter, HTTPException
    
    error_router = APIRouter()
    
    @error_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def router_error(path: str):
        raise HTTPException(
            status_code=500,
            detail=f"Router initialization failed. Check logs for details. Original error: {str(e)}"
        )
    
    app.include_router(error_router, prefix="/api")


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
    This endpoint works even if settings fail to load.
    """
    try:
        # Try to check if settings are available (but don't fail if they're not)
        from app.config import get_settings_instance
        try:
            settings = get_settings_instance()
            return {
                "status": "healthy",
                "config_loaded": True,
                "openai_key_set": bool(settings.openai_api_key),
                "supabase_url_set": bool(settings.supabase_url),
                "supabase_key_set": bool(settings.supabase_key)
            }
        except Exception as config_error:
            return {
                "status": "healthy",
                "config_loaded": False,
                "config_error": str(config_error)[:200]  # Truncate long errors
            }
    except Exception as e:
        # Even if config import fails, return healthy status
        return {
            "status": "healthy",
            "config_loaded": False,
            "error": str(e)[:200]
        }


@app.get("/api/debug/config")
async def debug_config():
    """
    Debug endpoint to check configuration status.
    Returns configuration status without exposing sensitive values.
    """
    import os
    
    try:
        from app.config import get_settings_instance
        settings = get_settings_instance()
        
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
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "env_vars": {
                "OPENAI_API_KEY": "set" if os.getenv("OPENAI_API_KEY") else "missing",
                "SUPABASE_URL": "set" if os.getenv("SUPABASE_URL") else "missing",
                "SUPABASE_KEY": "set" if os.getenv("SUPABASE_KEY") else "missing",
            }
        }

#404 Fixed for Vercel deployment
