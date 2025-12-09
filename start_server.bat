@echo off
REM Change to the script's directory (backend folder)
cd /d %~dp0
echo Starting Learning Coach Backend Server...
echo Current directory: %CD%
echo.

REM Try to use Anaconda Python (which has all dependencies)
if exist "%CONDA_PREFIX%\python.exe" (
    echo Using Anaconda Python...
    "%CONDA_PREFIX%\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
) else (
    REM Check if conda is available
    where conda >nul 2>&1
    if %errorlevel% == 0 (
        echo Activating Anaconda base environment...
        call conda activate base
        python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    ) else (
        echo Using system Python...
        python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    )
)
