"""
Simple test handler to verify Vercel Python functions work.
This endpoint should be accessible at /api/test (without rewrite).
"""
import json

def handler(event, context=None):
    """Simple test handler that returns event information."""
    # Extract path from various sources
    path = event.get('path') or event.get('rawPath') or 'unknown'
    method = event.get('httpMethod') or 'GET'
    headers = event.get('headers', {}) or {}
    query = event.get('queryStringParameters') or {}
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'ok',
            'message': 'Test handler is working',
            'method': method,
            'path': path,
            'event_keys': list(event.keys()) if isinstance(event, dict) else 'not a dict',
            'headers_with_path': [k for k in headers.keys() if 'path' in k.lower()],
            'query_params': query,
            'note': 'If you see this, the Python function is working!'
        }, indent=2)
    }
