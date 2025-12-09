# Deployment Changes Summary

This document summarizes all changes made to prepare the Learning Coach project for Vercel deployment.

## ✅ Changes Made

### 1. Created Vercel Serverless Function Wrapper
- **File**: `api/index.py`
- **Purpose**: Wraps FastAPI application with Mangum adapter for Vercel serverless compatibility
- **Key Features**:
  - Adds backend directory to Python path
  - Wraps FastAPI app with Mangum handler
  - Disables lifespan events (not supported in serverless)

### 2. Created Vercel Configuration
- **File**: `vercel.json`
- **Configuration**:
  - Python serverless function build from `api/index.py`
  - Static frontend build from `frontend/package.json`
  - Routes API calls to serverless function
  - Routes all other requests to frontend
  - Sets function timeout to 60s and memory to 1024MB
  - Configures PYTHONPATH for backend imports

### 3. Updated Python Dependencies
- **File**: `backend/requirements.txt`
- **Added**: `mangum==0.17.0` (required for FastAPI → Vercel compatibility)

### 4. Created Vercel-Specific Requirements
- **File**: `api/requirements.txt`
- **Purpose**: Vercel looks for requirements.txt in the api/ directory
- **Contains**: All necessary Python dependencies including mangum

### 5. Updated Frontend API Calls
- **Files Modified**:
  - `frontend/src/App.jsx`
  - `frontend/src/components/ChatInterface.jsx`
- **Changes**: Replaced all hardcoded `http://localhost:8000/api/` URLs with relative `/api/` paths
- **Impact**: Frontend now works in both development (via Vite proxy) and production (via Vercel)

### 6. Updated Vite Configuration
- **File**: `frontend/vite.config.js`
- **Added**:
  - Build output directory configuration
  - Base path set to `/` for production compatibility

### 7. Updated Package.json
- **File**: `frontend/package.json`
- **Added**: `vercel-build` script for Vercel deployment

### 8. Updated CORS Settings
- **File**: `backend/app/main.py`
- **Changes**: 
  - Made CORS origins configurable via `ALLOWED_ORIGINS` environment variable
  - Supports multiple origins (comma-separated)
  - Defaults to `*` if not set

### 9. Created .vercelignore
- **File**: `.vercelignore`
- **Purpose**: Excludes unnecessary files from deployment
- **Excludes**: 
  - Python cache files
  - Local ChromaDB files
  - Node modules
  - Environment files
  - IDE files

## 📁 New File Structure

```
LearningCoach/
├── api/                          # NEW - Vercel serverless functions
│   ├── index.py                  # NEW - FastAPI wrapper
│   └── requirements.txt          # NEW - Vercel Python deps
├── backend/                       # Existing
│   ├── app/
│   └── requirements.txt          # UPDATED - Added mangum
├── frontend/                      # Existing
│   ├── src/                      # UPDATED - API calls use relative paths
│   ├── package.json              # UPDATED - Added vercel-build script
│   └── vite.config.js            # UPDATED - Added build config
├── vercel.json                   # NEW - Vercel configuration
├── .vercelignore                 # NEW - Deployment exclusions
├── VERCEL_DEPLOYMENT.md          # NEW - Deployment guide
└── DEPLOYMENT_CHANGES.md         # NEW - This file
```

## 🔄 Migration Notes

### What Changed for Development
- **No breaking changes** - Development workflow remains the same
- Vite proxy still works for local development
- Backend can still run with `uvicorn app.main:app --reload`

### What Changed for Production
- API calls now use relative paths (works in both dev and prod)
- CORS is configurable via environment variables
- FastAPI is wrapped for serverless execution

### Environment Variables Needed
Set these in Vercel Dashboard → Settings → Environment Variables:
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SESSION_SECRET_KEY`
- `ALLOWED_ORIGINS` (optional, defaults to `*`)

## 🚀 Next Steps

1. **Review the changes** in this document
2. **Read** `VERCEL_DEPLOYMENT.md` for deployment instructions
3. **Set environment variables** in Vercel dashboard
4. **Deploy** using Vercel CLI or dashboard
5. **Test** the deployed application

## ⚠️ Important Notes

1. **ChromaDB**: Local ChromaDB files are excluded from deployment. The project uses Supabase pgvector, so this is fine.

2. **Function Timeout**: Set to 60 seconds (maximum for Pro plan). If you need longer, consider optimizing the code or using a different deployment strategy.

3. **Cold Starts**: First request after inactivity may take 1-2 seconds. This is normal for serverless functions.

4. **Memory**: Set to 1024MB for AI operations. Monitor usage in Vercel dashboard.

5. **Streaming**: Server-Sent Events (SSE) should work, but test thoroughly after deployment.

## 🐛 Troubleshooting

If you encounter issues:

1. **Check function logs** in Vercel Dashboard → Functions
2. **Verify environment variables** are set correctly
3. **Check build logs** for any errors during deployment
4. **Test API endpoints** directly: `https://your-app.vercel.app/api/health`
5. **Review** `VERCEL_DEPLOYMENT.md` for common issues

## 📚 Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/runtimes/python)
- [Mangum Documentation](https://mangum.io/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

