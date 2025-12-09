# Vercel Deployment Alternatives

Since the standard deployment isn't triggering, here are multiple alternative configurations to try.

## Current Configuration (vercel.json)

Using `functions` format with `rewrites`:
- ✅ Modern Vercel format
- ✅ Explicit function configuration
- ✅ Rewrites for routing

## Alternative 1: Builds + Routes Format

**File**: `vercel-alternative-1.json`

This uses the older `builds` and `routes` format:
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [...]
}
```

**To use**: Rename `vercel-alternative-1.json` to `vercel.json`

## Alternative 2: Minimal Configuration

**File**: `vercel-alternative-2.json`

Simplified configuration without explicit function declaration:
```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

**To use**: Rename `vercel-alternative-2.json` to `vercel.json`

## Alternative 3: Move Handler to Root

If the `api/` directory isn't being detected, try moving the handler:

1. Create `index.py` in project root
2. Update imports to point to `backend/app/main.py`
3. Update `vercel.json` to reference root `index.py`

## Alternative 4: Separate Projects

Deploy frontend and backend as separate Vercel projects:

### Frontend Project
- Root directory: `frontend/`
- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist/`

### Backend Project
- Root directory: `backend/` or `api/`
- Framework: Other
- Build command: (none)
- Functions: Auto-detect Python

## Manual Deployment Steps

### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Or deploy to production
vercel --prod
```

### Option 2: GitHub Integration

1. Go to Vercel Dashboard
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: Leave empty (or set to project root)
   - **Framework Preset**: Other
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm ci`

### Option 3: Deploy Hook

1. Go to Vercel Project Settings
2. Navigate to "Deploy Hooks"
3. Create a new hook
4. Use the hook URL to trigger deployments:
```bash
curl -X POST "YOUR_DEPLOY_HOOK_URL"
```

## Troubleshooting Steps

### 1. Check Vercel Dashboard

1. Go to your Vercel project
2. Check "Settings" → "General"
3. Verify:
   - Root Directory is correct
   - Build Command is set
   - Output Directory is set
   - Framework Preset (try "Other" if auto-detection fails)

### 2. Check Build Logs

1. Go to "Deployments" tab
2. Click on a deployment
3. Check build logs for errors
4. Look for Python function detection

### 3. Verify File Structure

Ensure these files exist:
- ✅ `api/index.py` (with `handler` variable)
- ✅ `api/requirements.txt`
- ✅ `vercel.json` in root
- ✅ `backend/app/main.py` (FastAPI app)

### 4. Test Locally with Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Run local dev server
vercel dev

# This will show you if the configuration works
```

### 5. Check Environment Variables

Ensure all required environment variables are set:
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SESSION_SECRET_KEY`

## Alternative Deployment Platforms

If Vercel continues to have issues, consider:

### 1. Railway
- Easy FastAPI deployment
- Free tier available
- GitHub integration

### 2. Render
- Simple deployment
- Free tier
- Good for FastAPI

### 3. Fly.io
- Edge deployment
- Docker support
- Free tier

### 4. DigitalOcean App Platform
- Easy setup
- Good documentation
- Paid plans

## Quick Fix: Try This First

1. **Delete `.vercel` folder** (if exists)
2. **Clear Vercel cache** in dashboard
3. **Try minimal vercel.json**:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/(.*)",
         "destination": "/api/index.py"
       }
     ]
   }
   ```
4. **Deploy via CLI**: `vercel --prod`

## Next Steps

1. Try Alternative 1 (builds + routes)
2. If that fails, try Alternative 2 (minimal)
3. Test with `vercel dev` locally
4. Check Vercel dashboard settings
5. Consider separate projects for frontend/backend

