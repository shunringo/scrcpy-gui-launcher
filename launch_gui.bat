@echo off
echo ============================================
echo  scrcpy GUI Launcher - Setup and Launch
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo Please install from https://www.python.org/downloads/
    pause
    exit /b 1
)

python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Installing PyQt5...
    python -m pip install PyQt5
    if errorlevel 1 (
        echo [ERROR] Failed to install PyQt5.
        pause
        exit /b 1
    )
)

echo Launching scrcpy GUI Launcher...
python "%~dp0scrcpy_launcher.py"
