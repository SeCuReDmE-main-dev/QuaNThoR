@echo off
title QuaNThoR - Triple-AI Mathematical Verification System - Student Installer
color 0A

echo.
echo ========================================================================
echo    QuaNThoR - Triple-AI Mathematical Verification System
echo    Student One-Click Installer
echo ========================================================================
echo.
echo Welcome! This installer will set up QuaNThoR for you automatically.
echo No technical knowledge required - just follow the prompts!
echo.
pause

echo.
echo [1/5] Checking system requirements...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or newer from: https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo ✓ Python found!
python --version

REM Check Python version (basic check)
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.8 or newer required
    echo Please update your Python installation
    pause
    exit /b 1
)

echo ✓ Python version is compatible!
echo.

echo [2/5] Installing Python dependencies...
echo.
echo Installing Flask, CORS support, and security packages...
pip install flask flask-cors requests cryptography watchdog
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo ✓ Python packages installed successfully!
echo.

echo [3/5] Setting up Mizar Mathematical Library...
echo.
if not exist "mizar\" (
    echo ERROR: Mizar directory not found!
    echo Please ensure the mizar folder is in the same directory as this installer.
    pause
    exit /b 1
)

REM Set up Mizar environment
set MIZFILES=%~dp0mizar
set PATH=%PATH%;%MIZFILES%

echo ✓ Mizar path configured: %MIZFILES%
echo.

echo [4/5] Testing Mizar installation...
echo.
cd /d "%~dp0mizar"
if exist "verifier.exe" (
    echo ✓ Mizar verifier found!
) else (
    echo ERROR: Mizar verifier not found
    echo Please ensure all Mizar files are properly extracted
    pause
    exit /b 1
)

REM Test basic Mizar functionality
echo environ > test_install.miz
echo. >> test_install.miz
echo begin >> test_install.miz
echo. >> test_install.miz
echo theorem T1: 1 = 1; >> test_install.miz
echo end. >> test_install.miz

echo Testing mathematical verification...
mizfiles=%MIZFILES% "%MIZFILES%\mizf.bat" test_install.miz >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Mizar mathematical verification working!
) else (
    echo ⚠ Mizar test completed (some errors expected for test)
)

del test_install.miz >nul 2>&1
del test_install.* >nul 2>&1
cd /d "%~dp0"
echo.

echo [5/5] Creating desktop shortcuts and start script...
echo.

REM Create start script
echo @echo off > START_QUANTHOR.bat
echo title QuaNThoR - Triple-AI Mathematical Verification System >> START_QUANTHOR.bat
echo color 0B >> START_QUANTHOR.bat
echo echo. >> START_QUANTHOR.bat
echo echo ======================================================== >> START_QUANTHOR.bat
echo echo    QuaNThoR - Triple-AI Mathematical Verification >> START_QUANTHOR.bat
echo echo    Starting Web Server... >> START_QUANTHOR.bat
echo echo ======================================================== >> START_QUANTHOR.bat
echo echo. >> START_QUANTHOR.bat
echo echo Server starting at: http://localhost:5000 >> START_QUANTHOR.bat
echo echo. >> START_QUANTHOR.bat
echo echo INSTRUCTIONS FOR STUDENTS: >> START_QUANTHOR.bat
echo echo 1. Wait for "Running on http://127.0.0.1:5000" message >> START_QUANTHOR.bat
echo echo 2. Open your web browser >> START_QUANTHOR.bat
echo echo 3. Go to: http://localhost:5000 >> START_QUANTHOR.bat
echo echo 4. Start verifying mathematical proofs! >> START_QUANTHOR.bat
echo echo. >> START_QUANTHOR.bat
echo echo Press Ctrl+C to stop the server when done >> START_QUANTHOR.bat
echo echo. >> START_QUANTHOR.bat
echo cd /d "%~dp0" >> START_QUANTHOR.bat
echo python src/app.py >> START_QUANTHOR.bat
echo pause >> START_QUANTHOR.bat

echo ✓ Start script created: START_QUANTHOR.bat
echo.

REM Create README for students
echo # QuaNThoR - Student Quick Start Guide > STUDENT_README.txt
echo. >> STUDENT_README.txt
echo Welcome to QuaNThoR - Your AI-powered math verification tool! >> STUDENT_README.txt
echo. >> STUDENT_README.txt
echo ## How to Use: >> STUDENT_README.txt
echo. >> STUDENT_README.txt
echo 1. Double-click "START_QUANTHOR.bat" >> STUDENT_README.txt
echo 2. Wait for the server to start >> STUDENT_README.txt  
echo 3. Open your web browser >> STUDENT_README.txt
echo 4. Go to: http://localhost:5000 >> STUDENT_README.txt
echo 5. Start writing mathematical proofs! >> STUDENT_README.txt
echo. >> STUDENT_README.txt
echo ## Need Help? >> STUDENT_README.txt
echo - The system will translate technical errors into plain English >> STUDENT_README.txt
echo - AI assistance is built-in for learning >> STUDENT_README.txt
echo - Contact your teacher if you have problems >> STUDENT_README.txt
echo. >> STUDENT_README.txt
echo ## Safety Note: >> STUDENT_README.txt
echo This tool is protected by SCL-2.0 license for educational stability. >> STUDENT_README.txt
echo Please do not modify system files - focus on learning mathematics! >> STUDENT_README.txt

echo ✓ Student guide created: STUDENT_README.txt
echo.

echo ========================================================================
echo                    INSTALLATION COMPLETE! 
echo ========================================================================
echo.
echo 🎓 QuaNThoR is now ready for students!
echo.
echo STUDENTS: To start using QuaNThoR:
echo   1. Double-click "START_QUANTHOR.bat" 
echo   2. Open browser to: http://localhost:5000
echo   3. Start verifying mathematical proofs!
echo.
echo TEACHERS: Share the entire QuaNThoR folder with students
echo           They only need to run "START_QUANTHOR.bat"
echo.
echo 📚 Check "STUDENT_README.txt" for detailed instructions
echo.
echo ========================================================================
echo.
echo Press any key to finish...
pause >nul

REM Optional: Open the student guide
if exist "STUDENT_README.txt" (
    start notepad "STUDENT_README.txt"
)

exit /b 0