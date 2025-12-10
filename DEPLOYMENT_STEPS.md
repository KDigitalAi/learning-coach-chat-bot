# Final Deployment Steps

## ✅ All Fixes Applied

### Files Modified:
1. ✅ `vercel.json` - Removed `builds`, added modern `rewrites`
2. ✅ `backend/app/main.py` - Changed root endpoint to `/api` to avoid conflict

---

## Step-by-Step Deployment

### Step 1: Verify Local Changes
```bash
# Check vercel.json doesn't have "builds"
cat vercel.json

# Should see "rewrites" not "builds"
```

### Step 2: Commit Changes
```bash
git add vercel.json backend/app/main.py
git commit -m "Fix Vercel 404: Remove builds config, use modern rewrites, fix API root endpoint"
git push origin dev
```

### Step 3: Verify Environment Variables in Vercel
Go to Vercel Dashboard > Your Project > Settings > Environment Variables

Ensure these are set:
- ✅ `OPENAI_API_KEY`
- ✅ `SUPABASE_URL`
- ✅ `SUPABASE_KEY`

**Important:** Select **Production, Preview, and Development** for each.

### Step 4: Wait for Auto-Deploy
Vercel will automatically detect the new commit and deploy.

OR manually trigger:
```bash
vercel --prod
```

### Step 5: Test Endpoints

**Frontend (should load):**
```
https://your-app.vercel.app/
```

**API Health Check:**
```bash
curl https://your-app.vercel.app/health
# Should return: {"status": "healthy"}
```

**API Root:**
```bash
curl https://your-app.vercel.app/api
# Should return API info with endpoints
```

**Chat Endpoint:**
```bash
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

**Onboarding:**
```bash
curl -X POST https://your-app.vercel.app/api/onboarding/consent \
  -H "Content-Type: application/json" \
  -d '{"consent": true, "onboarding_data": {"learningLevel": "Beginner"}}'
```

---

## Expected Results

✅ **No more 404 errors**
✅ **Frontend loads at `/`**
✅ **API routes work at `/api/*`**
✅ **No warning about `builds`**
✅ **Static assets (CSS, JS) load correctly**

---

## Troubleshooting

### If Still Getting 404:

1. **Check Vercel Function Logs:**
   - Dashboard > Deployments > Your deployment > Functions tab
   - Look for import errors or handler issues

2. **Verify Handler Export:**
   - Check `api/index.py` has `handler = create_handler()` at module level

3. **Check Route Matching:**
   - API routes should match `/api/*` pattern
   - Frontend should match catch-all `/(.*)`

4. **Environment Variables:**
   - Ensure all required vars are set
   - Redeploy after adding variables

---

## Summary of Changes

### Why 404 Occurred:
1. Legacy `builds` config prevented proper static file serving
2. Route ordering issues
3. FastAPI root `/` endpoint conflicted with frontend

### What Was Fixed:
1. ✅ Removed `builds` - Use Vercel auto-detection
2. ✅ Added `rewrites` for API routes
3. ✅ Fixed route ordering (static assets first)
4. ✅ Changed FastAPI root to `/api` to avoid conflict
5. ✅ Added proper static asset caching

### Result:
- Modern Vercel configuration
- Proper routing for both frontend and backend
- No conflicts between API and frontend routes
- Optimized static asset serving

