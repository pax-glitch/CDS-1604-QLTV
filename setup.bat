@echo off
echo ====================================
echo Thu vien MGX - Setup Script
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Create directories
if not exist "database\" mkdir database
if not exist "static\uploads\avatars\" mkdir static\uploads\avatars
if not exist "static\uploads\covers\" mkdir static\uploads\covers
echo Directories created!
echo.

REM Initialize database
echo Initializing database...
python manage.py initdb
echo.

REM Seed data
echo Seeding sample data...
python manage.py seed
echo.

echo ====================================
echo Setup complete!
echo ====================================
echo.
echo To start the application:
echo 1. Activate venv: venv\Scripts\activate
echo 2. Run: python run.py
echo 3. Open: http://127.0.0.1:5000
echo.
echo Login credentials:
echo   Admin: admin / admin123
echo   Staff: staff / staff123
echo.
pause
