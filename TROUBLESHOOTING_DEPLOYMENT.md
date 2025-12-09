# Troubleshooting: Deployment Not Triggering

## 🔍 Quick Diagnosis

If your Vercel deployment is not being triggered, check these common issues:

## 1. Git Integration Issues

### Check Repository Connection
1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Git**
2. Verify your repository is connected
3. Check if the correct branch is selected (usually `main` or `master`)

### Verify Vercel GitHub App
- Ensure Vercel GitHub App is installed
- Check repository permissions
- Reconnect if needed

## 2. Commit Author Email

Your Git commit email must match your Vercel account email.

**Check your Git email:**
```bash
git config user.email
```

**Update if needed:**
```bash
git config --global user.email "your-vercel-email@example.com"
git config --global user.name "Your Name"
```

**Then make a new commit:**
```bash
git commit --amend --reset-author
git push --force
```

## 3. Branch Configuration

**Check which branch Vercel is watching:**
1. Vercel Dashboard → Project → Settings → Git
2. Verify "Production Branch" matches your branch name
3. Default branches: `main`, `master`, or `production`

**Push to correct branch:**
```bash
git branch  # Check current branch
git push origin main  # Or master, depending on your setup
```

## 4. Manual Deployment Test

**Try deploying manually:**
1. Go to Vercel Dashboard
2. Click **"Deployments"** tab
3. Click **"Redeploy"** or **"Deploy"**
4. Check build logs for errors

**Or via CLI:**
```bash
vercel --prod
```

## 5. Configuration File Issues

### Verify vercel.json
- ✅ File exists at project root
- ✅ Valid JSON (no syntax errors)
- ✅ All paths are correct

**Test JSON validity:**
```bash
# On Linux/Mac
cat vercel.json | python -m json.tool

# Or use online JSON validator
```

### Current Configuration Status
- ✅ `api/index.py` exists
- ✅ `api/requirements.txt` exists
- ✅ `frontend/package.json` has build script
- ✅ `vercel.json` is configured

## 6. Build Command Issues

**Test frontend build locally:**
```bash
cd frontend
npm install
npm run build
```

**Verify dist folder is created:**
```bash
ls frontend/dist  # Should show index.html and assets/
```

## 7. Missing Environment Variables

**Required variables:**
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SESSION_SECRET_KEY`

**Set in Vercel Dashboard:**
1. Project → Settings → Environment Variables
2. Add each variable
3. Select environments (Production, Preview, Development)
4. Click "Save"
5. **Redeploy** (variables don't apply to existing deployments)

## 8. Project Detection Issues

**If Vercel doesn't detect your project:**
1. Delete and re-import the project
2. Or use Vercel CLI:
   ```bash
   vercel
   ```
3. Follow prompts to link project

## 9. Check Build Logs

**View logs in Dashboard:**
1. Go to Deployments tab
2. Click on a deployment
3. Check "Build Logs" for errors

**Common errors:**
- Missing dependencies
- Build command failures
- Path errors
- Environment variable issues

## 10. Force Redeploy

**Via Dashboard:**
1. Go to Deployments
2. Click "..." menu on latest deployment
3. Select "Redeploy"

**Via CLI:**
```bash
vercel --prod --force
```

## 🚀 Step-by-Step Fix

### Step 1: Verify Local Setup
```bash
# Test frontend build
cd frontend
npm install
npm run build

# Check if dist folder exists
ls dist
```

### Step 2: Check Git Configuration
```bash
# Verify Git email matches Vercel account
git config user.email

# Check current branch
git branch

# Verify commits are pushed
git log --oneline -5
```

### Step 3: Test Vercel CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Test deployment
vercel
```

### Step 4: Check Vercel Dashboard
1. Go to your project
2. Check "Deployments" tab
3. Look for error messages
4. Check "Settings" → "Git" for connection status

### Step 5: Set Environment Variables
1. Vercel Dashboard → Project → Settings → Environment Variables
2. Add all required variables
3. Save and redeploy

## 📋 Deployment Checklist

Before deploying, ensure:

- [ ] Code is committed: `git status` shows clean
- [ ] Code is pushed: `git push origin main`
- [ ] Repository connected in Vercel Dashboard
- [ ] Branch matches Vercel settings
- [ ] `vercel.json` exists and is valid JSON
- [ ] `api/index.py` exists
- [ ] `api/requirements.txt` exists
- [ ] `frontend/package.json` has `build` script
- [ ] Frontend builds successfully: `cd frontend && npm run build`
- [ ] Environment variables are set in Vercel
- [ ] No syntax errors in configuration

## 🐛 Common Error Messages

### "Build failed"
- Check build logs for specific error
- Verify all dependencies are in `package.json` or `requirements.txt`
- Check build command works locally

### "Function not found"
- Verify `api/index.py` exists
- Check `handler` is exported correctly
- Verify `api/requirements.txt` includes all dependencies

### "Static files not found"
- Check `frontend/dist` folder exists after build
- Verify `distDir` in `vercel.json` matches actual folder name
- Ensure build command runs successfully

### "Environment variable missing"
- Set all required variables in Vercel Dashboard
- Redeploy after setting variables

## 🔗 Useful Commands

```bash
# Check Vercel project status
vercel inspect

# View deployment logs
vercel logs

# Test locally
vercel dev

# Deploy to production
vercel --prod

# Force redeploy
vercel --prod --force
```

## 💡 Still Not Working?

1. **Check Vercel Status**: https://www.vercel-status.com/
2. **Review Full Build Logs**: Look for specific error messages
3. **Contact Support**: 
   - Vercel Dashboard → Help → Contact Support
   - Include: error logs, vercel.json, project structure
4. **Community Help**: https://github.com/vercel/vercel/discussions

## 📝 Current Project Status

✅ **Configuration Files:**
- `vercel.json` - Configured
- `api/index.py` - Handler exported
- `api/requirements.txt` - Dependencies listed
- `api/runtime.txt` - Python version specified

✅ **Build Test:**
- Frontend builds successfully
- `dist` folder created with assets

✅ **Project Structure:**
```
LearningCoach/
├── api/
│   ├── index.py ✅
│   ├── requirements.txt ✅
│   └── runtime.txt ✅
├── backend/ ✅
├── frontend/
│   ├── package.json ✅
│   └── dist/ ✅ (after build)
└── vercel.json ✅
```

## 🎯 Next Steps

1. **Verify Git integration** in Vercel Dashboard
2. **Set environment variables** if not done
3. **Try manual deployment** via Dashboard
4. **Check build logs** for specific errors
5. **Contact support** with error details if issue persists

