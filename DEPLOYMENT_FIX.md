# Deployment Fix Guide

## Issue: Deployment Not Triggering

If your Vercel deployment is not being triggered, follow these steps:

## 🔍 Common Causes & Solutions

### 1. Git Integration Issues

**Check:**
- Is your repository connected to Vercel?
- Is the Vercel GitHub App installed?
- Are you pushing to the correct branch (usually `main` or `master`)?

**Solution:**
1. Go to Vercel Dashboard → Your Project → Settings → Git
2. Verify repository connection
3. Check branch settings

### 2. Commit Author Email Mismatch

**Check:**
```bash
git config user.email
```

**Solution:**
Ensure your Git email matches your Vercel account email:
```bash
git config --global user.email "your-vercel-email@example.com"
git config --global user.name "Your Name"
```

### 3. Manual Deployment Test

**Try deploying manually:**
1. Go to Vercel Dashboard
2. Click "Deployments"
3. Click "Redeploy" or "Deploy"
4. Check build logs for errors

### 4. Configuration Issues

**Check vercel.json:**
- Ensure file is valid JSON
- Check for syntax errors
- Verify paths are correct

**Current Configuration:**
- ✅ Python function: `api/index.py`
- ✅ Frontend build: `frontend/package.json` → `dist`
- ✅ Routes configured correctly

### 5. Build Command Issues

**Verify frontend build:**
```bash
cd frontend
npm install
npm run build
```

**Check if `dist` folder is created:**
```bash
ls frontend/dist
```

### 6. Environment Variables

**Required variables in Vercel Dashboard:**
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SESSION_SECRET_KEY`

**Set them:**
1. Vercel Dashboard → Project → Settings → Environment Variables
2. Add each variable
3. Redeploy

## 🚀 Quick Fix Steps

### Step 1: Verify Local Build
```bash
# Test frontend build
cd frontend
npm install
npm run build

# Verify dist folder exists
ls dist
```

### Step 2: Test Vercel CLI Locally
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Test deployment
vercel
```

### Step 3: Check Vercel Dashboard
1. Go to your project in Vercel Dashboard
2. Check "Deployments" tab
3. Look for any error messages
4. Check build logs

### Step 4: Force Redeploy
```bash
# Via CLI
vercel --prod --force

# Or via Dashboard
# Click "Redeploy" button
```

## 📋 Deployment Checklist

- [ ] Code is committed and pushed to Git
- [ ] Repository is connected to Vercel
- [ ] Branch matches Vercel settings
- [ ] `vercel.json` is valid JSON
- [ ] `api/index.py` exists and exports `handler`
- [ ] `api/requirements.txt` exists
- [ ] `frontend/package.json` has build script
- [ ] Environment variables are set
- [ ] Frontend builds successfully locally
- [ ] No syntax errors in configuration files

## 🐛 Debugging Commands

### Check Vercel Configuration
```bash
vercel inspect
```

### View Build Logs
```bash
vercel logs
```

### Test Function Locally
```bash
vercel dev
```

## 📝 Current Project Structure

```
LearningCoach/
├── api/
│   ├── index.py          ✅ Serverless function
│   ├── requirements.txt  ✅ Python deps
│   └── runtime.txt       ✅ Python version
├── backend/              ✅ FastAPI app
├── frontend/
│   ├── package.json      ✅ Has build script
│   └── dist/             ✅ Build output (after build)
└── vercel.json           ✅ Configuration
```

## ⚠️ Important Notes

1. **First Deployment**: May take longer (5-10 minutes)
2. **Build Time**: Frontend build + Python function setup
3. **Cold Starts**: First request after inactivity may be slow
4. **Logs**: Always check Vercel Dashboard → Functions → Logs

## 🔗 Useful Links

- [Vercel Deployment Troubleshooting](https://vercel.com/docs/deployments/troubleshooting)
- [Vercel Build Logs](https://vercel.com/docs/deployments/build-logs)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)

## 💡 Still Not Working?

1. **Check Vercel Status**: https://www.vercel-status.com/
2. **Review Build Logs**: Look for specific error messages
3. **Contact Support**: Vercel Dashboard → Help → Contact Support
4. **Share Error Messages**: Include full error logs when asking for help

