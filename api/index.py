"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.
"""
import sys
import os
import json
import traceback
import logging
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Add backend directory to Python path
current_dir = Path(__file__).parent
backend_path = current_dir.parent / "backend"
backend_path = str(backend_path.resolve())

log.info(f"Current directory: {current_dir}")
log.info(f"Backend path: {backend_path}")

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
    log.info(f"Added {backend_path} to Python path")
else:
    log.info(f"{backend_path} already in Python path")

log.info(f"Python path: {sys.path[:3]}")

# Initialize handler - must be at module level for Vercel
def create_handler():
    """Create the handler function for Vercel."""
    import logging
    log = logging.getLogger(__name__)
    log.info("Creating Vercel handler...")
    
    try:
        log.info("Importing Mangum...")
        from mangum import Mangum  # type: ignore # Package installed but IDE may not detect it
        log.info("Mangum imported successfully")
        
        # Import app with error handling
        try:
            log.info("Importing FastAPI app...")
            from app.main import app  # type: ignore # Path added dynamically at runtime
            log.info("FastAPI app imported successfully")
        except Exception as import_error:
            log.error(f"Failed to import app: {import_error}", exc_info=True)
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
            log.warning("Using error app due to import failure")
        
        # Create Mangum handler for Vercel
        log.info("Creating Mangum handler instance...")
        handler_instance = Mangum(app, lifespan="off")
        log.info("Mangum handler created successfully")
        
        # Wrap handler to ensure proper error handling
        def wrapped_handler(event, context=None):
            try:
                # Log the incoming event for debugging
                log.info(f"=== Handler called ===")
                log.info(f"Event type: {type(event)}")
                
                # Handle Vercel's event format
                # Vercel may pass the event in different formats
                if not isinstance(event, dict):
                    log.error(f"Event is not a dict: {type(event)}")
                    return {
                        'statusCode': 500,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'error': 'Invalid event format',
                            'event_type': str(type(event))
                        })
                    }
                
                log.info(f"Event keys: {list(event.keys())}")
                
                # Log path information for debugging
                original_path = event.get('path', '')
                log.info(f"Original path from Vercel: {original_path}")
                
                # Vercel routing: /api/* -> api/index.py
                # The path in event should be the full path including /api/
                # FastAPI routes are defined with /api/ prefix, so path should match
                # DO NOT modify the path - let Mangum handle routing as-is
                
                # Also handle queryStringParameters
                if 'queryStringParameters' in event and event['queryStringParameters']:
                    log.info(f"Query params: {event['queryStringParameters']}")
                
                # Call Mangum handler - it should handle the event conversion
                log.info(f"Calling Mangum handler with path: {event.get('path')}")
                response = handler_instance(event, context)
                log.info(f"Mangum returned response type: {type(response)}")
                
                # Ensure response is in correct format
                if isinstance(response, dict):
                    # Mangum returns dict with statusCode, headers, body
                    if 'statusCode' not in response:
                        log.error(f"Invalid response format from Mangum: {response}")
                        return {
                            'statusCode': 500,
                            'headers': {'Content-Type': 'application/json'},
                            'body': json.dumps({
                                'error': 'Invalid response format from handler',
                                'response': str(response)[:500]
                            })
                        }
                    log.info(f"Response status: {response.get('statusCode')}")
                    return response
                elif hasattr(response, 'status_code'):
                    # FastAPI Response object
                    log.info("Converting FastAPI Response to Vercel format")
                    return {
                        'statusCode': response.status_code,
                        'headers': dict(response.headers),
                        'body': response.body.decode() if hasattr(response, 'body') else ''
                    }
                else:
                    log.error(f"Unexpected response type: {type(response)}")
                    return {
                        'statusCode': 500,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'error': 'Unexpected response type from handler',
                            'type': str(type(response))
                        })
                    }
                    
            except Exception as e:
                log.error(f"Handler error: {e}", exc_info=True)
                error_details = {
                    'error': f'Handler error: {str(e)}',
                    'type': type(e).__name__,
                    'traceback': traceback.format_exc(),
                    'event_method': event.get('httpMethod', 'UNKNOWN') if isinstance(event, dict) else 'N/A',
                    'event_path': event.get('path', 'UNKNOWN') if isinstance(event, dict) else 'N/A',
                    'event_keys': list(event.keys()) if isinstance(event, dict) else 'not a dict'
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
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

try:
    log.info("Initializing handler...")
    handler = create_handler()
    log.info("Handler initialized successfully")
except Exception as e:
    log.error(f"Critical handler initialization error: {e}", exc_info=True)
    # Ultimate fallback - create a handler that always returns error details
    def fallback_handler(event, context=None):
        error_details = {
            'error': f'Critical handler initialization error: {str(e)}',
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
    handler = fallback_handler
    log.warning("Using fallback handler due to initialization failure")
