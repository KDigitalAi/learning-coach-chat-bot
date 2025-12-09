# Vercel Deployment Guide

This guide explains how to deploy the Learning Coach Chat Bot (both frontend and backend) to Vercel.

## Prerequisites

- A Vercel account
- GitHub repository with your code
- OpenAI API key
- Supabase account and project

## Deployment Steps

### 1. Configure Environment Variables

Before deploying, you need to set the following environment variables in Vercel:

1. Go to your Vercel project settings
2. Navigate to **Settings** > **Environment Variables**
3. Add the following variables:

   **Backend Environment Variables:**
   - **Name**: `OPENAI_API_KEY`
     - **Value**: Your OpenAI API key
     - **Environment**: Production, Preview, Development
   
   - **Name**: `SUPABASE_URL`
     - **Value**: Your Supabase project URL (e.g., `https://xxxxx.supabase.co`)
     - **Environment**: Production, Preview, Development
   
   - **Name**: `SUPABASE_KEY`
     - **Value**: Your Supabase service_role key (NOT the anon key)
     - **Environment**: Production, Preview, Development
   
   - **Name**: `SESSION_SECRET_KEY`
     - **Value**: A random secret key for session management
     - **Environment**: Production, Preview, Development
     - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

   **Frontend Environment Variables (Optional):**
   - **Name**: `VITE_API_URL`
     - **Value**: Leave empty (backend is on same domain) OR set to separate backend URL if deployed separately
     - **Environment**: Production, Preview, Development
     - **Note**: If backend is on the same Vercel project, leave this empty to use relative paths

### 2. Deploy to Vercel

#### Option A: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

#### Option B: Deploy via GitHub Integration

1. Push your code to GitHub
2. Import your repository in Vercel
3. Vercel will automatically detect the configuration from `vercel.json`

### 3. Verify Deployment

After deployment:
1. Check that the build completed successfully
2. Visit your deployment URL
3. Verify that the application loads without 404 errors
4. Test API connectivity

## Configuration Files

### vercel.json

The `vercel.json` file configures:
- **Build Command**: Builds the frontend from the `frontend` directory
- **Output Directory**: Points to `frontend/dist` (Vite's default build output)
- **Functions**: Configures Python serverless functions for the backend API
- **Rewrites**: 
  - `/api/*` routes are handled by the Python serverless function
  - All other routes are rewritten to `/index.html` for SPA routing
- **Headers**: Security headers and caching for static assets

### API Serverless Function

The backend is deployed as a serverless function:
- **Location**: `api/index.py`
- **Runtime**: Python 3.9+ (via `@vercel/python`)
- **Handler**: Uses Mangum to wrap FastAPI for serverless compatibility
- **Dependencies**: Managed via `api/requirements.txt`

### API Configuration

The frontend uses `frontend/src/utils/api.js` to handle API endpoints:
- In development: Uses `http://localhost:8000`
- In production: 
  - If `VITE_API_URL` is set: Uses that URL
  - If `VITE_API_URL` is empty: Uses relative paths (same domain - recommended)

## Troubleshooting

### 404 Errors

If you're still getting 404 errors:
1. Verify `vercel.json` is in the project root
2. Check that `outputDirectory` points to `frontend/dist`
3. Ensure the build completed successfully
4. Check browser console for specific error messages

### API Connection Issues

If API calls are failing:
1. Verify all backend environment variables are set in Vercel (OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY, SESSION_SECRET_KEY)
2. Check that the serverless function is deployed correctly (check Functions tab in Vercel dashboard)
3. Verify Supabase credentials are correct (use service_role key, not anon key)
4. Check browser network tab for specific error details
5. Check Vercel function logs for backend errors

### Build Failures

If the build fails:
1. Check build logs in Vercel dashboard
2. Ensure all dependencies are in `package.json`
3. Verify Node.js version compatibility
4. Check for TypeScript/ESLint errors

## Project Structure

```
.
├── api/
│   ├── index.py              # Serverless function handler
│   └── requirements.txt      # Python dependencies for serverless
├── backend/
│   ├── app/                   # FastAPI application
│   └── requirements.txt       # Python dependencies (includes mangum)
├── frontend/
│   └── dist/                  # Built frontend (generated)
├── vercel.json                # Vercel configuration
└── .vercelignore              # Files to exclude from deployment
```

## Backend URL

After deployment, your backend API will be available at:
- **Base URL**: `https://your-project-name.vercel.app/api`
- **Endpoints**:
  - `POST /api/chat` - Main chat endpoint
  - `POST /api/chat/save` - Save message to history
  - `POST /api/onboarding/consent` - Update consent
  - `GET /api/health` - Health check
  - `GET /api/` - API info

## Notes

- Both frontend and backend are deployed on the same Vercel project
- The backend runs as serverless functions (no need for separate deployment)
- CORS is configured to allow all origins (can be restricted in production)
- The frontend is a Single Page Application (SPA), so all routes are handled client-side
- Environment variables are automatically available to both frontend and backend
- Make sure your Supabase database schema is set up (run `backend/database/schema.sql` in Supabase SQL Editor)

