@echo off
setlocal

REM Chuyen den thu muc chua file run.bat.
cd /d "%~dp0" || exit /b 1

REM Kiem tra moi truong Python.
if not exist ".venv\Scripts\python.exe" (
    echo Chua co moi truong .venv.
    echo Hay cai dat theo README truoc khi chay.
    exit /b 1
)

echo Starting AR-IMMS Backend...
echo API: http://localhost:5000
echo Swagger: http://localhost:5000/docs/
echo Press Ctrl+C to stop.
echo.

".venv\Scripts\python.exe" -m src.app

exit /b %ERRORLEVEL%