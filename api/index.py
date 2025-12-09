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

try:
    # Import FastAPI app
    # The import should work now with backend in sys.path
    # Note: app.main is resolved at runtime after adding backend to sys.path
    from app.main import app  # type: ignore[import-untyped]
    
    # Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
    # lifespan="off" disables lifespan events which aren't supported in serverless
    handler = Mangum(app, lifespan="off")
    
except ImportError as e:
    # More detailed error for import issues
    import logging
    logging.error(f"Import Error - Failed to import FastAPI app")
    logging.error(f"Current sys.path: {sys.path}")
    logging.error(f"Backend path attempted: {backend_path}")
    logging.error(f"Backend path exists: {os.path.exists(backend_path)}")
    logging.error(f"Error details: {str(e)}")
    raise
except Exception as e:
    # General error handling
    import logging
    logging.error(f"Failed to initialize FastAPI app: {str(e)}")
    logging.error(f"Error type: {type(e).__name__}")
    import traceback
    logging.error(traceback.format_exc())
    raise

