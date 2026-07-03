@echo off
cd /d "%~dp0\.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_client.ps1"
if errorlevel 1 (
    echo.
    echo Oshibka sborki.
    pause
    exit /b 1
)
pause
