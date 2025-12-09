"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.
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
    # The handler is a callable that receives (event, context) and returns a response
    handler = Mangum(app, lifespan="off")
except Exception as e:
    # If there's an import error, create a simple error handler
    import json
    def error_handler(event, context):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Import error: {str(e)}'})
        }
    handler = error_handler

