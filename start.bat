@echo off
REM Industry Classification Tool - Quick Start Script (Windows)

echo ================================================================
echo          Industry Classification Tool - Quick Start             
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python is installed

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X pip is not installed. Please install pip.
    pause
    exit /b 1
)

echo [OK] pip is installed

REM Install requirements
echo.
echo Installing required packages...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo X Failed to install packages
    pause
    exit /b 1
)

echo [OK] Packages installed successfully

REM Check for API key
echo.
if "%GEMINI_API_KEY%"=="" (
    echo [!] GEMINI_API_KEY environment variable is not set
    echo.
    echo Please set your Gemini API key:
    echo   set GEMINI_API_KEY=your-api-key-here
    echo.
    echo Or you can enter it in the UI after launching.
    echo.
) else (
    echo [OK] GEMINI_API_KEY is set
)

REM Offer to launch UI
echo.
echo ================================================================
echo Setup complete! Choose an option:
echo ================================================================
echo.
echo   1) Launch Streamlit UI (recommended)
echo   2) Run example script
echo   3) Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Launching Streamlit UI...
    streamlit run ui.py
) else if "%choice%"=="2" (
    echo.
    echo Running example script...
    python example.py
) else if "%choice%"=="3" (
    echo.
    echo Goodbye!
) else (
    echo.
    echo X Invalid choice
)

pause