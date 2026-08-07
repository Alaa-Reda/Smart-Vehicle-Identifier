@echo off
setlocal

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

if not exist "%VENV%\Scripts\activate.bat" (
    echo [ERROR] Virtual Environment not found:
    echo %VENV%
    pause
    exit /b 1
)

echo ============================================
echo Starting Backend...
echo ============================================

start "SVI Backend" cmd /k ^
"call "%VENV%\Scripts\activate.bat" && cd /d "%BACKEND%" && python run.py"

timeout /t 5 >nul

echo ============================================
echo Starting Frontend...
echo ============================================

start "SVI Frontend" cmd /k ^
"call "%VENV%\Scripts\activate.bat" && cd /d "%FRONTEND%" && streamlit run app.py"

exit