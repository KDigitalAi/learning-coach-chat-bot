"""
Vercel serverless function handler - Single entry point for all /api/* routes.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.

This file must be in the api/ directory for Vercel to recognize it as a serverless function.
Vercel routes all /api/* requests to this handler via rewrites.
"""
import sys
import os
import json
import logging
import asyncio
from pathlib import Path
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Add backend directory to Python path so we can import app.main
current_dir = Path(__file__).parent
backend_path = current_dir.parent / "backend"
backend_path = str(backend_path.resolve())

# Add backend to Python path - critical for Vercel file structure
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
    log.info(f"✅ Added {backend_path} to Python path")

# Import FastAPI app and Mangum
try:
    from mangum import Mangum
    from app.main import app
    
    # Create Mangum handler - this adapts FastAPI (ASGI) to Vercel's Lambda format
    # lifespan="off" because Vercel doesn't support ASGI lifespan events
    handler_instance = Mangum(app, lifespan="off")
    log.info("✅ FastAPI app and Mangum handler initialized successfully")
    
    # Log environment variable status (for debugging, doesn't expose values)
    log.info(f"🔑 Environment Check: OPENAI_API_KEY={'SET' if os.environ.get('OPENAI_API_KEY') else 'MISSING'}")
    log.info(f"🔑 Environment Check: SUPABASE_URL={'SET' if os.environ.get('SUPABASE_URL') else 'MISSING'}")
    log.info(f"🔑 Environment Check: SUPABASE_KEY={'SET' if os.environ.get('SUPABASE_KEY') else 'MISSING'}")
    
except Exception as e:
    log.error(f"❌ Failed to initialize FastAPI app: {e}", exc_info=True)
    import traceback
    
    # Create error handler that returns 500 if initialization fails
    def error_handler(event, context=None):
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to initialize FastAPI application',
                'message': str(e)[:200],
                'type': type(e).__name__
            })
        }
    handler_instance = error_handler

# Vercel serverless function handler
def handler(event, context=None):
    """
    Vercel serverless function handler.
    This is called for all requests matching /api/* routes via rewrite.
    
    When Vercel rewrites /api/health to /api/index, the original path
    is preserved in the event, and Mangum passes it correctly to FastAPI.
    """
    try:
        # Extract method
        method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        # Get headers (convert to lowercase keys if needed for consistency)
        headers = event.get('headers', {}) or {}
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # Extract the original request path
        # Vercel preserves the original path in the event when using rewrites
        original_path = (
            # Try Vercel-specific headers first
            headers_lower.get('x-vercel-rewrite-path') or
            headers_lower.get('x-vercel-forwarded-path') or
            headers_lower.get('x-forwarded-path') or
            # Check event path (Vercel usually preserves original path here)
            event.get('path') or
            event.get('rawPath') or
            # Last resort
            '/api/'
        )
        
        # If path contains the handler filename, we need to extract original
        if 'index' in original_path.lower() or original_path.endswith('.py'):
            # Try to get from forwarded URL
            forwarded_url = headers_lower.get('x-forwarded-url') or headers_lower.get('x-forwarded-uri')
            if forwarded_url:
                try:
                    parsed = urlparse(forwarded_url)
                    original_path = parsed.path or '/api/'
                except:
                    pass
            
            # If still not found, check query string
            if 'index' in original_path.lower() or original_path.endswith('.py'):
                query = event.get('queryStringParameters') or {}
                if query.get('path'):
                    original_path = query['path']
                else:
                    # Default to /api/ if we can't determine
                    original_path = '/api/'
        
        # Ensure path starts with /api (for FastAPI routes)
        if not original_path.startswith('/api'):
            if original_path.startswith('/'):
                original_path = '/api' + original_path
            else:
                original_path = '/api/' + original_path
        
        # Update event with the correct path for Mangum
        event['path'] = original_path
        if 'rawPath' in event:
            event['rawPath'] = original_path
        
        log.info(f"📥 Request: {method} {original_path}")
        log.debug(f"🔍 Event keys: {list(event.keys())}")
        log.debug(f"🔍 Headers keys: {list(headers.keys())[:10]}")
        
        # Call Mangum handler - it handles ASGI conversion and routing
        # Mangum converts the Lambda event to FastAPI request with the correct path
        response = handler_instance(event, context)
        
        # Mangum returns a coroutine for async handlers, so we need to await it
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)
        
        # Log response status
        status_code = response.get('statusCode', 500) if isinstance(response, dict) else 500
        log.info(f"📤 Response: {status_code} for {method} {original_path}")
        
        # Ensure CORS headers are present (FastAPI CORS middleware should handle this, but add as backup)
        if isinstance(response, dict) and 'headers' in response:
            response_headers = response['headers']
            # Only add CORS headers if they're not already set by FastAPI
            if 'Access-Control-Allow-Origin' not in response_headers:
                response_headers['Access-Control-Allow-Origin'] = '*'
            if 'Access-Control-Allow-Methods' not in response_headers:
                response_headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
            if 'Access-Control-Allow-Headers' not in response_headers:
                response_headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        return response
        
    except Exception as e:
        log.error(f"❌ Handler error: {e}", exc_info=True)
        import traceback
        log.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error (Handler Crash)',
                'message': str(e)[:200],
                'type': type(e).__name__,
                'path': event.get('path', 'unknown')
            })
        }
