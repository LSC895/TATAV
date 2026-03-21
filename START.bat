@echo off
echo ============================================
echo   TATAV 1 - AI Commander Battle
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo [1/3] Installing Python packages...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed. Check your internet connection.
    pause
    exit /b 1
)

REM Check Ollama
echo [2/3] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama not running. Starting Ollama...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
)

REM Pull model if not present
echo [3/3] Checking AI model (mistral)...
ollama pull mistral

REM Start server
echo.
echo ============================================
echo   Starting Tatav 1 server...
echo   Open: http://localhost:8000
echo   Press Ctrl+C to stop
echo ============================================
echo.
start "" http://localhost:8000
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

pause
