# Redis to Supabase Migration - Step-by-Step Guide

Follow these steps to complete the migration and get your Learning Coach running with Supabase.

## Step 1: Install Supabase Python Package

Open a terminal/PowerShell in the `backend` directory and install the new dependency:

```bash
cd C:\Users\gowth\LearningCoach\backend
pip install supabase==2.0.0
```

Or if you're using Anaconda:
```bash
conda activate base
pip install supabase==2.0.0
```

**Verify installation:**
```bash
python -c "import supabase; print('Supabase installed successfully!')"
```

---

## Step 2: Create Supabase Account and Project

1. **Go to Supabase:**
   - Visit https://supabase.com
   - Click "Sign Up" or "Start your project" (if you don't have an account)

2. **Create a New Project:**
   - Click "New Project"
   - Fill in:
     - **Name**: `learning-coach` (or any name you prefer)
     - **Database Password**: Choose a strong password (SAVE THIS - you'll need it!)
     - **Region**: Choose closest to your location
   - Click "Create new project"
   - Wait 2-3 minutes for project to be created

3. **Get Your Credentials:**
   - Once project is ready, go to **Settings** (gear icon) → **API**
   - Find these values:
     - **Project URL**: Copy this (looks like `https://xxxxx.supabase.co`)
     - **service_role key**: Click "Reveal" and copy the **service_role** key (NOT the anon key)
     - Keep these safe - you'll need them for Step 4

---

## Step 3: Run Database Schema

1. **Open SQL Editor:**
   - In Supabase dashboard, click **SQL Editor** (left sidebar)
   - Click **New Query**

2. **Copy and Run Schema:**
   - Open the file: `backend/database/schema.sql` in your code editor
   - Copy **ALL** the SQL content
   - Paste it into the Supabase SQL Editor
   - Click **Run** (or press Ctrl+Enter)

3. **Verify Tables Created:**
   - Go to **Table Editor** (left sidebar)
   - You should see these tables:
     - ✅ `user_sessions`
     - ✅ `user_profiles`
     - ✅ `conversation_history`
     - ✅ `learning_patterns`

---

## Step 4: Update .env File

1. **Open your `.env` file:**
   - Location: `backend/.env`

2. **Remove old Redis variables:**
   - Delete these lines (if they exist):
     ```
     REDIS_HOST=localhost
     REDIS_PORT=6379
     REDIS_PASSWORD=
     REDIS_DB=0
     ```

3. **Add Supabase variables:**
   - Add these lines:
     ```env
     # Supabase Configuration
     SUPABASE_URL=https://your-project-id.supabase.co
     SUPABASE_KEY=your_service_role_key_here
     ```
   - Replace:
     - `your-project-id.supabase.co` with your actual Project URL from Step 2
     - `your_service_role_key_here` with your actual service_role key from Step 2

4. **Your final `.env` should look like:**
   ```env
   # OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here

   # Supabase Configuration
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   # Session Configuration
   SESSION_SECRET_KEY=your_random_secret_key_here
   ```

---

## Step 5: Test the Connection

1. **Test Supabase connection:**
   ```bash
   cd backend
   python -c "from app.utils.database import get_supabase_client; client = get_supabase_client(); print('✅ Supabase connected successfully!')"
   ```

2. **If you see an error:**
   - Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
   - Make sure you're using the **service_role** key (not anon key)
   - Verify Supabase project is active

---

## Step 6: Start the Backend Server

1. **Start the server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **You should see:**
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   INFO:     Application startup complete.
   ```

3. **Test the health endpoint:**
   - Open browser: http://localhost:8000/health
   - Should return: `{"status":"healthy"}`

---

## Step 7: Test the Application

1. **Start Frontend (if not already running):**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test the flow:**
   - Open http://localhost:3000
   - Complete onboarding (5 steps)
   - Send a chat message
   - Check Supabase dashboard → Table Editor:
     - `user_sessions` should have a new row
     - `user_profiles` should have your onboarding data
     - `conversation_history` should have your messages
     - `learning_patterns` should be created after a few messages

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'supabase'"
**Solution:** Run `pip install supabase==2.0.0` in the backend directory

### Error: "Invalid API key" or "401 Unauthorized"
**Solution:** 
- Make sure you're using the **service_role** key (not anon key)
- Check that the key is copied correctly (no extra spaces)

### Error: "Connection refused" or "Network error"
**Solution:**
- Verify `SUPABASE_URL` is correct in `.env`
- Check that your Supabase project is active (not paused)

### Tables not created
**Solution:**
- Make sure you ran ALL the SQL from `schema.sql`
- Check for any SQL errors in Supabase SQL Editor
- Verify you have the right permissions in Supabase

### No data in tables after testing
**Solution:**
- Make sure you completed onboarding and gave consent
- Check that `has_consent` is `true` in `user_sessions` table
- Verify backend is using the correct Supabase credentials

---

## Success Checklist

After completing all steps, verify:

- ✅ Supabase package installed
- ✅ Supabase project created
- ✅ Database schema run successfully
- ✅ `.env` file updated with Supabase credentials
- ✅ Backend server starts without errors
- ✅ Health endpoint returns `{"status":"healthy"}`
- ✅ Frontend connects to backend
- ✅ Onboarding works
- ✅ Chat messages are saved to Supabase
- ✅ Learning patterns are created after conversations

---

## What's Different Now?

**Before (Redis):**
- Data expired after 30 days
- No learning pattern analysis
- Temporary storage only

**After (Supabase):**
- ✅ Persistent storage (no expiry)
- ✅ Learning pattern analysis (RAG feature)
- ✅ Better querying capabilities
- ✅ All data stored in PostgreSQL
- ✅ Enhanced personalization based on learning patterns

---

## Need Help?

If you encounter any issues:
1. Check the error message in the terminal
2. Verify your `.env` file is correct
3. Check Supabase dashboard for any errors
4. Make sure all dependencies are installed

Good luck! 🚀

