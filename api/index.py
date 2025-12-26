"""
Vercel serverless function handler - Single entry point for all /api/* routes.
"""
import sys
import os
import json
import logging
import asyncio
from pathlib import Path
from urllib.parse import urlparse, unquote

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Add backend to path
backend_path = str(Path(__file__).parent.parent / "backend")
sys.path.insert(0, backend_path)

# Import FastAPI app
try:
    from mangum import Mangum
    from app.main import app
    handler_instance = Mangum(app, lifespan="off")
    log.info("✅ FastAPI initialized")
except Exception as e:
    log.error(f"❌ Init failed: {e}", exc_info=True)
    def error_handler(event, context=None):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Init failed', 'message': str(e)[:200]})
        }
    handler_instance = error_handler

def handler(event, context=None):
    """Vercel serverless function handler."""
    try:
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {}) or {}
        headers_lower = {k.lower(): v for k, v in headers.items()}
        query = event.get('queryStringParameters') or {}
        request_context = event.get('requestContext', {})
        
        # CRITICAL: Extract original path from Vercel event
        # Vercel may pass the original path in different places when using rewrites
        original_path = None
        
        # Method 1: Check query string FIRST (we're explicitly passing it in rewrite)
        # This is the most reliable method since we control it
        if query and query.get('path'):
            original_path = query['path']
            log.info(f"✅ Found in query string: {original_path}")
        
        # Method 2: Check Vercel-specific headers (fallback if query not available)
        if not original_path:
            for header_name in ['x-vercel-rewrite-path', 'x-vercel-forwarded-path', 'x-forwarded-path', 'x-invoke-path']:
                if header_name in headers_lower:
                    original_path = headers_lower[header_name]
                    log.info(f"✅ Found in {header_name}: {original_path}")
                    break
        
        # Method 3: Check if path in event is already the original (Vercel sometimes preserves it)
        if not original_path:
            event_path = event.get('path') or event.get('rawPath', '')
            if event_path and not event_path.endswith('/index') and 'index' not in event_path.lower():
                original_path = event_path
                log.info(f"✅ Using event path (original): {original_path}")
        
        # Method 4: Extract from request URL if available
        if not original_path:
            # Check if there's a URL in the request context
            http_info = request_context.get('http', {})
            if http_info.get('path'):
                original_path = http_info['path']
                log.info(f"✅ Found in requestContext.http.path: {original_path}")
            elif request_context.get('path'):
                original_path = request_context['path']
                log.info(f"✅ Found in requestContext.path: {original_path}")
        
        # Method 5: Try to get from forwarded URL headers
        if not original_path:
            for url_header in ['x-forwarded-url', 'x-forwarded-uri', 'x-original-url', 'referer']:
                if url_header in headers_lower:
                    try:
                        url = headers_lower[url_header]
                        # Extract path from full URL
                        if url.startswith('http'):
                            parsed = urlparse(url)
                            path = parsed.path
                            if path and path.startswith('/api/'):
                                original_path = path
                                log.info(f"✅ Extracted from {url_header}: {original_path}")
                                break
                    except Exception as e:
                        log.debug(f"Failed to parse {url_header}: {e}")
        
        # Method 6: If we got /api/index, try to reconstruct from headers
        if not original_path or 'index' in original_path.lower():
            # Check all headers for any path-like value
            for header_name, header_value in headers.items():
                if isinstance(header_value, str):
                    # Look for paths that start with /api/ but aren't /api/index
                    if header_value.startswith('/api/') and 'index' not in header_value.lower():
                        original_path = header_value
                        log.info(f"✅ Found in header {header_name}: {original_path}")
                        break
        
        # Method 7: Last resort - if path is /api/index, we can't know the original
        # But we can at least try /api/health as a fallback for testing
        if not original_path or 'index' in original_path.lower():
            log.warning("⚠️ Could not extract original path, using default")
            log.warning(f"Event path: {event.get('path')}")
            log.warning(f"Event rawPath: {event.get('rawPath')}")
            log.warning(f"Headers: {list(headers.keys())[:10]}")
            # Default to /api/ - this will at least hit the root
            original_path = '/api/'
        
        # Ensure path starts with /api
        if not original_path.startswith('/api'):
            if original_path.startswith('/'):
                original_path = '/api' + original_path
            else:
                original_path = '/api/' + original_path
        
        # Clean up path (remove query strings, fragments, etc.)
        if '?' in original_path:
            original_path = original_path.split('?')[0]
        if '#' in original_path:
            original_path = original_path.split('#')[0]
        original_path = unquote(original_path)  # URL decode
        
        # Update event with correct path for Mangum
        event['path'] = original_path
        if 'rawPath' in event:
            event['rawPath'] = original_path
        event['httpMethod'] = method
        
        # Also update requestContext if it exists
        if 'requestContext' in event:
            if 'http' in event['requestContext']:
                event['requestContext']['http']['path'] = original_path
            event['requestContext']['path'] = original_path
        
        log.info(f"📥 {method} {original_path}")
        
        # Call Mangum - it will convert Lambda event to FastAPI request
        response = handler_instance(event, context)
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)
        
        status_code = response.get('statusCode', 500) if isinstance(response, dict) else 500
        log.info(f"📤 {status_code} for {original_path}")
        
        # Add CORS headers
        if isinstance(response, dict) and 'headers' in response:
            h = response['headers']
            h.setdefault('Access-Control-Allow-Origin', '*')
            h.setdefault('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, HEAD')
            h.setdefault('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        
        return response
        
    except Exception as e:
        log.error(f"❌ Handler error: {e}", exc_info=True)
        import traceback
        log.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'error': 'Handler error',
                'message': str(e)[:200],
                'type': type(e).__name__
            })
        }
