"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.

According to Vercel docs: https://vercel.com/docs/functions/serverless-functions/runtimes/python
The handler must be a callable that receives (event, context) and returns a response.

Vercel Python functions work like AWS Lambda - they receive events and return responses.
Mangum handles the ASGI-to-Lambda conversion automatically.
"""
import sys
import os
import json
import traceback

# Add backend directory to Python path
# Get the absolute path to ensure it works in Vercel's environment
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, '..', 'backend')
backend_path = os.path.abspath(backend_path)

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Initialize handler variable
mangum_handler = None
init_error = None

try:
    from mangum import Mangum
    from app.main import app
    
    # Create Mangum handler for Vercel
    # Mangum converts ASGI (FastAPI) to AWS Lambda/API Gateway format
    # Vercel's Python runtime uses AWS Lambda-compatible format
    # Mangum handles async internally, so the handler can be synchronous
    mangum_handler = Mangum(app, lifespan="off")
    
except Exception as e:
    # Store error for later use
    init_error = e
    mangum_handler = None

# Export handler function for Vercel
# Vercel expects a function named 'handler' at module level
# The handler receives (event, context) and returns a response dict
def handler(event, context):
    """
    Vercel serverless function handler.
    This function is called by Vercel for each request to /api/* routes.
    
    Args:
        event: AWS Lambda event object (contains request data)
              - event['path']: The request path (e.g., '/api/chat')
              - event['httpMethod']: HTTP method (e.g., 'POST')
              - event['headers']: Request headers
              - event['body']: Request body (string)
        context: AWS Lambda context object
    
    Returns:
        Response dictionary with:
        - statusCode: HTTP status code (e.g., 200)
        - headers: Response headers dict
        - body: Response body (string)
    """
    # Check if handler was initialized successfully
    if mangum_handler is None:
        # Return error response if initialization failed
        error_msg = str(init_error) if init_error else "Unknown initialization error"
        traceback_str = traceback.format_exc() if init_error else ""
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Server initialization error',
                'message': error_msg,
                'traceback': traceback_str
            })
        }
    
    # Mangum handles the async FastAPI app internally
    # It converts the ASGI app to Lambda-compatible format
    try:
        return mangum_handler(event, context)
    except Exception as e:
        # Handle runtime errors
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Runtime error',
                'message': str(e),
                'traceback': traceback.format_exc()
            })
        }

