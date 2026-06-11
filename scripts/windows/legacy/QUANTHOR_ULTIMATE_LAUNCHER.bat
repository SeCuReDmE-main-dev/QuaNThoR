@echo off
setlocal
title QuaNThoR Ultimate Launcher
color 0F

cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                  QuaNThoR container launcher and verifier                   ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo This launcher now delegates to the Docker-based runtime so Mizar stays
echo inside the container.
echo.

call "%~dp0START_QUANTHOR.bat"
set "EXIT_CODE=%errorlevel%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo The container launcher reported a failure.
    pause
)

exit /b %EXIT_CODE%
