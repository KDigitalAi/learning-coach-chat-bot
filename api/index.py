"""
Vercel FastAPI entry point.
This file simply exports the FastAPI app instance.
Vercel's Python runtime automatically handles ASGI routing.
"""
import sys
from pathlib import Path

# Add backend to Python path so we can import the app
backend_path = str(Path(__file__).parent.parent / "backend")
sys.path.insert(0, backend_path)

# Import the FastAPI app from the backend
# Vercel looks for an 'app' variable that is a WSGI/ASGI application
from app.main import app

# That's it! Vercel handles the rest.
# No Mangum, no handler function needed - Vercel's Python runtime
# natively supports FastAPI/ASGI applications.
