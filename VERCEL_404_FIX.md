# Fixing 404 NOT_FOUND Error on Vercel

## Problem
Getting `404: NOT_FOUND` error when accessing API endpoints on Vercel.

## Root Causes

1. **Routing Configuration**: Vercel needs proper routing rules in `vercel.json`
2. **Handler Export**: The handler function must be properly exported
3. **Path Matching**: API routes need to match Vercel's expected format

## Solutions Applied

### 1. Updated `vercel.json`
- Changed destination from `/api/index` to `/api/index.py`
- Added route for `/health` endpoint
- Added route for root `/` to handle API root endpoint

### 2. Enhanced Handler Logging
- Added debug logging to see what events are received
- Better error messages with event details

### 3. Handler Export
- Added `__all__ = ['handler']` to ensure proper export

## Testing Steps

After redeploying, test these endpoints:

1. **Health Check:**
   ```bash
   curl https://your-app.vercel.app/health
   ```
   Should return: `{"status": "healthy"}`

2. **API Root:**
   ```bash
   curl https://your-app.vercel.app/
   ```
   Should return API info

3. **Onboarding:**
   ```bash
   curl -X POST https://your-app.vercel.app/api/onboarding/consent \
     -H "Content-Type: application/json" \
     -d '{"consent": true}'
   ```

4. **Chat:**
   ```bash
   curl -X POST https://your-app.vercel.app/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
   ```

## If Still Getting 404

### Check Vercel Function Logs:
1. Go to Vercel Dashboard > Your Project > Deployments
2. Click on the deployment
3. Go to **Functions** tab
4. Check logs for:
   - Import errors
   - Handler errors
   - Path mismatches

### Common Issues:

1. **Environment Variables Not Set**
   - Check Vercel Dashboard > Settings > Environment Variables
   - Ensure all required vars are set: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`

2. **Dependencies Not Installing**
   - Check build logs for pip install errors
   - Verify `requirements.txt` is correct

3. **Path Issues**
   - Vercel might be looking for `/api/index` but file is `/api/index.py`
   - Current config uses `/api/index.py` which should work

4. **Mangum Version**
   - Ensure `mangum==0.17.0` is in requirements.txt
   - Older versions might have compatibility issues

## Alternative: Try Newer Vercel Format

If the current config doesn't work, try this simplified `vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    },
    {
      "source": "/health",
      "destination": "/api/index.py"
    },
    {
      "source": "/",
      "destination": "/api/index.py"
    }
  ]
}
```

This uses the newer `rewrites` format instead of `builds` and `routes`.

## Debugging

Add this to `api/index.py` to see what's happening:

```python
# At the top of wrapped_handler function
print(f"Event received: {json.dumps(event, default=str)}")
print(f"Context: {context}")
```

This will show in Vercel function logs what events are being received.

