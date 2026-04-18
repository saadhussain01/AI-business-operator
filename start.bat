@echo off
REM ============================================================
REM AI Business Operator — Windows launcher
REM Usage: double-click start.bat or run from cmd
REM ============================================================

echo.
echo  AI Business Operator - Powered by Google Gemini (Free)
echo  ========================================================
echo.

cd /d "%~dp0"

REM Check .env
if not exist ".env" (
    echo WARNING: No .env file found. Copying from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your GEMINI_API_KEY
    echo Get a free key at: https://aistudio.google.com/apikey
    echo.
    pause
    exit /b 1
)

REM Create venv if missing
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt -q

mkdir reports 2>nul
mkdir memory\vector_store 2>nul

echo.
echo  Starting server on http://localhost:8000
echo  Open your browser to http://localhost:8000
echo  Press Ctrl+C to stop
echo.

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause
