# Quick Start Guide

## Start the Application Locally

### Step 1: Start the Backend Server

Open a terminal/PowerShell and run:

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Or use the batch file (Windows):**
```bash
cd backend
start_server.bat
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Step 2: Start the Frontend Server

Open a **NEW** terminal/PowerShell window and run:

```bash
# From project root directory
python -m http.server 3000
```

**Or use the startup script (Windows):**
```bash
start_local.bat
```

### Step 3: Open in Browser

1. Open your browser
2. Go to: **http://localhost:3000**
3. You should see the Learning Coach chat interface

### Step 4: Test the Backend

Before using the chat, verify the backend is working:

1. Open: **http://localhost:8000/health**
2. You should see: `{"status":"healthy"}`

## Troubleshooting

### Error: "I can't connect to the server"

**Solution:**
1. Make sure the backend is running on port 8000
2. Check: http://localhost:8000/health
3. If it doesn't work, the backend isn't running - go back to Step 1

### Error: "ModuleNotFoundError"

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Error: "Port already in use"

**Solution:**
- Backend (8000): Change the port in the uvicorn command
- Frontend (3000): Use a different port: `python -m http.server 3001`

### Suggestion Buttons Not Showing

**Solution:**
1. Refresh the browser (Ctrl+F5 or Cmd+Shift+R)
2. Check browser console for errors (F12)
3. Make sure you're using the latest `script.js` file

## Environment Variables

Make sure you have a `.env` file in the `backend` directory with:

```
OPENAI_API_KEY=your_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
```

## Quick Test

1. ✅ Backend running: http://localhost:8000/health
2. ✅ Frontend running: http://localhost:3000
3. ✅ Complete onboarding (click suggestion buttons or type answers)
4. ✅ Ask a question about FastAPI or Python

## Need Help?

- Check `LOCAL_DEVELOPMENT.md` for detailed instructions
- Check backend logs in the terminal where uvicorn is running
- Check browser console (F12) for frontend errors

