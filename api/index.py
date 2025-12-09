"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.

According to Vercel docs: https://vercel.com/docs/functions/serverless-functions/runtimes/python
The handler must be a callable that receives (event, context) and returns a response.
"""
import sys
import os

# Add backend directory to Python path
# Get the absolute path to ensure it works in Vercel's environment
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, '..', 'backend')
backend_path = os.path.abspath(backend_path)

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from mangum import Mangum
from app.main import app

# Create Mangum handler for Vercel
# Mangum converts ASGI (FastAPI) to AWS Lambda/API Gateway format
# Vercel's Python runtime uses AWS Lambda-compatible format
# The handler is a callable that receives (event, context) and returns a response
mangum_handler = Mangum(app, lifespan="off")

# Export handler function for Vercel
# Vercel expects a function named 'handler' that it can call
def handler(event, context):
    """
    Vercel serverless function handler.
    This function is called by Vercel for each request to /api/* routes.
    
    Args:
        event: AWS Lambda event object (contains request data)
        context: AWS Lambda context object
    
    Returns:
        Response dictionary with statusCode, headers, and body
    """
    return mangum_handler(event, context)

