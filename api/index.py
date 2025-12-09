"""
Vercel serverless function handler for FastAPI backend.
This file wraps the FastAPI application to work with Vercel's serverless functions.

Application Details:
- FastAPI app location: backend/app/main.py
- FastAPI app variable name: app
- Application code directory: backend/app/
- API route prefix: /api (routers: /api/chat, /api/onboarding)
- Main routers: chat.py, onboarding.py
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
# This allows importing from the backend/app module
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import Mangum adapter for ASGI (ASGI to AWS Lambda/Vercel adapter)
from mangum import Mangum

# Import FastAPI app from backend/app/main.py
# The app variable is defined in backend/app/main.py
from app.main import app

# Create handler for Vercel
# Mangum wraps the FastAPI ASGI app to work with Vercel's serverless function runtime
# lifespan="off" disables lifespan events (startup/shutdown) which aren't needed in serverless
handler = Mangum(app, lifespan="off")

# Export both handler and app for compatibility
# Vercel Python runtime looks for 'handler' variable
# Some configurations may also check for 'app'
__all__ = ["handler", "app"]

