"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.
"""
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

try:
    from mangum import Mangum
    from app.main import app
    
    # Create Mangum handler for Vercel
    # Mangum converts ASGI (FastAPI) to AWS Lambda/API Gateway format
    # Vercel's Python runtime uses AWS Lambda-compatible format
    handler = Mangum(app, lifespan="off")
except Exception as e:
    # Fallback error handler if imports fail
    import json
    
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Server initialization error', 'message': str(e)})
        }
