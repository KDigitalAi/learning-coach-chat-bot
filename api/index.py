"""
Vercel serverless function handler - Single entry point for all /api/* routes.
"""
import sys
import os
import json
import logging
import asyncio
from pathlib import Path

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
        
        # Extract original path - try all methods
        original_path = (
            headers_lower.get('x-vercel-rewrite-path') or
            headers_lower.get('x-vercel-forwarded-path') or
            headers_lower.get('x-forwarded-path') or
            query.get('path') or
            event.get('path') or
            event.get('rawPath') or
            '/api/'
        )
        
        # If path contains 'index', try to find original
        if 'index' in original_path.lower():
            # Check all headers
            for k, v in headers.items():
                if isinstance(v, str) and v.startswith('/api/') and 'index' not in v.lower():
                    original_path = v
                    break
        
        # Ensure /api prefix
        if not original_path.startswith('/api'):
            original_path = '/api' + (original_path if original_path.startswith('/') else '/' + original_path)
        
        # Update event
        event['path'] = original_path
        event['rawPath'] = original_path
        event['httpMethod'] = method
        
        log.info(f"📥 {method} {original_path}")
        
        # Call Mangum
        response = handler_instance(event, context)
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)
        
        # Add CORS
        if isinstance(response, dict) and 'headers' in response:
            h = response['headers']
            h.setdefault('Access-Control-Allow-Origin', '*')
        
        return response
        
    except Exception as e:
        log.error(f"❌ Error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'error': str(e)[:200],
                'event_keys': list(event.keys()) if isinstance(event, dict) else 'not dict'
            })
        }
