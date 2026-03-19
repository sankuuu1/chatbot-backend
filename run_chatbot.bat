@echo off
echo ==================================================
echo      Chatbot Backend Setup & Startup
echo ==================================================

echo [1/2] Installing required libraries...
:: Try using 'py' launcher first
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 'py' command failed, trying 'python'...
    python -m pip install -r requirements.txt
)

echo.
echo [2/2] Starting Server...
echo.
:: Try run using 'py' first
py app.py
if %errorlevel% neq 0 (
    echo 'py' failed, trying 'python'...
    python app.py
)

pause
