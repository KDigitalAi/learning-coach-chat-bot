"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.
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

# Initialize handler - must be at module level for Vercel
def create_handler():
    """Create the handler function for Vercel."""
    try:
        from mangum import Mangum  # type: ignore
        from app.main import app  # type: ignore
        
        # Create Mangum handler for Vercel
        # Mangum converts ASGI (FastAPI) to AWS Lambda/API Gateway format
        # Vercel's Python runtime uses AWS Lambda-compatible format
        handler_instance = Mangum(app, lifespan="off")
        
        # Wrap handler to ensure proper error handling
        def wrapped_handler(event, context=None):
            try:
                # Log the event for debugging
                print(f"Handler received event: method={event.get('httpMethod')}, path={event.get('path')}, rawPath={event.get('rawPath')}")
                
                # Call Mangum handler
                response = handler_instance(event, context)
                
                # Mangum should return proper Lambda format, but ensure it's correct
                if isinstance(response, dict) and 'statusCode' in response:
                    return response
                
                # If not in Lambda format, wrap it
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps(response) if not isinstance(response, str) else response
                }
            except Exception as e:
                error_details = {
                    'error': f'Handler error: {str(e)}',
                    'traceback': traceback.format_exc(),
                    'event_method': event.get('httpMethod', 'UNKNOWN'),
                    'event_path': event.get('path', 'UNKNOWN'),
                    'event_rawPath': event.get('rawPath', 'UNKNOWN'),
                    'event_keys': list(event.keys())
                }
                print(f"Handler error: {error_details}")
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps(error_details)
                }
        
        return wrapped_handler
        
    except Exception as e:
        # If there's an import error, create a simple error handler
        def error_handler(event, context=None):
            error_details = {
                'error': f'Import error: {str(e)}',
                'traceback': traceback.format_exc(),
                'backend_path': backend_path,
                'sys_path': sys.path[:3]  # First 3 entries for debugging
            }
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(error_details)
            }
        return error_handler

# Create handler at module level - required for Vercel
handler = create_handler()

# Export handler for Vercel (some configurations require explicit export)
__all__ = ['handler']

