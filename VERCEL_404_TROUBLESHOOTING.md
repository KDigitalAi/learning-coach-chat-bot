# Vercel 404 Error - Troubleshooting Guide

## Current Status
- ✅ Code structure is correct
- ✅ Handler function exists and is properly formatted
- ✅ Rewrite configuration is set
- ❌ Getting 404 from Vercel (not from FastAPI)

## Diagnosis Steps

### Step 1: Check if Function is Deployed
**Action**: Go to Vercel Dashboard → Your Project → **Functions** tab

**What to look for**:
- Is `api/index.py` listed as a function?
- If YES → Function is deployed, issue is with routing/path extraction
- If NO → Function isn't being detected (see Step 2)

### Step 2: If Function NOT Listed
**Possible causes**:
1. Build failed (check Build Logs)
2. Python not detected (check if `requirements.txt` is in root)
3. File structure issue

**Solutions**:
- Check Vercel Build Logs for errors
- Verify `requirements.txt` exists in root directory
- Ensure `api/index.py` has `handler` function
- Check that file is committed to git

### Step 3: If Function IS Listed but Getting 404
**This means**: Function exists but rewrite/path extraction isn't working

**Test direct access**:
```
https://your-app.vercel.app/api/index
```
- If this works → Rewrite issue (path not being extracted)
- If this also 404s → Function execution issue

### Step 4: Check Function Logs
**Action**: Vercel Dashboard → Functions → `api/index.py` → Click on a request → View logs

**What to look for**:
- Log messages starting with "📥 Request:"
- What path is being extracted
- Any error messages
- Event structure

**Expected logs**:
```
✅ FastAPI initialized
📥 GET /api/health
📤 200
```

**If you see**:
- "❌ Init failed" → Import/dependency issue
- "❌ Error:" → Handler execution issue
- No logs at all → Function not being called

## Quick Fixes to Try

### Fix 1: Test Direct Function Access
Remove the rewrite temporarily and test:
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "public"
}
```

Then access: `https://your-app.vercel.app/api/index`
- If this works → Rewrite is the issue
- If this fails → Function detection issue

### Fix 2: Check Path Extraction
The handler tries multiple methods to get the original path. Check logs to see which method works (if any).

### Fix 3: Verify FastAPI Routes
Ensure all routes in `backend/app/main.py` have `/api/` prefix:
- ✅ `@app.get("/api/health")`
- ✅ `@app.get("/api/test")`
- ❌ `@app.get("/health")` (missing /api prefix)

## Current Configuration Summary

**Files**:
- `api/index.py` - Main handler (has `handler` function)
- `api/index.json` - Function config (memory, timeout)
- `vercel.json` - Rewrite: `/api/(.*)` → `/api/index`
- `requirements.txt` - Python dependencies (root level)

**Handler Logic**:
1. Extracts original path from headers/query/event
2. Updates event with correct path
3. Passes to Mangum → FastAPI
4. Returns response

## Next Steps After Deployment

1. **Check Functions Tab** - Is `api/index.py` listed?
2. **Test `/api/index` directly** - Does it work?
3. **Check Function Logs** - What path/headers are received?
4. **Test `/api/health`** - Does rewrite work?

Based on the results, we can adjust the path extraction logic.

