# Vercel FastAPI Deployment Configuration

This document describes the complete Vercel configuration for the Learning Coach FastAPI application.

## Application Details

- **FastAPI app location**: `backend/app/main.py`
- **FastAPI app variable name**: `app`
- **Application code directory**: `backend/app/`
- **Static files directory**: `frontend/dist/` (built from `frontend/`)
- **Requirements file**: `api/requirements.txt` (for serverless function)
- **API route prefix**: `/api`
- **Main routers**:
  - `backend/app/routers/chat.py` → `/api/chat`
  - `backend/app/routers/onboarding.py` → `/api/onboarding`

## Project Structure

```
learning-coach-chat-bot/
├── api/
│   ├── index.py              # Vercel serverless function handler
│   └── requirements.txt      # Python dependencies for serverless
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application (app variable)
│   │   ├── routers/
│   │   │   ├── chat.py       # /api/chat routes
│   │   │   └── onboarding.py # /api/onboarding routes
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utilities
│   └── requirements.txt      # Full Python dependencies
├── frontend/
│   ├── dist/                 # Built static files (generated)
│   └── src/                  # React source code
├── vercel.json               # Vercel configuration
├── .vercelignore             # Files to exclude from deployment
└── requirements.txt          # Root requirements (fallback)
```

## Configuration Files

### 1. vercel.json

**Key Configuration:**
- **Build Command**: Builds React frontend from `frontend/` directory
- **Output Directory**: `frontend/dist/` (static files)
- **Builds**: Configures Python serverless function at `api/index.py`
- **Routes**: 
  - `/api/*` → Python serverless function (FastAPI)
  - `/health` → Python serverless function (FastAPI health check)
  - Static assets → Cached with long TTL
  - All other routes → `index.html` (SPA routing)

**Route Priority:**
1. API routes (`/api/*`) → FastAPI serverless function
2. Health check (`/health`) → FastAPI serverless function
3. Static assets (`.js`, `.css`, images, etc.) → Cached static files
4. All other routes → `index.html` (React SPA)

### 2. api/index.py

**Purpose**: Serverless function handler that wraps FastAPI app for Vercel

**Key Features:**
- Adds `backend/` directory to Python path
- Imports FastAPI app from `backend/app/main.py`
- Wraps app with Mangum (ASGI to Lambda adapter)
- Exports `handler` variable (required by Vercel)

**Handler Configuration:**
```python
handler = Mangum(app, lifespan="off")
```
- `lifespan="off"`: Disables startup/shutdown events (not needed in serverless)

### 3. api/requirements.txt

Contains all Python dependencies needed for the serverless function:
- FastAPI and related packages
- Mangum (ASGI adapter)
- LangChain and OpenAI SDK
- Supabase client
- All other backend dependencies

### 4. .vercelignore

Optimizes bundle size by excluding:
- `node_modules/` (frontend dependencies)
- Python cache files (`__pycache__/`, `*.pyc`)
- Database files (`.sqlite3`, `.db`)
- Development files (`.bat`, `.sh`, IDE configs)
- Test files
- Documentation (except README.md)
- Build artifacts (will be regenerated)

## API Routes

### FastAPI Routes

All routes are prefixed with `/api`:

- `GET /api/` - API info
- `GET /api/health` - Health check
- `POST /api/chat` - Main chat endpoint (SSE streaming)
- `POST /api/chat/save` - Save message to history
- `POST /api/onboarding/consent` - Update user consent and onboarding data

### Frontend Routes

All frontend routes are handled by React Router (client-side):
- Any route not starting with `/api/` → `index.html`

## CORS Configuration

CORS is configured in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (can be restricted in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Note**: In production, consider restricting `allow_origins` to your frontend domain:
```python
allow_origins=["https://your-domain.vercel.app"]
```

## Static File Serving

Static files are served from `frontend/dist/`:
- Built by Vite during `npm run build`
- Served directly by Vercel (not through FastAPI)
- Cached with long TTL (31536000 seconds = 1 year) for optimal performance

## Environment Variables

Required environment variables in Vercel:

**Backend:**
- `OPENAI_API_KEY` - OpenAI API key
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service_role key
- `SESSION_SECRET_KEY` - Session encryption key

**Frontend (Optional):**
- `VITE_API_URL` - Backend API URL (leave empty for same-domain)

## Deployment Flow

1. **Build Phase**:
   - Install frontend dependencies (`cd frontend && npm ci`)
   - Build React app (`npm run build`) → `frontend/dist/`
   - Prepare Python serverless function (`api/index.py`)

2. **Deployment Phase**:
   - Upload static files from `frontend/dist/`
   - Package Python serverless function with dependencies
   - Configure routes and headers

3. **Runtime**:
   - API requests (`/api/*`) → Python serverless function → FastAPI
   - Static file requests → Served directly from `frontend/dist/`
   - Frontend routes → `index.html` → React Router handles routing

## Bundle Size Optimization

The `.vercelignore` file excludes:
- **~40MB** of `node_modules/` (not needed in serverless)
- Python cache files
- Development and test files
- Database files

**Estimated bundle size**: ~5-10MB (Python dependencies + backend code)

## Troubleshooting

### API Routes Not Working

1. Check that `api/index.py` exists and exports `handler`
2. Verify `api/requirements.txt` includes all dependencies
3. Check Vercel function logs for import errors
4. Ensure `backend/` directory is in the deployment

### Static Files Not Loading

1. Verify `frontend/dist/` is built and contains files
2. Check `outputDirectory` in `vercel.json` points to `frontend/dist`
3. Verify file paths in HTML are correct (should be relative)

### CORS Errors

1. Check CORS middleware is configured in `backend/app/main.py`
2. Verify `allow_origins` includes your frontend domain
3. Check browser console for specific CORS error messages

### Build Failures

1. Check build logs in Vercel dashboard
2. Verify all dependencies are in `api/requirements.txt`
3. Ensure Python version is compatible (Vercel uses Python 3.9+)
4. Check for syntax errors in Python code

## Testing Deployment

After deployment, test these endpoints:

1. **Health Check**: `GET https://your-project.vercel.app/api/health`
   - Should return: `{"status": "healthy"}`

2. **API Info**: `GET https://your-project.vercel.app/api/`
   - Should return API information

3. **Frontend**: `GET https://your-project.vercel.app/`
   - Should load React application

4. **Static Assets**: `GET https://your-project.vercel.app/assets/...`
   - Should return cached static files

## Performance Optimization

1. **Static Assets**: Cached for 1 year (immutable)
2. **API Responses**: Consider adding caching headers for GET requests
3. **Bundle Size**: Optimized via `.vercelignore`
4. **Cold Starts**: Python serverless functions may have cold start latency (~1-2s)

## Security Headers

Configured in `vercel.json`:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

## Next Steps

1. Set environment variables in Vercel dashboard
2. Deploy to Vercel (via Git push or CLI)
3. Test all endpoints
4. Monitor function logs for errors
5. Consider restricting CORS origins in production

