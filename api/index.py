"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.

This is the entry point for all /api/* routes on Vercel.
"""
import sys
import os
import json
import traceback
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

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
    log.info(f"Added {backend_path} to Python path")

# Import FastAPI app and Mangum
try:
    from mangum import Mangum
    from app.main import app
    
    # Create Mangum handler - this adapts FastAPI (ASGI) to Vercel's Lambda format
    # lifespan="off" because Vercel doesn't support ASGI lifespan events
    handler_instance = Mangum(app, lifespan="off")
    log.info("✅ FastAPI app and Mangum handler initialized successfully")
    
except Exception as e:
    log.error(f"❌ Failed to initialize FastAPI app: {e}", exc_info=True)
    # Create a minimal error handler
    def error_handler(event, context=None):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Failed to initialize FastAPI application',
                'message': str(e),
                'type': type(e).__name__
            })
        }
    handler_instance = error_handler

# Vercel serverless function handler
# This function is called by Vercel for every request to /api/*
def handler(event, context=None):
    """
    Vercel serverless function handler.
    
    Vercel routes /api/* requests to this function.
    The event contains the HTTP request details.
    Mangum converts the event to ASGI format and passes it to FastAPI.
    """
    try:
        # Log request for debugging
        path = event.get('path', '')
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN'))
        log.info(f"📥 Request: {method} {path}")
        
        # CRITICAL: Vercel may strip /api/ prefix when routing to api/index.py
        # FastAPI routes expect /api/ prefix, so we need to ensure it's present
        if path and not path.startswith('/api'):
            # Prepend /api/ if missing
            event['path'] = '/api' + path if path.startswith('/') else '/api/' + path
            log.info(f"🔧 Fixed path: {path} -> {event['path']}")
        elif not path:
            # Empty path means root /api/
            event['path'] = '/api/'
            log.info(f"🔧 Set empty path to: {event['path']}")
        
        # Call Mangum handler - it handles ASGI conversion and routing
        response = handler_instance(event, context)
        
        # Mangum returns a coroutine for async handlers, so we need to await it
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)
        
        # Log response
        status_code = response.get('statusCode', 500) if isinstance(response, dict) else 500
        log.info(f"📤 Response: {status_code} for {method} {path}")
        
        return response
        
    except Exception as e:
        log.error(f"❌ Handler error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'type': type(e).__name__
            })
        }
