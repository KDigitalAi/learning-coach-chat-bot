"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.
"""
import sys
import os
import json
import traceback
from pathlib import Path

# Add backend directory to Python path
current_dir = Path(__file__).parent
backend_path = current_dir.parent / "backend"
backend_path = str(backend_path.resolve())

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Initialize handler - must be at module level for Vercel
def create_handler():
    """Create the handler function for Vercel."""
    try:
        from mangum import Mangum  # type: ignore # Package installed but IDE may not detect it
        
        # Import app with error handling
        try:
            from app.main import app  # type: ignore # Path added dynamically at runtime
        except Exception as import_error:
            # If app import fails, create a minimal error app
            from fastapi import FastAPI, HTTPException
            
            error_app = FastAPI(title="Learning Coach API - Error Mode")
            
            @error_app.get("/{path:path}")
            @error_app.post("/{path:path}")
            @error_app.put("/{path:path}")
            @error_app.delete("/{path:path}")
            async def error_endpoint(path: str):
                raise HTTPException(
                    status_code=500,
                    detail=f"Application failed to initialize. Import error: {str(import_error)[:500]}"
                )
            
            app = error_app
        
        # Create Mangum handler for Vercel
        handler_instance = Mangum(app, lifespan="off")
        
        # Wrap handler to ensure proper error handling
        def wrapped_handler(event, context=None):
            try:
                return handler_instance(event, context)
            except Exception as e:
                error_details = {
                    'error': f'Handler error: {str(e)}',
                    'traceback': traceback.format_exc(),
                    'event_method': event.get('httpMethod', 'UNKNOWN'),
                    'event_path': event.get('path', 'UNKNOWN')
                }
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
                'error': f'Handler creation error: {str(e)}',
                'traceback': traceback.format_exc(),
                'backend_path': backend_path,
                'sys_path': sys.path[:3],
                'python_version': sys.version
            }
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(error_details)
            }
        return error_handler

# Create handler at module level - required for Vercel
# Wrap in try-except to ensure we always have a handler
try:
    handler = create_handler()
except Exception as e:
    # Ultimate fallback - create a handler that always returns error details
    def fallback_handler(event, context=None):
        error_details = {
            'error': f'Critical handler initialization error: {str(e)}',
            'traceback': traceback.format_exc(),
            'backend_path': backend_path,
            'sys_path': sys.path[:3]
        }
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(error_details)
        }
    handler = fallback_handler
