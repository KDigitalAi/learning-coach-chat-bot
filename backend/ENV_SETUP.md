# Environment Setup

Create a `.env` file in the `backend/` directory with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_service_role_key_here

# Session Configuration
SESSION_SECRET_KEY=your_random_secret_key_here_change_this_in_production
```

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and paste it in your `.env` file

## Supabase Setup

### Step 1: Create Supabase Account and Project

1. Go to https://supabase.com
2. Sign up or sign in
3. Click "New Project"
4. Fill in project details:
   - **Name**: Your project name
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to your users
5. Wait for project to be created (2-3 minutes)

### Step 2: Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Find your **Project URL** (e.g., `https://xxxxx.supabase.co`)
3. Find your **service_role** key (NOT the anon key - this is for backend use)
4. Copy both values to your `.env` file:
   - `SUPABASE_URL` = Project URL
   - `SUPABASE_KEY` = service_role key

### Step 3: Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Open the file `backend/database/schema.sql` from this project
3. Copy and paste the entire SQL content into the SQL Editor
4. Click **Run** to execute the schema
5. Verify tables are created by checking **Table Editor**

### Step 4: Verify Setup

After running the schema, you should see these tables:
- `user_sessions`
- `user_profiles`
- `conversation_history`
- `learning_patterns`

## Session Secret Key

Generate a random secret key for session management:

```bash
# On Linux/Mac:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# On Windows PowerShell:
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

Copy the generated key to `SESSION_SECRET_KEY` in your `.env` file.

## Important Notes

- **Never commit your `.env` file** to version control
- **Use service_role key** for backend (not anon key)
- **Keep your Supabase password safe** - you'll need it for direct database access
- The schema includes indexes for performance optimization
