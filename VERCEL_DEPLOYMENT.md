# Vercel Deployment Guide

This guide explains how to deploy the Learning Coach project to Vercel.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional, for CLI deployment):
   ```bash
   npm install -g vercel
   ```

## 🚀 Deployment Steps

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub/GitLab/Bitbucket**
   - Make sure all changes are committed and pushed

2. **Import Project in Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your repository
   - Vercel will auto-detect the configuration

3. **Configure Environment Variables**
   - In Vercel Dashboard → Project Settings → Environment Variables
   - Add the following variables:
     ```
     OPENAI_API_KEY=your_openai_api_key
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your_service_role_key
     SESSION_SECRET_KEY=your_secret_key_here
     ALLOWED_ORIGINS=https://your-app.vercel.app (optional)
     ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete

### Method 2: Deploy via CLI

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy to Preview**:
   ```bash
   vercel
   ```

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

5. **Set Environment Variables**:
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add SUPABASE_URL
   vercel env add SUPABASE_KEY
   vercel env add SESSION_SECRET_KEY
   vercel env add ALLOWED_ORIGINS
   ```

## 📁 Project Structure for Vercel

```
LearningCoach/
├── api/
│   ├── index.py              # Vercel serverless function wrapper
│   └── requirements.txt      # Python dependencies for Vercel
├── backend/                  # FastAPI application
│   ├── app/
│   └── requirements.txt
├── frontend/                 # React + Vite application
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── vercel.json               # Vercel configuration
└── .vercelignore            # Files to ignore during deployment
```

## ⚙️ Configuration Details

### vercel.json
- **Builds**: 
  - Python serverless function from `api/index.py`
  - Static frontend build from `frontend/package.json`
- **Routes**:
  - `/api/*` → Python serverless function
  - Static assets → Frontend dist folder
  - All other routes → Frontend index.html (SPA routing)
- **Function Settings**:
  - Max duration: 60 seconds
  - Memory: 1024 MB

### API Function (api/index.py)
- Wraps FastAPI app with Mangum adapter
- Handles all `/api/*` routes
- Supports Server-Sent Events (SSE) for streaming

## 🔧 Environment Variables

Required environment variables in Vercel:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI models | `sk-...` |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase service role key | `eyJ...` |
| `SESSION_SECRET_KEY` | Secret key for sessions | `your-secret-key` |
| `ALLOWED_ORIGINS` | CORS allowed origins (optional) | `https://app.vercel.app` |

## 🐛 Troubleshooting

### Issue: Function timeout
- **Solution**: Increase `maxDuration` in `vercel.json` (max 60s on Pro plan)

### Issue: Import errors
- **Solution**: Ensure `PYTHONPATH` is set correctly in `vercel.json`

### Issue: CORS errors
- **Solution**: Set `ALLOWED_ORIGINS` environment variable with your Vercel domain

### Issue: Frontend not loading
- **Solution**: Check that `frontend/dist` is being built correctly
- Verify routes in `vercel.json` are correct

### Issue: API routes not working
- **Solution**: 
  - Check that `api/index.py` exists
  - Verify `api/requirements.txt` includes all dependencies
  - Check function logs in Vercel dashboard

## 📊 Monitoring

- **Function Logs**: Vercel Dashboard → Functions → View logs
- **Analytics**: Vercel Dashboard → Analytics
- **Performance**: Monitor function execution time and memory usage

## 🔄 Updating Deployment

1. **Make changes** to your code
2. **Commit and push** to your repository
3. **Vercel automatically deploys** (if connected via Git)
   - Or run `vercel --prod` for manual deployment

## 📝 Notes

- **Cold Starts**: First request may be slower (~1-2 seconds)
- **Function Limits**: 
  - Hobby plan: 10s timeout, 1024 MB memory
  - Pro plan: 60s timeout, 3008 MB memory
- **Database**: Supabase is external, so no changes needed
- **Vector Store**: Uses Supabase pgvector (no local ChromaDB in production)

## 🎯 Post-Deployment Checklist

- [ ] Environment variables are set
- [ ] API endpoints are accessible (`/api/health`)
- [ ] Frontend loads correctly
- [ ] Chat functionality works
- [ ] SSE streaming works
- [ ] CORS is configured correctly
- [ ] Custom domain is set (if applicable)

## 📚 Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/runtimes/python)
- [Mangum Documentation](https://mangum.io/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

