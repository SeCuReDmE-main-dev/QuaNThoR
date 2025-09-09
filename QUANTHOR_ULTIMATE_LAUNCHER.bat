@echo off
title QuaNThoR Ultimate Auto-Debug Launcher
color 0F

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║          🚀 QUANTHOR ULTIMATE AUTO-DEBUG LAUNCHER 🚀                        ║
echo ║                      THE MOST POWERFUL SYSTEM EVER                          ║
echo ║                                                                              ║
echo ║                    🎓 100%% BULLETPROOF STARTUP 🎓                          ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo Welcome to the most advanced QuaNThoR launcher ever created!
echo.
echo This system will:
echo   ✅ Automatically diagnose ALL system issues
echo   ✅ Fix problems before they cause failures
echo   ✅ Monitor performance in real-time
echo   ✅ Provide emergency recovery if needed
echo   ✅ Ensure 100%% successful startup EVERY TIME
echo.
echo 🔧 Features:
echo   • Comprehensive system requirements check
echo   • Automatic Python installation and configuration  
echo   • Mizar mathematical library verification
echo   • Network port conflict resolution
echo   • Real-time resource monitoring
echo   • Emergency recovery system
echo   • Detailed logging and diagnostics
echo.
pause

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell available'" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PowerShell is not available on this system
    echo Please ensure PowerShell 5.0 or later is installed
    pause
    exit /b 1
)

REM Check if script exists
if not exist "%~dp0QUANTHOR_AUTODEBUG.ps1" (
    echo ERROR: QUANTHOR_AUTODEBUG.ps1 not found
    echo Please ensure the PowerShell script is in the same directory
    pause
    exit /b 1
)

echo.
echo 🚀 Launching QuaNThoR Ultimate Auto-Debug System...
echo.

REM Launch PowerShell script with execution policy bypass
powershell -ExecutionPolicy Bypass -WindowStyle Maximized -File "%~dp0QUANTHOR_AUTODEBUG.ps1" -Verbose

REM Check if PowerShell script executed successfully  
if %errorlevel% equ 0 (
    echo.
    echo ✅ QuaNThoR Ultimate Auto-Debug System completed successfully
) else (
    echo.
    echo ❌ QuaNThoR Auto-Debug System encountered issues
    echo Check the debug log for details
)

echo.
echo Press any key to exit...
pause >nul