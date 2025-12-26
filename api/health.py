"""
Minimal health check endpoint to verify Vercel Python functions work.
This should be accessible at /api/health without any rewrites.
"""
import json

def handler(event, context=None):
    """Minimal health check handler."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'ok',
            'message': 'Python function is working',
            'service': 'Vercel serverless function'
        })
    }

