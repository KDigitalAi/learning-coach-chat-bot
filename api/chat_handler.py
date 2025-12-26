"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.

This is the entry point for all /api/* routes on Vercel.
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

# FORCE ADD backend to path - critical for Vercel file structure
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
    log.info(f"Added {backend_path} to Python path")

# Also try adding current directory just in case
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import FastAPI app and Mangum
try:
    from mangum import Mangum
    from app.main import app
    
    # Create Mangum handler - this adapts FastAPI (ASGI) to Vercel's Lambda format
    # lifespan="off" because Vercel doesn't support ASGI lifespan events
    handler_instance = Mangum(app, lifespan="off")
    log.info("✅ FastAPI app and Mangum handler initialized successfully")
    
    # DEBUG: Check environment variables on startup
    log.info(f"🔑 Environment Check: OPENAI_API_KEY={'SET' if os.environ.get('OPENAI_API_KEY') else 'MISSING'}")
    log.info(f"🔑 Environment Check: SUPABASE_URL={'SET' if os.environ.get('SUPABASE_URL') else 'MISSING'}")
    
except Exception as e:
    log.error(f"❌ Failed to initialize FastAPI app: {e}", exc_info=True)
    import traceback
    traceback.print_exc()
    # Create a minimal error handler
    def error_handler(event, context=None):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Failed to initialize FastAPI application',
                'message': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            })
        }
    handler_instance = error_handler

# Vercel serverless function handler
def handler(event, context=None):
    """
    Vercel serverless function handler.
    """
    try:
        # Extract path and method from event
        # Vercel may pass path in different formats depending on routing
        path = event.get('path', '')
        raw_path = event.get('rawPath', '')
        method = event.get('httpMethod', '') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        headers = event.get('headers', {})
        
        # STRATEGY 1: Trust x-vercel-forwarded-path if available (standard for Vercel rewrites)
        # This header usually contains the path BEFORE the rewrite (e.g., /api/chat)
        forwarded_path = headers.get('x-vercel-forwarded-path') or headers.get('x-forwarded-path')
        
        # DEBUG: Log all relevant headers to understand what Vercel is sending
        log.info(f"🔎 Headers dump: x-vercel-forwarded-path={headers.get('x-vercel-forwarded-path')}, x-forwarded-path={headers.get('x-forwarded-path')}, host={headers.get('host')}")
        
        if forwarded_path:
            actual_path = forwarded_path
            log.info(f"🎯 Using forwarded path from headers: {actual_path}")
        else:
            # STRATEGY 2: Fallback to rawPath or path
            actual_path = raw_path if raw_path else path
            log.info(f"⚠️ No forwarded path header found. Using: {actual_path}")

        # STRATEGY 3 (Emergency Fallback):
        # If we are stuck at /api/chat_handler.py and it's a POST, it's 99% likely a chat request
        # This fixes the "404" if headers are stripped by a proxy or Vercel
        if (actual_path.endswith('/api/chat_handler.py') or actual_path.endswith('/api/chat_handler')):
            if method == 'POST':
                log.warning(f"🚨 EMERGENCY ROUTING: Path is {actual_path} but method is POST. Forcing /api/chat")
                actual_path = "/api/chat"
            elif method == 'GET':
                 # If it's GET /api/chat_handler.py, it might be a health check or just hitting the root of the function
                 log.warning(f"🚨 EMERGENCY ROUTING: Path is {actual_path} and method is GET. Defaulting to /api/health")
                 actual_path = "/api/health"

        log.info(f"📥 Request: {method} | path={path} | forwarded={forwarded_path} | actual_path={actual_path}")
        
        # CRITICAL: FastAPI routers are mounted with /api prefix
        # We must ensure the path starts with /api
        if actual_path:
            if not actual_path.startswith('/api'):
                # Path is missing /api/ prefix - add it
                # But be careful: if actual_path is just "/", do we want "/api/"?
                fixed_path = '/api' + actual_path if actual_path.startswith('/') else '/api/' + actual_path
                # Special case: if it became /api//chat, fix it
                fixed_path = fixed_path.replace('/api//', '/api/')
                
                event['path'] = fixed_path
                if 'rawPath' in event:
                    event['rawPath'] = fixed_path
                log.info(f"🔧 Fixed path: {actual_path} -> {fixed_path}")
            else:
                # Path already has /api/ prefix - ensure event uses it
                event['path'] = actual_path
                if 'rawPath' in event:
                    event['rawPath'] = actual_path
                log.info(f"✅ Path already correct: {actual_path}")
        else:
            # Empty path - set to /api/ root
            event['path'] = '/api/'
            if 'rawPath' in event:
                event['rawPath'] = '/api/'
            log.info(f"🔧 Set empty path to: /api/")
        
        # Ensure httpMethod is set correctly
        if 'httpMethod' not in event and method:
            event['httpMethod'] = method
            headers = event.get('headers', {})
            # Try standard Vercel/proxy headers for original path
            forwarded_path = headers.get('x-vercel-forwarded-path') or headers.get('x-forwarded-path')
            # Also check if query string needs to be appended (rawPath usually has it, but forwarded_path might not)
            if forwarded_path:
                # If we have query parameters in the event, we might need to append them
                # But usually purely for routing in FastAPI, path is enough.
                # However, rawQueryString might be separate.
                actual_path = forwarded_path
                log.info(f"🔄 Recovered original path from headers: {actual_path}")

        log.info(f"📥 Request: {method} | path={path} | rawPath={raw_path} | actual_path={actual_path}")
        log.info(f"📋 Event keys: {list(event.keys())}")
        
        # CRITICAL FIX: Vercel routes /api/* to api/index.py
        # The path in the event should be the FULL path including /api/
        # FastAPI routes are defined with /api/ prefix, so path should match exactly
        # If path doesn't start with /api/, prepend it
        if actual_path:
            if not actual_path.startswith('/api'):
                # Path is missing /api/ prefix - add it
                fixed_path = '/api' + actual_path if actual_path.startswith('/') else '/api/' + actual_path
                event['path'] = fixed_path
                if 'rawPath' in event:
                    event['rawPath'] = fixed_path
                log.info(f"🔧 Fixed path: {actual_path} -> {fixed_path}")
            else:
                # Path already has /api/ prefix - ensure event uses it
                event['path'] = actual_path
                if 'rawPath' in event:
                    event['rawPath'] = actual_path
                log.info(f"✅ Path already correct: {actual_path}")
        else:
            # Empty path - set to /api/ root
            event['path'] = '/api/'
            if 'rawPath' in event:
                event['rawPath'] = '/api/'
            log.info(f"🔧 Set empty path to: /api/")
        
        # Ensure httpMethod is set correctly
        if 'httpMethod' not in event and method:
            event['httpMethod'] = method
        
        # Call Mangum handler - it handles ASGI conversion and routing
        log.info(f"🚀 Calling Mangum with path: {event.get('path')}")
        
        # Check for empty body on POST requests (common Vercel issue)
        if event.get('httpMethod') == 'POST' and not event.get('body') and not event.get('isBase64Encoded'):
             log.warning("⚠️ Received POST request with empty body")
             # We let Mangum handle it, but it's good to know

        response = handler_instance(event, context)
        
        # Mangum returns a coroutine for async handlers, so we need to await it
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)
        
        # Log response
        status_code = response.get('statusCode', 500) if isinstance(response, dict) else 500
        log.info(f"📤 Response: {status_code} for {method} {event.get('path')}")
        
        # Ensure CORS headers are present
        if isinstance(response, dict) and 'headers' in response:
            headers = response['headers']
            if 'Access-Control-Allow-Origin' not in headers:
                headers['Access-Control-Allow-Origin'] = '*'
            if 'Access-Control-Allow-Methods' not in headers:
                headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            if 'Access-Control-Allow-Headers' not in headers:
                headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
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
                'message': str(e),
                'type': type(e).__name__,
                'path': event.get('path', 'unknown'),
                'traceback': traceback.format_exc()
            })
        }
