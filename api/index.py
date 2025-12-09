"""
Vercel serverless function handler for FastAPI backend.
This file wraps the FastAPI application to work with Vercel's serverless functions.
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import Mangum adapter for ASGI
from mangum import Mangum

# Import FastAPI app
from app.main import app

# Create handler for Vercel
# Vercel Python runtime looks for 'handler' variable
handler = Mangum(app, lifespan="off")

# Also export app for Vercel's FastAPI auto-detection (if needed)
# This ensures compatibility with both approaches
__all__ = ["handler", "app"]

