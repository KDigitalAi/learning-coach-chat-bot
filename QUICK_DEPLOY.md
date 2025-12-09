# Quick Deployment Guide

If automatic deployment isn't working, try these steps in order:

## Method 1: Vercel CLI (Recommended)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login
```bash
vercel login
```

### Step 3: Deploy
```bash
# Deploy to preview
vercel

# Or deploy to production
vercel --prod
```

### Step 4: Test Locally First
```bash
# Test the configuration locally
vercel dev
```
This will start a local server and show you if there are any configuration issues.

## Method 2: Try Alternative Configurations

### Option A: Use Builds + Routes Format

1. Backup current vercel.json:
```bash
cp vercel.json vercel.json.backup
```

2. Use alternative configuration:
```bash
cp vercel-alternative-1.json vercel.json
```

3. Deploy:
```bash
vercel --prod
```

### Option B: Use Minimal Configuration

1. Use minimal config:
```bash
cp vercel-alternative-2.json vercel.json
```

2. Deploy:
```bash
vercel --prod
```

## Method 3: Manual Vercel Dashboard Configuration

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. **Important Settings**:
   - **Root Directory**: Leave empty (or `/`)
   - **Framework Preset**: Select "Other"
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm ci`
5. Click "Deploy"

## Method 4: Check Vercel Project Settings

If project already exists:

1. Go to Project Settings → General
2. Verify:
   - **Root Directory**: Empty or `/`
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Framework Preset**: Other
3. Save and redeploy

## Method 5: Use Deploy Hook

1. Go to Project Settings → Deploy Hooks
2. Create a new hook
3. Use the hook URL:
```bash
curl -X POST "YOUR_DEPLOY_HOOK_URL"
```

## Troubleshooting

### Issue: "No deployments found"
- Check if Git integration is connected
- Verify you have push access to the repository
- Try deploying via CLI instead

### Issue: "Build failed"
- Check build logs in Vercel dashboard
- Verify all dependencies are in `api/requirements.txt`
- Check for syntax errors in Python code

### Issue: "Function not found"
- Verify `api/index.py` exists
- Check that `handler` variable is exported
- Ensure `api/requirements.txt` includes all dependencies

### Issue: "Routes not working"
- Check `vercel.json` routes/rewrites configuration
- Verify API routes match FastAPI route prefixes
- Test with `vercel dev` locally

## Quick Test Commands

```bash
# Test configuration locally
vercel dev

# Check what Vercel sees
vercel inspect

# List deployments
vercel ls

# View deployment logs
vercel logs [deployment-url]
```

## Alternative: Deploy Frontend and Backend Separately

### Frontend Only (Static Site)
1. Create new Vercel project
2. Root: `frontend/`
3. Framework: Vite
4. Build: `npm run build`
5. Output: `dist/`

### Backend Only (Serverless Function)
1. Create new Vercel project  
2. Root: Project root
3. Framework: Other
4. Functions: Auto-detect from `api/` directory

Then update frontend `VITE_API_URL` to point to backend URL.

## Next Steps

1. ✅ Try `vercel dev` to test locally
2. ✅ Try `vercel --prod` to deploy
3. ✅ Check Vercel dashboard for errors
4. ✅ Review build logs
5. ✅ Try alternative configurations

If none of these work, the issue might be:
- Vercel account permissions
- Git repository access
- Project configuration in dashboard
- Missing environment variables

Consider using Railway, Render, or Fly.io as alternatives if Vercel continues to have issues.

