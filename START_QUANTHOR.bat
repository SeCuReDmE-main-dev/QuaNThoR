@echo off
setlocal
title QuaNThoR - Container Launch
color 0B

cd /d "%~dp0"

where docker >nul 2>&1
if errorlevel 1 (
    echo Docker Desktop is required to run QuaNThoR in the container.
    echo Install Docker Desktop, then run this script again.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   QuaNThoR container startup
echo   Mizar runs inside Docker, not on the host machine.
echo ========================================================
echo.
if "%QUANTHOR_HOST_PORT%"=="" (
    set "QUANTHOR_HOST_PORT=5050"
)
echo Open http://localhost:%QUANTHOR_HOST_PORT% after the container starts.
echo Press Ctrl+C to stop the container.
echo.

docker compose up --build
set "EXIT_CODE=%errorlevel%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo QuaNThoR failed to start. Check the Docker logs above.
    pause
)

exit /b %EXIT_CODE%
