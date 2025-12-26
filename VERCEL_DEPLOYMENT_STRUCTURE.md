# Vercel Deployment Structure

This document describes the optimized project structure for Vercel serverless deployment.

## Project Structure

```
LearningCoach/
├── api/                          # Vercel serverless functions
│   ├── __init__.py              # Python package marker
│   ├── index.py                 # Main handler for all /api/* routes
│   └── test.py                  # Test handler (optional, for debugging)
│
├── backend/                      # FastAPI application code
│   └── app/
│       ├── main.py              # FastAPI app instance
│       ├── routers/             # API route handlers
│       ├── services/            # Business logic
│       └── utils/               # Utility functions
│
├── frontend/                     # Frontend source files
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── assets/
│
├── public/                       # Built frontend (created by build script)
│   └── [copied from frontend/]
│
├── scripts/
│   └── copy-frontend.js         # Build script to copy frontend to public
│
├── requirements.txt              # Python dependencies (root level for Vercel)
├── package.json                 # Node.js dependencies and build script
├── vercel.json                  # Vercel configuration
└── .vercelignore                # Files to ignore during deployment
```

## Key Configuration Files

### vercel.json
- **Functions**: Configures Python serverless functions in `api/` directory
- **Rewrites**: Routes all `/api/*` requests to `/api/index` handler
- **Build Command**: Runs `npm run build` to copy frontend to `public/`
- **Output Directory**: `public/` (served as static files)

### api/index.py
- **Purpose**: Single entry point for all API routes
- **Handler Function**: `handler(event, context)` - required by Vercel
- **Technology**: Uses Mangum to adapt FastAPI (ASGI) to Vercel (Lambda)
- **Path Handling**: Extracts original request path from Vercel event headers

### Build Process
1. Vercel runs `npm run build`
2. Script copies `frontend/` → `public/`
3. Vercel detects Python files in `api/` directory
4. Installs dependencies from `requirements.txt`
5. Creates serverless functions

## Routing Flow

### API Routes (`/api/*`)
1. Request: `GET /api/health`
2. Vercel rewrite: Routes to `/api/index`
3. Vercel executes: `api/index.py` → `handler()` function
4. Handler extracts: Original path from event headers (`/api/health`)
5. Mangum converts: Lambda event → FastAPI request
6. FastAPI routes: To correct endpoint (`@app.get("/api/health")`)
7. Response: Streamed back through handler

### Static Files (`/`)
1. Request: `GET /` or `/index.html`
2. Vercel serves: Files from `public/` directory
3. Frontend loads: `index.html` with `script.js` and `style.css`

## Environment Variables Required

Set these in Vercel Dashboard → Settings → Environment Variables:

- `OPENAI_API_KEY` - OpenAI API key
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service role key
- `SESSION_SECRET_KEY` - (Optional) Session encryption key

## Deployment Checklist

- [ ] Environment variables set in Vercel Dashboard
- [ ] `requirements.txt` contains all dependencies (including `mangum`)
- [ ] `api/index.py` has proper handler function
- [ ] `vercel.json` configured with correct rewrites
- [ ] Build script (`scripts/copy-frontend.js`) works
- [ ] `public/` directory is created (or will be created during build)
- [ ] All routes in FastAPI have `/api/` prefix

## Testing After Deployment

1. **Health Check**: `GET /api/health` → Should return 200 OK
2. **Test Endpoint**: `GET /api/test` → Should return 200 OK  
3. **Frontend**: `GET /` → Should serve `index.html`
4. **Chat Endpoint**: `POST /api/chat` → Should stream response
5. **Onboarding**: `POST /api/onboarding/consent` → Should save data

## Troubleshooting

### 404 Errors on All Routes
- Check Vercel Functions tab - is `api/index.py` listed?
- Check build logs - are dependencies installing correctly?
- Verify `handler` function exists in `api/index.py`

### Path Routing Issues
- Check Vercel function logs for path extraction
- Verify Mangum is receiving correct path in event
- Ensure FastAPI routes have `/api/` prefix

### Import Errors
- Verify `backend/` is in Python path (handled in `api/index.py`)
- Check `includeFiles: "backend/**"` in `vercel.json`
- Ensure all dependencies in `requirements.txt`

### Frontend Not Loading
- Verify `public/` directory exists after build
- Check build logs for `copy-frontend.js` execution
- Ensure `vercel.json` has correct `outputDirectory`

## Notes

- The catch-all route in `main.py` is commented out (not needed, FastAPI handles 404s)
- Old handler files (`chat_handler.py`, `status.py`) have been removed
- `api/test.py` is kept for debugging but not used by rewrites
- All API routes must have `/api/` prefix to match rewrite pattern

