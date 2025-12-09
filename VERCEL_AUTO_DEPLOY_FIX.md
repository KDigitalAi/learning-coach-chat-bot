# Vercel Auto-Deployment Fix Guide

## ✅ vercel.json Configuration - FIXED

The `vercel.json` has been optimized for automatic deployments:
- ✅ Added explicit Python runtime specification (`python3.11`)
- ✅ Cleaned up configuration format
- ✅ Proper routing for API and frontend
- ✅ Function settings configured correctly

## 🔧 Vercel Dashboard Configuration (REQUIRED)

For automatic deployments to work, you **MUST** configure these in the Vercel Dashboard:

### Step 1: Connect Git Repository

1. Go to **Vercel Dashboard**: https://vercel.com/dashboard
2. Select your project (or create new if doesn't exist)
3. Go to **Settings** → **Git**
4. Click **"Connect Git Repository"** if not connected
5. Select your GitHub repository
6. Authorize Vercel GitHub App if prompted

### Step 2: Configure Branch Settings

1. In **Settings** → **Git**
2. Find **"Production Branch"** setting
3. **IMPORTANT**: Set it to `dev1` (or the branch you want to deploy)
4. By default, Vercel watches `main` or `master`
5. If your code is on `dev1`, Vercel won't auto-deploy unless you configure it

### Step 3: Verify Branch Configuration

**Option A: Set dev1 as Production Branch**
- Settings → Git → Production Branch → Change to `dev1`
- This will deploy `dev1` branch to production URL

**Option B: Configure Preview Deployments for dev1**
- Settings → Git → Preview Deployments
- Ensure `dev1` is enabled for preview deployments
- This will create preview URLs for each push to `dev1`

### Step 4: Check Webhook Status

1. Go to **GitHub** → Your Repository → **Settings** → **Webhooks**
2. Look for `vercel.com` webhook
3. Verify it's **Active** and has recent deliveries
4. If missing or inactive, reconnect Git in Vercel Dashboard

### Step 5: Verify Commit Email

Your Git commit email must match your Vercel account email:

```bash
# Check your Git email
git config user.email

# If it doesn't match Vercel account email, update it:
git config --global user.email "your-vercel-email@example.com"
```

## 🚨 Common Issues & Solutions

### Issue 1: "Deployment not triggering"

**Cause**: Branch mismatch
- Vercel is watching `main`, but you're pushing to `dev1`

**Solution**: 
- Go to Vercel Dashboard → Settings → Git
- Change Production Branch to `dev1`
- OR enable Preview Deployments for `dev1`

### Issue 2: "Git repository not connected"

**Cause**: Repository not linked to Vercel project

**Solution**:
- Vercel Dashboard → Settings → Git → Connect Git Repository
- Select your repository and authorize

### Issue 3: "Webhook not working"

**Cause**: GitHub webhook not active or misconfigured

**Solution**:
- GitHub → Settings → Webhooks → Check vercel.com webhook
- If missing, reconnect Git in Vercel Dashboard
- Vercel will automatically create the webhook

### Issue 4: "Build fails"

**Cause**: Configuration or environment variable issues

**Solution**:
- Check build logs in Vercel Dashboard
- Verify environment variables are set:
  - `OPENAI_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `SESSION_SECRET_KEY`

## 📋 Quick Checklist

Before expecting auto-deployments:

- [ ] Git repository connected in Vercel Dashboard
- [ ] Branch configured correctly (`dev1` set as production or preview)
- [ ] Webhook active in GitHub
- [ ] Commit email matches Vercel account email
- [ ] Environment variables set in Vercel Dashboard
- [ ] `vercel.json` is valid (✅ Already fixed)
- [ ] Project exists in Vercel Dashboard

## 🧪 Test Auto-Deployment

After configuring the dashboard:

1. Make a small change to your code
2. Commit and push to `dev1` branch:
   ```bash
   git add .
   git commit -m "Test auto-deployment"
   git push origin dev1
   ```
3. Check Vercel Dashboard → Deployments
4. You should see a new deployment starting automatically

## 💡 Why Manual Deployment Works But Auto Doesn't

If manual deployment works but auto-deployment doesn't:

- ✅ Your `vercel.json` is correct (manual deploy proves this)
- ❌ Git integration is not properly configured
- ❌ Branch settings don't match your push branch
- ❌ Webhook is not active

**The fix is in the Vercel Dashboard, not in your code!**

## 🔗 Important Links

- Vercel Dashboard: https://vercel.com/dashboard
- Project Settings: https://vercel.com/dashboard → Your Project → Settings
- Git Settings: https://vercel.com/dashboard → Your Project → Settings → Git
- Deployments: https://vercel.com/dashboard → Your Project → Deployments

