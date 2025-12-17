"""
Simple test handler to verify Vercel Python functions work.
"""
import json

def handler(event, context=None):
    """Simple test handler."""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'ok',
            'message': 'Test handler is working',
            'event_type': str(type(event)),
            'event_keys': list(event.keys()) if isinstance(event, dict) else 'not a dict'
        })
    }
