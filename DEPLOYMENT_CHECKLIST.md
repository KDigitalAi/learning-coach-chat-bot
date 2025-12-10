# Vercel Deployment Checklist

## Pre-Deployment Checks ✅

### 1. Environment Variables
Make sure you've set these in Vercel Dashboard > Settings > Environment Variables:

- ✅ `OPENAI_API_KEY` - Your OpenAI API key
- ✅ `SUPABASE_URL` - Your Supabase project URL (e.g., `https://xxxxx.supabase.co`)
- ✅ `SUPABASE_KEY` - Your Supabase service role key (not anon key!)
- ✅ `SESSION_SECRET_KEY` (optional) - For session encryption

**Important:** 
- Use the **service role key** for `SUPABASE_KEY`, not the anon key
- The service role key has admin access and is needed for backend operations
- Never commit these keys to git (they're in `.gitignore`)

### 2. Database Setup
Ensure your Supabase database has the required tables:

1. **Run these SQL scripts in Supabase SQL Editor:**
   - `backend/database/schema.sql` - Creates main tables
   - `backend/database/vector_schema.sql` - Creates vector storage tables
   - `backend/database/vector_functions.sql` - Creates vector functions

2. **Enable pgvector extension:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 3. Files Checked
- ✅ `requirements.txt` - All dependencies consolidated (Vercel doesn't support `-r` flag)
- ✅ `vercel.json` - Correct routing configuration
- ✅ `api/index.py` - Proper handler setup with error handling
- ✅ `.vercelignore` - Excludes unnecessary files (chroma_db, __pycache__, etc.)

### 4. Code Fixes Applied
- ✅ Fixed `requirements.txt` to include all dependencies directly (removed `-r backend/requirements.txt`)
- ✅ Fixed bug in `config.py` (undefined `root_env` variable)
- ✅ Enhanced error handling in `api/index.py`
- ✅ Added logging for learning style personalization

## Deployment Steps

### 1. Install Vercel CLI (if not already installed)
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy
```bash
vercel
```

Or deploy to production:
```bash
vercel --prod
```

### 4. Set Environment Variables in Vercel Dashboard
1. Go to your project in Vercel Dashboard
2. Navigate to **Settings** > **Environment Variables**
3. Add each variable:
   - `OPENAI_API_KEY` = `your_openai_key`
   - `SUPABASE_URL` = `https://xxxxx.supabase.co`
   - `SUPABASE_KEY` = `your_service_role_key`
4. **Important:** Select **Production, Preview, and Development** for each variable
5. Click **Save**
6. **Redeploy** after adding variables (they're only loaded at build time)

## Post-Deployment Testing

### 1. Test Health Endpoint
```bash
curl https://your-app.vercel.app/health
```
Should return: `{"status": "healthy"}`

### 2. Test API Root
```bash
curl https://your-app.vercel.app/
```
Should return API info

### 3. Test Onboarding Endpoint
```bash
curl -X POST https://your-app.vercel.app/api/onboarding/consent \
  -H "Content-Type: application/json" \
  -d '{"consent": true, "onboarding_data": {"learningLevel": "Beginner", "interests": "Python", "goals": "Learn programming", "preferredStyle": "hands-on"}}'
```

### 4. Test Chat Endpoint
```bash
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?", "session_id": "test-123"}'
```

### 5. Test Frontend
1. Open your deployed URL in browser
2. Complete onboarding
3. Send a test message
4. Verify responses are personalized based on learning style

## Common Deployment Issues

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution:** The `api/index.py` should correctly add `backend` to Python path. If this fails, check that `backend/app/__init__.py` exists.

### Issue: "Missing environment variables"
**Solution:** 
- Verify all environment variables are set in Vercel Dashboard
- Make sure you selected **Production, Preview, and Development** for each variable
- **Redeploy** after adding variables

### Issue: "Import error" in Vercel logs
**Solution:** Check Vercel build logs. The error handler in `api/index.py` will show detailed error information including the Python path.

### Issue: Database connection errors
**Solution:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Make sure you're using the **service role key**, not the anon key
- Check that all database tables are created (run SQL scripts)

### Issue: "Failed to load resource" or CORS errors
**Solution:**
- Check that `vercel.json` routing is correct
- Verify CORS middleware in `backend/app/main.py` allows your frontend domain
- In production, update `allow_origins` in `main.py` to your actual domain

## Monitoring

### Check Vercel Logs
1. Go to Vercel Dashboard > Your Project > **Deployments**
2. Click on a deployment
3. Click **Functions** tab to see serverless function logs
4. Check for any errors or warnings

### Check Application Logs
The application logs important events:
- `✅ Profile loaded for session...` - Profile retrieval
- `✅ Using PROFILE-based learning style...` - Personalization active
- `⚠️ No personalization context available...` - Missing onboarding data

## Next Steps After Deployment

1. ✅ Update frontend `API_BASE` in `script.js` to use production URL (or keep it dynamic)
2. ✅ Test all features end-to-end
3. ✅ Monitor Vercel logs for any errors
4. ✅ Set up error tracking (optional: Sentry, LogRocket, etc.)
5. ✅ Configure custom domain (optional)

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Ensure database tables are created
5. Test endpoints individually using curl or Postman

