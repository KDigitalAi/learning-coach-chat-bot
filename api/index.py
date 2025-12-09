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

# Add backend directory to Python path
# Get the absolute path to ensure it works in Vercel's environment
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, '..', 'backend')
backend_path = os.path.abspath(backend_path)

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from mangum import Mangum
    from app.main import app
    
    # Create Mangum handler for Vercel
    # Mangum converts ASGI (FastAPI) to AWS Lambda/API Gateway format
    # Vercel's Python runtime uses AWS Lambda-compatible format
    # Mangum handles async internally, so the handler can be synchronous
    mangum_handler = Mangum(app, lifespan="off")
    
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
        # Mangum handles the async FastAPI app internally
        # It converts the ASGI app to Lambda-compatible format
        return mangum_handler(event, context)
        
except Exception as e:
    # Fallback error handler if imports fail
    import json
    import traceback
    
    def handler(event, context):
        """Error handler for import failures."""
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        
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

