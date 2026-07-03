@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PYEXE="
if exist "runtime\python\python.exe" set "PYEXE=runtime\python\python.exe"
if not defined PYEXE if exist ".venv\Scripts\python.exe" set "PYEXE=.venv\Scripts\python.exe"

if not defined PYEXE (
    where py >nul 2>&1
    if errorlevel 1 (
        echo.
        echo Ne najdena papka runtime\python.
        echo Raspakujte programmu iz polnogo arhiva ot postavshchika.
        echo.
        pause
        exit /b 1
    )
)

start "" cmd /c "timeout /t 4 /nobreak >nul && start http://localhost:8501"

if defined PYEXE (
    "%PYEXE%" -m streamlit run salesapp\ui.py --server.headless true --browser.gatherUsageStats false
) else (
    py -3 -m streamlit run salesapp\ui.py --server.headless true --browser.gatherUsageStats false
)

pause
