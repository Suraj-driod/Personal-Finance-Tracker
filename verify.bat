@echo off
echo Personal Finance Tracker - Dependency Verification
echo ================================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo [OK] Python is installed
)

REM Check if we're in the right directory
echo Checking project files...
if not exist "main.py" (
    echo [ERROR] Please run this script from the finance_tracker directory
    pause
    exit /b 1
) else (
    echo [OK] Project files found
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [WARNING] Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    ) else (
        echo [OK] Virtual environment created
    )
) else (
    echo [OK] Virtual environment exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
) else (
    echo [OK] Virtual environment activated
)

REM Check if requirements are installed
echo Checking Python packages...
pip show mysql-connector-python >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Required packages not installed
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements
        pause
        exit /b 1
    ) else (
        echo [OK] Requirements installed
    )
) else (
    echo [OK] Required packages are installed
)

REM Check database connection
echo Checking database connection...
python -c "from db.connection import db; print('Database connection:', 'OK' if db.get_connection() else 'FAILED')" 2>nul
if errorlevel 1 (
    echo [WARNING] Database connection failed
    echo Please check your MySQL server and credentials in db/connection.py
) else (
    echo [OK] Database connection successful
)

echo.
echo ================================================
echo [SUCCESS] All dependencies verified!
echo You can now run the application with: run.bat
echo ================================================
pause