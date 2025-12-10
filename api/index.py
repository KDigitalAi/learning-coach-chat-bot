"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.
"""
import sys
import os
import json
import traceback

# Add backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, '..', 'backend')
backend_path = os.path.abspath(backend_path)

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import and create handler at module level
try:
    from mangum import Mangum
    from app.main import app
    
    # Create Mangum handler - this is what Vercel will call
    handler = Mangum(app, lifespan="off")
    
except Exception as e:
    # If import fails, create error handler
    def handler(event, context=None):
        error_details = {
            'error': f'Import error: {str(e)}',
            'traceback': traceback.format_exc(),
            'backend_path': backend_path,
            'sys_path': sys.path[:3]
        }
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(error_details)
        }
