@echo off
setlocal

cd /d "%~dp0" || exit /b 1

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

echo Starting AR-IMMS Backend...
echo API:     http://localhost:5002
echo Health:  http://localhost:5002/health
echo Swagger: http://localhost:5002/docs/
echo Press Ctrl+C to stop.
echo.

".venv\Scripts\python.exe" -m flask --env-file .env.migration --app src.app run --host 127.0.0.1 --port 5002

pause