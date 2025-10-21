@echo off
echo Personal Finance Tracker
echo ======================
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo [ERROR] Please run this script from the finance_tracker directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found
    echo Please run verify.bat first to set up dependencies
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    echo Please run verify.bat first
    pause
    exit /b 1
)

REM Run the application
echo Starting Personal Finance Tracker...
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start
    echo Please check the error messages above
    pause
)