@echo off
setlocal

cd /d "%~dp0" || exit /b 1

if not exist ".venv\Scripts\python.exe" (
    echo Chua co moi truong Python .venv cho Agent.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Khong tim thay file .env cua Agent.
    pause
    exit /b 1
)

echo Starting AR-IMMS Collector Agent...
echo Backend: cau hinh trong .env
echo Press Ctrl+C to stop.
echo.

".venv\Scripts\python.exe" agent.py

pause