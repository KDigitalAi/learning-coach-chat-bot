@echo off
echo ========================================
echo Learning Coach - Local Development
echo ========================================
echo.

echo Starting Backend Server...
echo.
start "Learning Coach Backend" cmd /k "cd backend && start_server.bat"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend Server...
echo.
start "Learning Coach Frontend" cmd /k "python -m http.server 3000"

echo.
echo ========================================
echo Servers are starting!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend:   http://localhost:3000
echo.
echo Press any key to exit (servers will keep running)...
pause >nul

