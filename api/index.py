"""
Vercel Serverless Function Wrapper for FastAPI
This file wraps the FastAPI application to work with Vercel's serverless functions.
"""
from mangum import Mangum
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    # Import FastAPI app
    from app.main import app
    
    # Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
    # lifespan="off" disables lifespan events which aren't supported in serverless
    handler = Mangum(app, lifespan="off")
except Exception as e:
    # Error handling for import issues
    import logging
    logging.error(f"Failed to import FastAPI app: {e}")
    raise

