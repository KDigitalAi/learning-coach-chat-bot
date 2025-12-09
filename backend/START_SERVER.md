# How to Start the Backend Server

## Important: Run from the BACKEND directory!

The server MUST be run from the `backend` directory, NOT from the project root.

## Steps:

1. **Open a terminal/PowerShell**

2. **Activate Anaconda (if not already active):**
   ```powershell
   conda activate base
   ```

3. **Navigate to the backend directory:**
   ```powershell
   cd C:\Users\gowth\LearningCoach\backend
   ```
   **OR** if you're already in the LearningCoach folder:
   ```powershell
   cd backend
   ```

4. **Verify you're in the right directory:**
   ```powershell
   # You should see: C:\Users\gowth\LearningCoach\backend
   pwd
   ```

5. **Start the server:**
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **You should see:**
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Application startup complete.
   ```

## Alternative: Use the batch file

1. Navigate to `C:\Users\gowth\LearningCoach\backend`
2. Double-click `start_server.bat`

## Common Errors:

- **`ModuleNotFoundError: No module named 'app'`** 
  → You're running from the wrong directory! Make sure you're in the `backend` folder.

- **`ModuleNotFoundError: No module named 'supabase'`**
  → Install dependencies: `pip install -r requirements.txt`

