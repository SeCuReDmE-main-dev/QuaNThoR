@echo off
setlocal
title QuaNThoR - Container Installer
color 0A

cd /d "%~dp0"

where docker >nul 2>&1
if errorlevel 1 (
    echo Docker Desktop is required to build the QuaNThoR container.
    echo Install Docker Desktop, then rerun this installer.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo    QuaNThoR container installer
echo    This prepares the Docker image that includes Mizar and Python.
echo ========================================================================
echo.
echo Building the image may take a few minutes the first time.
echo Default host port: 5050
echo.

docker compose build
set "EXIT_CODE=%errorlevel%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Container build failed. Check the Docker output above.
    pause
    exit /b %EXIT_CODE%
)

echo.
echo Build complete.
echo Run START_QUANTHOR.bat to start the container and open the app.
echo.
pause
exit /b 0
