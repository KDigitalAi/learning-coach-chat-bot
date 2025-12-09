# Vercel Deployment Guide

This guide explains how to deploy the Learning Coach application on Vercel using serverless functions.

## Architecture

- **Frontend**: React/Vite app deployed as static files
- **Backend**: FastAPI app deployed as Python serverless functions using Mangum adapter
- **API Routes**: All `/api/*` routes are handled by the Python serverless function

## Project Structure

```
.
├── api/
│   └── index.py          # Vercel serverless function handler
├── backend/              # FastAPI application
│   ├── app/
│   └── requirements.txt
├── frontend/            # React/Vite application
│   ├── src/
│   └── package.json
├── vercel.json          # Vercel configuration
├── requirements.txt     # Root requirements (references backend/requirements.txt)
└── .vercelignore       # Files to exclude from deployment
```

## Setup Instructions

### 1. Environment Variables

Set these environment variables in your Vercel project dashboard (Settings → Environment Variables):

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase service role key
- `SESSION_SECRET_KEY` - A random secret key for session management

**Optional:**
- `VITE_API_BASE_URL` - Leave empty for same-domain API calls (recommended)

### 2. Database Setup

1. Create a Supabase project at https://supabase.com
2. Run the SQL schema from `backend/database/schema.sql` in Supabase SQL Editor
3. Get your project URL and service_role key from Supabase dashboard

### 3. Deploy

1. Connect your GitHub repository to Vercel
2. Vercel will automatically detect the configuration from `vercel.json`
3. Set the environment variables in Vercel dashboard
4. Deploy!

## How It Works

### Serverless Function Handler

The `api/index.py` file uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless function format:

```python
from mangum import Mangum
from app.main import app

handler = Mangum(app, lifespan="off")
```

### Routing

- All requests to `/api/*` are routed to the Python serverless function
- All other requests are served by the frontend `index.html` (for client-side routing)

### Build Process

1. **Frontend Build**: Vercel builds the React app using `npm run build` in the `frontend/` directory
2. **Python Function**: Vercel installs Python dependencies from `requirements.txt` and creates the serverless function
3. **Deployment**: Both are deployed together on the same domain

## Troubleshooting

### 404 Errors

- Ensure environment variables are set in Vercel dashboard
- Check that routes in `vercel.json` are correct
- Verify the serverless function is building correctly (check Functions tab in Vercel dashboard)

### Function Timeouts

- Vercel free tier has a 10-second timeout
- Hobby tier has a 60-second timeout
- Consider optimizing long-running operations or upgrading your plan

### Import Errors

- Ensure `backend/` directory is in the Python path (handled in `api/index.py`)
- Check that all dependencies are in `backend/requirements.txt`

## Local Testing

Test locally using Vercel CLI:

```bash
npm install -g vercel
vercel dev
```

This will:
- Start the frontend dev server
- Run serverless functions locally
- Use environment variables from `.env` file (if present)

## Notes

- The backend uses Supabase for database storage (no local database needed)
- Environment variables are read from Vercel's environment (not `.env` file in production)
- The frontend uses relative API paths when `VITE_API_BASE_URL` is empty

