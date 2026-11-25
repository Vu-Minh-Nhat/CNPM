@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Chua co moi truong Python .venv.
    pause
    exit /b 1
)

if not exist ".env.migration" (
    echo Khong tim thay file .env.migration.
    pause
    exit /b 1
)

echo Starting AR-IMMS Backend for Mobile...
echo Port: 5002
echo Press Ctrl+C to stop.
echo.

".venv\Scripts\python.exe" -m flask --env-file .env.migration --app src.app run --host 0.0.0.0 --port 5002

pause