# Local Development Guide

This guide explains how to run the Learning Coach application locally for development.

## Prerequisites

1. Python 3.8+ installed
2. Node.js and npm (optional, only if using a local HTTP server)
3. Environment variables set up (see `backend/ENV_SETUP.md`)

## Quick Start

### Option 1: Run Backend + Simple HTTP Server (Recommended for Quick Testing)

1. **Start the Backend Server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   
   Or use the batch file (Windows):
   ```bash
   cd backend
   start_server.bat
   ```

2. **Start a Simple HTTP Server for Frontend:**
   
   **Using Python:**
   ```bash
   # From project root
   python -m http.server 3000
   ```
   
   **Using Node.js (if you have it):**
   ```bash
   npx http-server -p 3000
   ```
   
   **Or just open `index.html` directly in your browser** (some features may not work due to CORS)

3. **Open in Browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Option 2: Use Vercel CLI (Best for Testing Production-like Environment)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Run Vercel Dev:**
   ```bash
   # From project root
   vercel dev
   ```

3. **Open the URL shown in terminal** (usually http://localhost:3000)

## Environment Variables

Create a `.env` file in the `backend` directory with:

```
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_service_role_key_here
```

## Troubleshooting

### Error: "Server returned HTML instead of JSON"

**Cause:** The backend server isn't running or the frontend can't reach it.

**Solution:**
1. Make sure the backend is running on port 8000
2. Check that `http://localhost:8000/health` returns `{"status":"healthy"}`
3. Verify the frontend is pointing to the correct API URL

### Error: "Failed to get response: 404"

**Cause:** The API route doesn't exist or the backend isn't running.

**Solution:**
1. Check that the backend server is running
2. Verify you can access http://localhost:8000/health
3. Check browser console for the exact error

### Error: "CORS policy" errors

**Cause:** Browser blocking requests due to CORS.

**Solution:**
- The backend already has CORS enabled for all origins
- If you're opening `index.html` directly (file://), use a local HTTP server instead
- Make sure the backend is running on `127.0.0.1:8000` or `localhost:8000`

### Backend won't start

**Common issues:**
- Missing dependencies: Run `pip install -r backend/requirements.txt`
- Wrong directory: Make sure you're running from the `backend` directory
- Port already in use: Change the port or stop the other service

## Development Workflow

1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Start Frontend Server:**
   ```bash
   # From project root
   python -m http.server 3000
   ```

3. **Open Browser:**
   - Navigate to http://localhost:3000
   - The frontend will automatically connect to http://localhost:8000 for API calls

4. **Make Changes:**
   - Backend changes: Server will auto-reload (thanks to `--reload` flag)
   - Frontend changes: Refresh the browser

## Testing API Endpoints

You can test the API directly:

```bash
# Health check
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test-123"}'
```

## Notes

- The frontend automatically detects if it's running on localhost and uses `http://localhost:8000` for API calls
- For production/Vercel deployment, it uses the same origin
- Make sure your `.env` file is in the `backend` directory, not the project root

