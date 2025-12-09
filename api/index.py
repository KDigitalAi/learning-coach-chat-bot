"""
Vercel serverless function handler for FastAPI application.
Uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format.
"""
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from mangum import Mangum
from app.main import app

# Create Mangum handler for Vercel
# Mangum converts ASGI (FastAPI) to AWS Lambda/API Gateway format
# Vercel's Python runtime uses AWS Lambda-compatible format
handler = Mangum(app, lifespan="off")

