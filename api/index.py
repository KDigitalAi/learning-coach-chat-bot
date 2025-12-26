"""
Vercel serverless function handler - Single entry point for all /api/* routes.
"""
# CRITICAL: Print statement to verify module is loaded (Vercel captures print output)
print("=" * 80)
print("🔵🔵🔵 api/index.py MODULE IS LOADING - This proves Vercel detected the function")
print("=" * 80)

import sys
import os
import json
import logging
import asyncio
from pathlib import Path
from urllib.parse import urlparse, unquote

# Configure logging - CRITICAL: This must be set up early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # Force reconfiguration in case logging was already configured
)
log = logging.getLogger(__name__)
log.info("=" * 80)
log.info("🔵🔵🔵 LOGGING CONFIGURED - api/index.py is executing")
log.info("=" * 80)

# #region agent log
def debug_log(location, message, data=None, hypothesis_id=None):
    """Enhanced logging that works in Vercel - logs to both file and standard logging."""
    import time
    log_entry = {
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
        "sessionId": "vercel-debug",
        "runId": os.getenv("VERCEL_DEPLOYMENT_ID", "local"),
        "hypothesisId": hypothesis_id
    }
    
    # ALWAYS log to standard logging (Vercel captures this)
    log_msg = f"[DEBUG {hypothesis_id or 'N/A'}] {location}: {message}"
    if data:
        log_msg += f" | Data: {json.dumps(data, default=str)[:500]}"
    log.info(log_msg)
    
    # Try to write to file (use /tmp in Vercel, fallback to .cursor locally)
    try:
        # Try /tmp first (Vercel allows writes here)
        tmp_path = Path("/tmp") / "vercel_debug.log"
        if tmp_path.parent.exists():
            with open(tmp_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        else:
            # Fallback to .cursor directory (local dev)
            debug_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
            debug_path.parent.mkdir(parents=True, exist_ok=True)
            with open(debug_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        # File write failed, but standard logging already captured it
        log.debug(f"File log write failed (non-critical): {e}")

# Module-level initialization log - THIS WILL SHOW IN VERCEL LOGS
debug_log("api/index.py:module", "🔵 MODULE LOADED - api/index.py is executing", {
    "python_version": sys.version.split()[0],
    "cwd": os.getcwd(),
    "file_path": __file__
}, "H1")
# #endregion

# Add backend to path
backend_path = str(Path(__file__).parent.parent / "backend")
sys.path.insert(0, backend_path)
# #region agent log
debug_log("api/index.py:18", "🔵 Backend path added to sys.path", {
    "backend_path": backend_path,
    "path_exists": os.path.exists(backend_path),
    "sys_path_length": len(sys.path)
}, "H1")
# #endregion

# Import FastAPI app
# #region agent log
env_vars = {k: "✅ SET" if os.getenv(k) else "❌ MISSING" for k in ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]}
debug_log("api/index.py:21", "🔵 Starting FastAPI import", {
    "backend_path": str(Path(__file__).parent.parent / "backend"),
    "env_vars": env_vars
}, "H4,H5")
# #endregion
try:
    from mangum import Mangum
    from app.main import app
    # #region agent log
    routes_info = [{"path": str(r.path), "methods": list(r.methods) if hasattr(r, 'methods') else []} for r in app.routes[:10]] if hasattr(app, 'routes') else []
    debug_log("api/index.py:25", "✅ FastAPI app imported successfully", {
        "app_routes_count": len(app.routes) if hasattr(app, 'routes') else 0,
        "sample_routes": routes_info[:5]
    }, "H4")
    # #endregion
    handler_instance = Mangum(app, lifespan="off")
    # #region agent log
    debug_log("api/index.py:27", "✅ Mangum handler created", {
        "handler_type": type(handler_instance).__name__
    }, "H4")
    # #endregion
    log.info("✅✅✅ FastAPI initialized successfully - handler ready")
except Exception as e:
    # #region agent log
    import traceback
    debug_log("api/index.py:30", "❌❌❌ FastAPI init FAILED", {
        "error": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc()[:1000]
    }, "H4")
    # #endregion
    log.error(f"❌❌❌ CRITICAL: Init failed: {e}", exc_info=True)
    def error_handler(event, context=None):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Init failed', 'message': str(e)[:200]})
        }
    handler_instance = error_handler

def handler(event, context=None):
    """Vercel serverless function handler."""
    # #region agent log
    log.info("🔵🔵🔵 HANDLER FUNCTION CALLED - This proves Vercel is executing the function")
    debug_log("api/index.py:36", "🔵 Handler function called", {
        "event_keys": list(event.keys()) if isinstance(event, dict) else "not_dict",
        "has_context": context is not None,
        "event_type": type(event).__name__
    }, "H1")
    # #endregion
    try:
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {}) or {}
        headers_lower = {k.lower(): v for k, v in headers.items()}
        query = event.get('queryStringParameters') or {}
        request_context = event.get('requestContext', {})
        # #region agent log
        log.info(f"🔵 Event received - Method: {method}, Path: {event.get('path')}, RawPath: {event.get('rawPath')}")
        debug_log("api/index.py:42", "🔵 Event structure extracted", {
            "method": method,
            "event_path": event.get('path'),
            "event_rawPath": event.get('rawPath'),
            "header_keys": list(headers.keys())[:10],
            "has_requestContext": bool(request_context),
            "all_headers": dict(headers) if len(headers) < 20 else "too_many"
        }, "H1")
        # #endregion
        
        # CRITICAL: Extract original path from Vercel event
        # Vercel may pass the original path in different places when using rewrites
        original_path = None
        # #region agent log
        debug_log("api/index.py:47", "Starting path extraction", {"headers_checked": ['x-vercel-rewrite-path', 'x-vercel-forwarded-path', 'x-forwarded-path', 'x-invoke-path']}, "H3")
        # #endregion
        
        # Method 1: Check Vercel-specific headers FIRST (most reliable for rewrites)
        if not original_path:
            for header_name in ['x-vercel-rewrite-path', 'x-vercel-forwarded-path', 'x-forwarded-path', 'x-invoke-path']:
                if header_name in headers_lower:
                    original_path = headers_lower[header_name]
                    # #region agent log
                    debug_log("api/index.py:54", "Path found in header", {"header": header_name, "path": original_path}, "H3")
                    # #endregion
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
            # #region agent log
            debug_log("api/index.py:105", "Path extraction failed, using default", {
                "event_path": event.get('path'),
                "event_rawPath": event.get('rawPath'),
                "all_headers": dict(headers),
                "requestContext": dict(request_context) if request_context else None
            }, "H3")
            # #endregion
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
        
        log.info(f"📥📥📥 REQUEST: {method} {original_path}")
        # #region agent log
        debug_log("api/index.py:139", "🔵 Calling Mangum handler", {
            "final_path": original_path,
            "method": method,
            "handler_type": type(handler_instance).__name__
        }, "H3")
        # #endregion
        
        # Call Mangum - it will convert Lambda event to FastAPI request
        response = handler_instance(event, context)
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)
        
        status_code = response.get('statusCode', 500) if isinstance(response, dict) else 500
        # #region agent log
        log.info(f"📤📤📤 RESPONSE: {status_code} for {original_path}")
        debug_log("api/index.py:147", "🔵 Mangum response received", {
            "status_code": status_code,
            "path": original_path,
            "response_keys": list(response.keys()) if isinstance(response, dict) else "not_dict"
        }, "H3")
        # #endregion
        
        # Add CORS headers
        if isinstance(response, dict) and 'headers' in response:
            h = response['headers']
            h.setdefault('Access-Control-Allow-Origin', '*')
            h.setdefault('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, HEAD')
            h.setdefault('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        
        return response
        
    except Exception as e:
        # #region agent log
        import traceback
        log.error(f"❌❌❌ HANDLER EXCEPTION: {e}")
        debug_log("api/index.py:158", "❌ Handler exception", {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()[:1000]
        }, "H1")
        # #endregion
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
