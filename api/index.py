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
    from mangum import Mangum  # type: ignore
    from app.main import app  # type: ignore
    
    # Create Mangum handler for Vercel
    # Mangum converts ASGI (FastAPI) to AWS Lambda/API Gateway format
    # Vercel's Python runtime uses AWS Lambda-compatible format
    mangum_handler = Mangum(app, lifespan="off")
    
    # Wrap handler to ensure proper error handling
    def handler(event, context):
        try:
            return mangum_handler(event, context)
        except Exception as e:
            import json
            import traceback
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': f'Handler error: {str(e)}',
                    'traceback': traceback.format_exc()
                })
            }
except Exception as e:
    # If there's an import error, create a simple error handler
    import json
    import traceback
    def handler(event, context):
        error_details = {
            'error': f'Import error: {str(e)}',
            'traceback': traceback.format_exc()
        }
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(error_details)
        }

