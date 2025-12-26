"""
Vercel serverless function handler - Single entry point for all /api/* routes.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.

This file must be in the api/ directory for Vercel to recognize it as a serverless function.
"""
import sys
import os
import json
import logging
import asyncio
from pathlib import Path

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
    This is called for all requests matching /api/* routes.
    Mangum handles the conversion from Lambda event to FastAPI request.
    """
    try:
        # Log the incoming request for debugging
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        path = event.get('path', event.get('rawPath', ''))
        log.info(f"📥 Incoming request: {method} {path}")
        
        # Call Mangum handler - it handles ASGI conversion and routing
        # Mangum automatically converts the Lambda event to FastAPI request
        response = handler_instance(event, context)
        
        # Mangum returns a coroutine for async handlers, so we need to await it
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)
        
        # Log response status
        status_code = response.get('statusCode', 500) if isinstance(response, dict) else 500
        log.info(f"📤 Response: {status_code} for {method} {path}")
        
        # Ensure CORS headers are present (FastAPI CORS middleware should handle this, but add as backup)
        if isinstance(response, dict) and 'headers' in response:
            headers = response['headers']
            # Only add CORS headers if they're not already set by FastAPI
            if 'Access-Control-Allow-Origin' not in headers:
                headers['Access-Control-Allow-Origin'] = '*'
            if 'Access-Control-Allow-Methods' not in headers:
                headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
            if 'Access-Control-Allow-Headers' not in headers:
                headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        return response
        
    except Exception as e:
        log.error(f"❌ Handler error: {e}", exc_info=True)
        import traceback
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

