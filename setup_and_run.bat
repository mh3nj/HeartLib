@echo off
title HeartLib – Library Management System Auto-Setup
color 07

setlocal enabledelayedexpansion

REM Store the starting directory
set STARTDIR=%CD%

echo    HeartLib – Library with a Heart
echo         Auto-Setup & Launcher
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check Python version (must be 3.10+)
for /f "tokens=2 delims= " %%v in ('python --version') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if !MAJOR! LSS 3 (
    echo [ERROR] Python 3.10+ is required. Detected: !PYVER!
    echo.
    pause
    exit /b 1
)
if !MAJOR! EQU 3 if !MINOR! LSS 10 (
    echo [ERROR] Python 3.10+ is required. Detected: !PYVER!
    echo.
    pause
    exit /b 1
)

echo [OK] Python found: !PYVER!
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available!
    echo Please ensure Python is installed correctly
    pause
    exit /b 1
)
echo [OK] pip found
echo.

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [SETUP] Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        cd /d "%STARTDIR%"
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo [SETUP] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    cd /d "%STARTDIR%"
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Check for requirements.txt
if not exist requirements.txt (
    echo [ERROR] requirements.txt not found!
    echo Please make sure you are in the correct HeartLib directory.
    cd /d "%STARTDIR%"
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo [INSTALL] Installing/updating dependencies...
echo This may take a moment...
echo.

python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

if errorlevel 1 (
    echo [WARNING] Some dependencies failed to install.
    echo Trying to continue anyway...
) else (
    echo [OK] All dependencies installed successfully
)

echo.
echo [SETUP] Checking database...
if not exist "heartlib.db" (
    echo [INFO] Creating new database (will be created on first run)
) else (
    echo [INFO] Existing database found
)

echo.
echo    Setup Complete! Starting HeartLib...
echo.

REM Start the application
python main.py

echo.
echo [DONE] HeartLib has been closed.
echo You can re-run this file anytime to update and launch.
echo.
echo Press any key to exit...
pause >nul

REM Return to original directory
cd /d "%STARTDIR%"
endlocal