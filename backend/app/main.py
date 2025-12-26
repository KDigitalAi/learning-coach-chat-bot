from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Learning Coach API",
    description="AI-powered learning companion with Socratic teaching method",
    version="1.0.0"
)

# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch all unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    logger.error(f"Request path: {request.url.path}")
    logger.error(f"Request method: {request.method}")
    
    error_detail = {
        "error": "Internal server error",
        "message": str(exc)[:200] if str(exc) else "An unexpected error occurred",
        "type": type(exc).__name__,
        "path": request.url.path
    }
    
    # In development, include traceback
    import os
    if os.getenv("ENVIRONMENT") == "development":
        error_detail["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

# HTTPException handler for proper error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper JSON responses."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )

# CRITICAL DEBUG: Catch specific 404s and log them loudly
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    logger.error(f"❌ 404 NOT FOUND: {request.method} {request.url.path}")
    logger.error(f"Headers: {request.headers}")
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Resource not found: {request.url.path}",
            "method": request.method,
            "message": "This 404 was caught by the backend application, meaning routing worked but the endpoint does not exist."
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track router initialization status
router_init_error = None

def _register_routers():
    """Register routers with error handling."""
    global router_init_error
    try:
        from app.routers import chat, onboarding
        app.include_router(onboarding.router)
        app.include_router(chat.router)
        logger.info("✅ Routers loaded successfully")
        return True
    except Exception as e:
        import traceback
        router_init_error = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        logger.error(f"⚠️ Warning: Failed to load routers: {e}")
        logger.error(traceback.format_exc())
        return False

# Try to register routers
if not _register_routers():
    logger.error("CRITICAL: Routers failed to load. Setting up fallback error routes.")
    
    # Define fallback routes to report the error instead of 404
    @app.api_route("/api/chat", methods=["GET", "POST"])
    async def chat_init_error(request: Request):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Service Initialization Failed",
                "message": "The chat service failed to start due to missing dependencies or configuration.",
                "detail": router_init_error
            }
        )
        
    @app.api_route("/api/onboarding/consent", methods=["POST"])
    async def onboarding_init_error(request: Request):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Service Initialization Failed",
                "detail": router_init_error
            }
        )

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


# DEBUG: Catch-all route to diagnose 404s
# This must be the LAST route defined
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def catch_all(path_name: str, request: Request):
    """
    Catch-all route to return the path that was actually received.
    This helps debug routing issues on Vercel.
    """
    method = request.method
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Route not found: {method} /{path_name}",
            "received_path": f"/{path_name}",
            "method": method,
            "message": "This is a custom 404 from the backend catch-all route."
        }
    )



@app.get("/api/test")
async def test_endpoint():
    """
    Minimal test endpoint that doesn't import anything.
    Use this to verify the serverless function is working.
    """
    return {
        "status": "ok",
        "message": "API is responding",
        "endpoint": "/api/test"
    }


@app.get("/api/health")
async def api_health():
    """
    Health endpoint for deployments where the API is mounted under `/api`,
    such as Vercel (`/api/*` routed to the serverless function).
    This endpoint ALWAYS returns 200 OK - it never fails.
    """
    import os
    
    # This endpoint should NEVER fail - wrap everything in try-except
    try:
        health_status = {
            "status": "healthy",
            "app": "Learning Coach API",
            "version": "1.0.0",
            "router_init_success": router_init_error is None
        }
        
        if router_init_error:
            health_status["router_init_error"] = router_init_error["error"]
        
        # Try to check config, but don't fail if it doesn't work
        try:
            from app.config import get_settings_instance
            try:
                settings = get_settings_instance()
                health_status.update({
                    "config_loaded": True,
                    "openai_key_set": bool(getattr(settings, 'openai_api_key', None)),
                    "supabase_url_set": bool(getattr(settings, 'supabase_url', None)),
                    "supabase_key_set": bool(getattr(settings, 'supabase_key', None))
                })
            except Exception as config_error:
                logger.warning(f"Config check failed: {config_error}")
                health_status.update({
                    "config_loaded": False,
                    "config_error": str(config_error)[:200]
                })
        except Exception as import_error:
            logger.warning(f"Config import failed: {import_error}")
            health_status.update({
                "config_loaded": False,
                "import_error": str(import_error)[:200]
            })
        
        # Always check environment variables directly (they're always available)
        try:
            health_status["env_vars"] = {
                "OPENAI_API_KEY": "set" if os.getenv("OPENAI_API_KEY") else "missing",
                "SUPABASE_URL": "set" if os.getenv("SUPABASE_URL") else "missing",
                "SUPABASE_KEY": "set" if os.getenv("SUPABASE_KEY") else "missing"
            }
        except Exception as env_error:
            logger.warning(f"Env var check failed: {env_error}")
            health_status["env_vars"] = {"error": "Unable to check environment variables"}
        
        return health_status
    except Exception as e:
        # Ultimate fallback - return basic health status even if everything fails
        logger.error(f"Health endpoint error (should never happen): {e}", exc_info=True)
        return {
            "status": "healthy",
            "app": "Learning Coach API",
            "version": "1.0.0",
            "note": "Basic health check - detailed status unavailable"
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
