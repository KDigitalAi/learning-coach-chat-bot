"""
Vercel Serverless Function Wrapper for FastAPI
This file wraps the FastAPI application to work with Vercel's serverless functions.
"""
from mangum import Mangum  # type: ignore[import-untyped]
import sys
import os

# Get the absolute path of the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up from api/ to project root
backend_path = os.path.join(project_root, 'backend')
backend_path = os.path.abspath(backend_path)  # Ensure absolute path

# Add backend directory to Python path
# Vercel sets PYTHONPATH=backend in vercel.json, but we also add it explicitly
if backend_path and os.path.exists(backend_path):
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

# Also check if PYTHONPATH environment variable is set (from vercel.json)
pythonpath = os.environ.get('PYTHONPATH', '')
if pythonpath:
    # PYTHONPATH might be relative, so resolve it
    if not os.path.isabs(pythonpath):
        pythonpath = os.path.join(project_root, pythonpath)
        pythonpath = os.path.abspath(pythonpath)
    
    if pythonpath and os.path.exists(pythonpath) and pythonpath not in sys.path:
        sys.path.insert(0, pythonpath)

# Import FastAPI app
# The import should work now with backend in sys.path
# Note: app.main is resolved at runtime after adding backend to sys.path
# Settings are lazy-loaded, so this import should succeed even if env vars aren't set yet
try:
    from app.main import app  # type: ignore[import-untyped]
    
    # Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
    # lifespan="off" disables lifespan events which aren't supported in serverless
    handler = Mangum(app, lifespan="off")
    
except (ImportError, Exception) as e:
    # Error handling - log but don't fail module import
    # This allows Vercel to validate the function structure
    import logging
    import traceback
    logging.basicConfig(level=logging.ERROR)
    error_msg = (
        f"Failed to initialize FastAPI app\n"
        f"Error type: {type(e).__name__}\n"
        f"Current sys.path: {sys.path}\n"
        f"Backend path attempted: {backend_path}\n"
        f"Backend path exists: {os.path.exists(backend_path)}\n"
        f"PYTHONPATH env: {os.environ.get('PYTHONPATH', 'NOT SET')}\n"
        f"Error details: {str(e)}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    logging.error(error_msg)
    
    # Create a handler that will return an error response
    # This allows Vercel to validate the function even if initialization fails
    def error_handler(event, context):
        import json
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Failed to initialize application",
                "message": str(e),
                "type": type(e).__name__
            })
        }
    handler = error_handler

